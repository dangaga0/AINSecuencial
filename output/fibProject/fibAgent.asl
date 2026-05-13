% Archivo: fibAgent.asl

% Plan de inicio automático al arrancar el agente
% Se dispara automáticamente cuando el agente se inicializa
+!init : true
<- .print("Iniciando cálculo de Fibonacci hasta 40");
   !fib(0, 1).

% Regla recursiva para generar la serie
% Contexto: A debe ser menor o igual a 40 Y Next debe calcularse como A + B
+!fib(A, B) : A =< 40 & Next is A + B
<- .print(A);
   !fib(B, Next).

% Caso base (Plan de contingencia)
% Se ejecuta cuando la condición A =< 40 deja de cumplirse (A > 40)
+!fib(_, _)
<- .print("--- Fin de la serie ---").
