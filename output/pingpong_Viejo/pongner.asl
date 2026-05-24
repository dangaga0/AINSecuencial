!start.

% Bucle de espera para mantener al agente vivo y receptivo
+!start : true <- .wait(100). !start.

% Plan de respuesta: al recibir Ping, envía Pong
+ping[source(pinger)] : true <- 
    .send(pinger, tell, pong);
    .println("Pongner envía Pong").