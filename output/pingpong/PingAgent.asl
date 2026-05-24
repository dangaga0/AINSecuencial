count(0).
!start.

/* Plan de inicio: inicia el envío */
+!start : true <- !send_ping.

/* Plan para enviar ping si el contador es menor a 3 */
+!send_ping : count(C) & C < 3 <- 
    .send(PongAgent, ping).

/* Plan para recibir pong: actualizar contador y reenviar si es necesario */
/* Corrección: El trigger correcto para recibir mensajes es +!m.(A, B) */
+!m.(PongAgent, pong) : count(C) & C < 3 <- 
    C2 is C + 1;
    -count(C);
    assertz(count(C2));
    !send_ping.

/* Plan de finalización */
/* Corrección: trigger +!m. */
+!m.(PongAgent, pong) : count(3) <- 
    .print("Ciclo completado: 3 Pings enviados").

/* Planes de contingencia */
+!send_ping : true <- .print("Fallo en send_ping").
+!m.(PongAgent, pong) : true <- .print("Fallo al recibir pong").