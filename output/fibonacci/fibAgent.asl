// Evento inicial: Lanza la serie con los valores iniciales (0, 1)
+!start :- !fib(0, 1).

// Plan de generación: Se activa mientras Y sea menor o igual a 40.
// 1. Imprime el valor actual Y.
// 2. Lanza recursivamente el siguiente estado: !fib(+Y, +X+Y).
//    - El nuevo primer argumento es el Y actual (+Y).
//    - El nuevo segundo argumento es la suma de ambos (+X+Y).
//    - El signo + delante de los términos obliga a evaluar la aritmética.
+!fib(X, Y) : Y <= 40 <- .println(+Y).
                         !fib(+Y, +X+Y).

// Plan de parada: Se activa cuando Y supera 40.
// Imprime mensaje de fin y cancela la intención actual.
+!fib(X, Y) : Y > 40 <- .println("Fin de la serie").
                        -!fib(_,_).