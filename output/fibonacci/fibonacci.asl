% Archivo: fibonacci.asl

% Plan de inicialización
% Se ejecuta una sola vez para arrancar el proceso
+!inicio <- 
    % Imprimimos los dos primeros números manualmente para simplificar la recursión
    .println(0), 
    .println(1),
    % Invocamos el plan recursivo pasando los dos últimos valores calculados:
    !fib(1, 1).

% Plan recursivo para generar el siguiente Fibonacci
% A: valor penúltimo
% B: valor actual (el siguiente a imprimir)
% Condición: solo ejecutar si B es menor o igual a 40
+!fib(A, B) : B <= 40 <- 
    .println(B), 
    % Se llama a sí mismo recursivamente con los nuevos valores:
    % El actual (B) se convierte en penúltimo, y la suma (A+B) en el actual.
    !fib(B, A + B).

% Objetivo inicial para lanzar la ejecución del agente
!inicio.