!start.

+!start/0 : true <- .print("Ping: Envía Ping");
                    .send(pong, ping, "Ping");

+!start/0/1 : true <- .print("Error: start");
                         .halt.

@reactive
+msg(pong, "Pong", S) <- .print("Ping: Recibe Pong de " + S);
                             .halt.