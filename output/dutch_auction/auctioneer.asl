/* Dutch Auctioneer */
bel(current_price(100)).
bel(min_price(20)).
bel(active(true)).

/* Iniciamos la subasta */
bel(!start).

/* Planes de contingencia estrictos por funtor */
+!start(X) : true <- .print("Error start: ", X).
+!broadcast(P) : true <- .print("Error broadcast: ", P).
+!wait_loop(P) : true <- .print("Error wait_loop: ", P).
+!check_reduce(P) : true <- .print("Error check_reduce: ", P).
+!buy(Agent) : true <- .print("Error buy: ", Agent).
+!announce_sale(W, Price) : true <- .print("Error announce_sale: ", W, Price).
+!terminate(X) : true <- .print("Error terminate: ", X).

% --- Lógica del Subastador ---

% Iniciar ciclo
+!start : true <- 
    ?current_price(P),
    !broadcast(P).

% Anunciar precio y guardar
+!broadcast(P) : active(true) & P > min_price <-
    assert(current_price(P)),
    !send(bidder1, price(P)),
    !send(bidder2, price(P)),
    !wait_loop(P).

% Bucle de espera
+!wait_loop(P) : active(true) & P > min_price <-
    .sleep(1000),
    !check_reduce(P).

% Reducir precio si nadie compró
+!check_reduce(P) : active(true) & P > min_price <-
    New is P - 10,
    !broadcast(New).

% Precio mínimo sin compradores
+!check_reduce(P) : active(true) & P =< min_price <-
    !announce_sale("none", P),
    !terminate.

% Alguien compró
+!buy(Agent) : active(true) <-
    ?current_price(P),
    !announce_sale(Agent, P),
    !terminate.

% Notificar ganadores
+!announce_sale(Winner, Price) : active(true) <-
    !send(bidder1, result(Winner, Price)),
    !send(bidder2, result(Winner, Price)),
    assert(active(false)).

% Detener subasta
+!terminate : true <-
    .print("Auction ended.").