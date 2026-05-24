!iniciar.

// Plan de inicialización
+!iniciar : true <- 
    +precio_actual(100).
    .print("--- INICIO DE LA SUBASTA HOLONDESA ---").
    !ofertar(100).

// Plan para emitir precio si no se ha vendido y el precio es válido
+!ofertar(Precio) : not vendido & Precio >= 0 <- 
    .print("Subastador: Precio actual ", Precio).
    .broadcast(tell, oferta(Precio)).
    !esperar.

// Plan de salida si el precio cae a 0 y nadie compra
+!ofertar(Precio) : not vendido & Precio < 0 <- 
    .print("Subasta finalizada, nadie compró").
    .

// CORRECCIÓN: Detener bucle silenciosamente si se vendió
+!ofertar(Precio) : vendido <- 
    .

// Bucle de espera y bajada de precio
+!esperar : not vendido & precio_actual(Precio) <- 
    .wait(1500).
    NuevoPrecio is Precio - 10.
    +precio_actual(NuevoPrecio). // Actualización crítica para el bucle
    !ofertar(NuevoPrecio).

// Detener espera si se vendió
+!esperar : vendido <- 
    .print("Subastador: Venta concretada").
    .

// Contingencia general
+!ofertar(_) : true <- .print("Error en ofertar").
+!esperar : true <- .print("Error en esperar").

// Sincronizar precio local
+oferta(Precio) : not vendido <- 
    +precio_actual(Precio).

// Recibir compra
+compre(Precio)[source(Agent)] : not vendido & precio_actual(Precio) <- 
    .print("Subastador: VENTADO a ", Agent, " por ", Precio).
    +vendido.