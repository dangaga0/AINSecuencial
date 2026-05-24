@initial_beliefs.
!start.

+!start : true
<- 
    +val_1(0),
    +val_2(1),
    +sequence([0, 1]),
    !process.

+!process : val_1(V1) & val_2(V2) & sequence(Seq)
<- 
    Next is V1 + V2,
    +!next_step(V1, V2, Next, Seq).

+!next_step(Prev, Curr, N, Seq) : N =< 40
<- 
    NewSeq is Seq ++ [N],
    -val_1(Prev), +val_1(Curr),
    -val_2(Curr), +val_2(N),
    -sequence(Seq), +sequence(NewSeq),
    !process.

+!next_step(_, _, N, Seq)
<- 
    .print("Serie Fibonacci: "),
    .print(Seq),
    .print(" Final number: ", N),
    .halt.