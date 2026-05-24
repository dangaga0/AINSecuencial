/* 1. Creencias / Estado Inicial */
/* Iniciamos el objetivo al cargar el agente */
!start.

/* 2. Planes */

/* Plan de inicio: Inicia el proceso de cálculo */
+!start : true <-
    .print("=== Iniciando Generación de Fibonacci ===");
    /* Llamada interna con: (TerminoActual, ValorActual, SiguienteValor)
       Empezamos en 1, con valor 0, y el siguiente es 1 */
    !calculate(1, 0, 1).

/* Plan recursivo/iterativo: Calcula el siguiente término */
+!calculate(Count, Current, Next) : Count <= 40 <-
    /* Imprime el valor del Fibonacci actual */
    .print("Fib(" + Count + ") = " + Current);
    
    /* Calculamos la suma de los dos anteriores (Current + Next) */
    Sum is Current + Next.
    
    /* Incrementamos el contador para la próxima iteración */
    NewCount is Count + 1.
    
    /* Llamada interna recursiva: el 'Next' actual pasa a ser el 'Current' */
    !calculate(NewCount, Next, Sum).

/* Plan de terminación: Se activa cuando el contador supera 40 */
+!calculate(Count, _, _) : Count > 40 <-
    .print("\n=== Serie finalizada correctamente ===").

/* Plan de contingencia: Manejo de errores genérico */
+!_ : true <-
    .print("Error: Objetivo no manejado o ejecutado incorrectamente").