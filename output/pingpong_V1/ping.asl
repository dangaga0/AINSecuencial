/* Objetivos y Creías */

/* Objetivo de inicio: Al ejecutar el agente, se dispara +!start */
!start.

/* Planes */

/* Plan: Al recibir el objetivo de inicio, envía 'ping' y se para */
+!start : true 
   <- .print("Ping: Iniciando y enviando ping...");
      .send(pong, inform, ping);
      .print("Ping: Ping enviado.");
      .halt().

/* Plan de contingencia: Captura cualquier otro objetivo no definido */
+!goal(X) : true 
   <- .print("Ping: Fallo en objetivo ", X).
