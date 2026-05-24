/* Plan de respuesta */
/* Corrección: trigger +!m. */
+!m.(PingAgent, ping) : true <- 
    .send(PingAgent, pong).

/* Plan de contingencia */
+!meta(_) : true <- .print("Fallo en plan: ", meta).