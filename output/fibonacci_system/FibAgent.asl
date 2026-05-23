agent FibAgent

/* 
   1. Objetivo Inicial
   Dispara el cálculo comenzando con F(0)=0 y F(1)=1.
*/
+!start_fibonacci(0, 1).

/*
   2. Plan de Inicialización
   Transforma el objetivo de inicio en el primer paso del algoritmo.
*/
+!start_fibonacci(A, B) <- !generate_step(A, B).

/*
   3. Plan Recursivo (Bucle Principal)
   Se ejecuta mientras el número actual (A) sea menor o igual a 40.
*/
+!generate_step(A, B) : A <= 40 <-
    // Imprime el término actual
    .print("Generando: ", A).
    
    // Calcula el siguiente término sumando A + B.
    C := A + B.
    
    // Llama recursivamente para el siguiente paso:
    // El nuevo primer número es el segundo actual (B),
    // y el nuevo segundo número es la suma calculada (C).
    !generate_step(B, C).

/*
   4. Plan de Terminación
   Se ejecuta cuando el número supera el límite de 40.
*/
+!generate_step(A, B) : A > 40 <-
    .print("Serie de Fibonacci generada hasta 40. Último número: ", A).

/*
   5. Plan de Contingencia
   Captura cualquier evento no definido para evitar fallos del sistema.
*/
+!_(_) <- .print("Error: ", _).