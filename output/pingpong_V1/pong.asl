/* Objetivos y Creías */

/* Planes */

/* Plan: Escucha mensajes del tipo inform con contenido 'ping' */
/* El evento +!inform(ping) se genera automáticamente al recibir el mensaje */
+!inform(ping) : true 
   <- .print("Pong: Recibido ping, respondiendo...");
      .send(ping, inform, pong);
      .print("Pong: Pong enviado.");
      .halt().

/* Plan de contingencia: Captura cualquier otro objetivo no definido */
+!goal(X) : true 
   <- .print("Pong: Fallo en objetivo ", X).
