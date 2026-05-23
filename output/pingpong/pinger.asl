!start.

% Plan de inicio: envía el primer Ping y termina su intención de inicio
+!start : true <- 
    .send(pongner, tell, ping);
    .println("Pinger envía Ping");
    .halt().

% Plan de respuesta: al recibir Pong, envía Ping nuevamente
+pong[source(pongner)] : true <- 
    .send(pongner, tell, ping);
    .println("Pinger recibió Pong, envía Ping").