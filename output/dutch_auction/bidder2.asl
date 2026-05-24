/* Bidder 2 */
bel(max_val(40)).
bel(listening(true)).

bel(!start).

/* Planes de contingencia estrictos */
+!start(X) : true <- .print("Error start bidder2: ", X).
+!listen(X) : true <- .print("Error listen bidder2: ", X).
+!price(P) : true <- .print("Error price bidder2: ", P).

% Iniciar comportamiento
+!start : true <- !listen.

% Escuchar precio
+!listen : listening(true) <-
    .print("Listening..."),
    .sleep(1000),
    !listen.

% Recibir precio
+!price(P) : listening(true) <-
    ?max_val(V),
    (P =< V : !send(auctioneer, buy(myself)), !print("Bidding at ", P)
              : !print("Price ", P, " too high (max ", V, ")")),
    !listen.

% Ver resultado
+!result(Winner, Price) : true <-
    if Winner == myself then 
        .print("I won! Price: ", Price)
    else 
        .print("I lost. Winner: ", Winner, " | Price: ", Price)
    endif.