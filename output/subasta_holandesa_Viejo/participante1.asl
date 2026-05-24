precio_max(60).

// Extrae el valor máximo (Max) y lo compara
+oferta(Precio) : not vendido & ?precio_max(Max) & (Precio <= Max) <- 
    .print("Participante 1: Acepto el precio ", Precio).
    .send(subastador, tell, compre(Precio)).
    +vendido.

// Si supera el máximo, rechaza
+oferta(Precio) : not vendido & ?precio_max(Max) & (Precio > Max) <- 
    .print("Participante 1: Rechazo oferta de ", Precio).
    .

// Ignorar si ya se vendió
+oferta(Precio) : vendido <- 
    .