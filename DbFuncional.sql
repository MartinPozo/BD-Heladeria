SET search_path TO public;
DROP TABLE IF EXISTS detalle_transaccion, transaccion, falla, contrato, turno, horario, empleado, caja, producto, maquina, sucursal, cliente CASCADE;

CREATE TABLE sucursal (
    id_sucursal SERIAL PRIMARY KEY,
    ciudad VARCHAR NOT NULL,
    direccion VARCHAR NOT NULL,
    numero_empleados INT,
    numero_ventas INT
);

CREATE TABLE empleado (
    id_empleado SERIAL PRIMARY KEY,
    rut VARCHAR NOT NULL,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    id_sucursal INT REFERENCES sucursal(id_sucursal)
);

CREATE TABLE contrato (
    id_contrato SERIAL PRIMARY KEY,
    id_empleado INT UNIQUE REFERENCES empleado(id_empleado),
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE,
    es_indefinido BOOLEAN DEFAULT TRUE,
    contador_fallas INT DEFAULT 0,
    cargo VARCHAR NOT NULL
);

CREATE TABLE horario (
    id_asistencia SERIAL PRIMARY KEY,
    id_empleado INT REFERENCES empleado(id_empleado),
    dia_semana VARCHAR NOT NULL,
    hora_entrada_estimada TIME,
    hora_salida_estimada TIME
);

CREATE TABLE turno (
    id_turno SERIAL PRIMARY KEY,
    id_empleado INT REFERENCES empleado(id_empleado),
    fecha DATE NOT NULL,
    hora_entrada_real TIME,
    hora_entrada_colacion TIME,
    hora_salida_colacion TIME,
    hora_salida_real TIME,
    horas_extras INT DEFAULT 0
);

CREATE TABLE falla (
    id_falla SERIAL PRIMARY KEY,
    id_contrato INT REFERENCES contrato(id_contrato),
    gravedad INT CHECK (gravedad BETWEEN 0 AND 9),
    fecha DATE NOT NULL,
    detalle VARCHAR
);

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    rut VARCHAR,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    correo VARCHAR,
    sexo CHAR(1) -- 'M' o 'F'
);

CREATE TABLE maquina (
    id_maquina SERIAL PRIMARY KEY,
    id_sucursal INT REFERENCES sucursal(id_sucursal),
    fecha_ultima_limpieza TIMESTAMP,
    en_uso BOOLEAN DEFAULT TRUE,
    consumo DECIMAL(10,2),
    sabor_actual VARCHAR
);

CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    precio INT,
    nombre VARCHAR NOT NULL,
    es_vegano BOOLEAN DEFAULT FALSE,
    receta TEXT
);

CREATE TABLE lote_producto (
    id_lote_producto SERIAL PRIMARY KEY,
    coste_lote INT NOT NULL,
    stock INT NOT NULL,
    fecha_elaboracion DATE,
    fecha_vencimiento DATE,
    fecha_salida_sala DATE,
    id_maquina INT REFERENCES maquina(id_maquina),
    id_producto INT REFERENCES producto(id_producto)
);

CREATE TABLE caja (
    id_caja SERIAL PRIMARY KEY,
    id_sucursal INT REFERENCES sucursal(id_sucursal),
    numero_caja INT NOT NULL,
    estado BOOLEAN DEFAULT FALSE,
    monto_apertura DECIMAL(10,2),
    monto_cierre DECIMAL(10,2),
    id_empleado_responsable INT REFERENCES empleado(id_empleado),
    transacciones_del_dia INT DEFAULT 0
);

CREATE TABLE transaccion (
    id_transaccion SERIAL PRIMARY KEY,
    id_caja INT REFERENCES caja(id_caja),
    id_empleado INT REFERENCES empleado(id_empleado),
    id_cliente INT REFERENCES cliente(id_cliente),
    metodo_pago VARCHAR NOT NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalle_transaccion (
    id_detalle SERIAL PRIMARY KEY,
    id_transaccion INT REFERENCES transaccion(id_transaccion),
    id_producto INT REFERENCES producto(id_producto),
    cantidad INT NOT NULL
);