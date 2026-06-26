CREATE TABLE dimension_fecha (
	id_dimension_fecha SERIAL PRIMARY key,
	fecha DATE,
	dia VARCHAR,
	mes VARCHAR,
	ano VARCHAR
);

CREATE TABLE dimension_hora (
	id_dimension_hora SERIAL PRIMARY key,
	hora TIME,
	rango_horario VARCHAR
);

CREATE TABLE dimension_sucursal (
	id_dimension_sucursal SERIAL PRIMARY key,
	ciudad VARCHAR,
	num_empleados INT
);
CREATE TABLE dimension_empleado (
	id_dimension_empleado SERIAL PRIMARY key,
	nombre VARCHAR,
	apellido VARCHAR,
	cargo VARCHAR,
	rut INT
);
CREATE TABLE dimension_caja (
	id_dimension_caja SERIAL PRIMARY key,
	numero INT
);	
CREATE TABLE dimension_cliente (
	id_dimension_cliente SERIAL PRIMARY key,
	rut INT,
	nombre VARCHAR,
	apellido VARCHAR,
	sexo CHAR
);
CREATE TABLE dimension_producto (
	id_dimension_producto SERIAL PRIMARY key,
	nombre VARCHAR,
	es_vegano BOOL
);


CREATE TABLE hecho_venta (
    id_hecho_venta SERIAL PRIMARY KEY,
    id_dimension_fecha INT REFERENCES dimension_fecha(id_dimension_fecha),
    id_dimension_hora INT REFERENCES dimension_hora(id_dimension_hora),
    id_dimension_sucursal INT REFERENCES dimension_sucursal(id_dimension_sucursal),
    id_dimension_empleado INT REFERENCES dimension_empleado(id_dimension_empleado),
	id_dimension_caja INT REFERENCES dimension_caja(id_dimension_caja),
    id_dimension_cliente INT REFERENCES dimension_cliente(id_dimension_cliente),
    id_dimension_producto INT REFERENCES dimension_producto(id_dimension_producto),
    trasaccion_id INT NOT null,
    monto INT NOT null
);

CREATE TABLE hecho_suministro (
    id_hecho_suministro SERIAL PRIMARY KEY,
    id_dimension_fecha INT REFERENCES dimension_fecha(id_dimension_fecha),
    id_dimension_sucursal INT REFERENCES dimension_sucursal(id_dimension_sucursal),
    id_dimension_producto INT REFERENCES dimension_producto(id_dimension_producto),
    lote_id INT NOT NULL,
    cantidad_suministrada INT NOT NULL,
    costo_total INT NOT NULL
);

CREATE TABLE hecho_empleado_diario (
    id_hecho_gestion_empleado SERIAL PRIMARY KEY,
	id_dimension_empleado INT REFERENCES dimension_empleado(id_dimension_empleado),
    id_dimension_fecha INT REFERENCES dimension_fecha(id_dimension_fecha),
    id_dimension_sucursal INT REFERENCES dimension_sucursal(id_dimension_sucursal),
    horas_trabajadas DECIMAL NOT null,
    horas_extras DECIMAL NOT null,
    fallas INT DEFAULT 0
);
