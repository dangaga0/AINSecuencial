// Definición del agente Fibonacci

// Objetivo inicial para iniciar la ejecución
!start.

// Plan que dispara el cálculo inicial
+!start :- !generarFib(0, 1, 40).

// Plan Recursivo (Bucle)
// Se ejecuta mientras N <= Max
+!generarFib(N, Sig, Max) :-
    N =< Max,
    Z = N + Sig,                 // CORRECCIÓN: Asignar la suma a una variable Z
    !generarFib(Sig, Z, Max).    // Pasar Z en lugar de la expresión N + Sig

// Plan de Terminación
// Se ejecuta cuando la condición anterior falla (N > Max)
+!generarFib(N, Sig, Max) :-
    N > Max,
    .print("Fin de la serie"),
    !finish.

// Plan para finalizar el agente limpiamente
+!finish :- .println("Fin del agente");