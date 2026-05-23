@reactive
+msg(ping, "Ping", S) <- .print("Pong: Recibe Ping de " + M);
                         .send(S, pong, "Pong");
                         .print("Pong: Envía Pong");
                         .halt.