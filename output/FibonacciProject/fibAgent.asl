+!start :- ~step, +step(1), ~last2, +last2(0), ~last1, +last1(1), !loop.
+!loop : step(C) & C < 28 <- ?last1(L1), ?last2(L2), Next = L1 + L2, NewC = C + 1, .print("Fib(" + NewC + ") = " + Next), ~step, +step(NewC), ~last2, +last2(L1), ~last1, +last1(Next), !loop.
+!loop : step(C) & C >= 28 <- .print("Proceso finalizado en F(28)."), halt.
+!loop(_) <- .print("Error en la ejecución."), halt.