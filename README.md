# ProyectoMC
proyecto de medio ciclo

-- 1. TABLA TICKETS (El recibo general de la apuesta)
CREATE TABLE IF NOT EXISTS tickets (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    monto_total DECIMAL(10, 2),
    ganancia_posible DECIMAL(10, 2),
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 2. TABLA DETALLES (Cada partido dentro del ticket)
CREATE TABLE IF NOT EXISTS detalles_apuesta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_ticket INT,
    id_partido INT,
    seleccion VARCHAR(50),
    cuota_momento DECIMAL(5, 2),
    FOREIGN KEY (id_ticket) REFERENCES tickets(id_ticket),
    FOREIGN KEY (id_partido) REFERENCES partidos(id)
);
***********agregue eso a la base de datos ***********

prueba de no force