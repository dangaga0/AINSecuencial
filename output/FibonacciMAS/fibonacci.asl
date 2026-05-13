%jason

begin <- 
    .print("Serie de Fibonacci hasta 40:").
    .print(0).
    .print(1).
    +generar(40, 0, 1).

+generar(Limite, A, B) : (A + B) <= Limite <- 
    Sig = A + B.
    .print(Sig).
    +generar(Limite, B, Sig).