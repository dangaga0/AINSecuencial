precio_max(70).

+oferta(Precio) : not vendido & ?precio_max(Max) & (Precio <= Max) <- 
    .print("Participante 2: Acepto el precio ", Precio).
    .send(subastador, tell, compre(Precio)).
    +vendido.

+oferta(Precio) : not vendido & ?precio_max(Max) & (Precio > Max) <- 
    .print("Participante 2: Rechazo oferta de ", Precio).
    .

+oferta(Precio) : vendido <- 
    .