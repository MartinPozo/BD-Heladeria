SET search_path TO public;

DROP TABLE IF EXISTS detalle_transaccion, transaccion, falla, contrato, turno, horario, empleado, caja, producto, maquina, sucursal, cliente CASCADE;

CREATE TABLE sucursal (
  id_sucursal serial PRIMARY KEY,
  ciudad varchar,
  direccion varchar,
  numero_empleados int,
  numero_ventas int
);

CREATE TABLE empleado (
  id_empleado serial PRIMARY KEY,
  rut varchar,
  nombre varchar,
  apellido varchar,
  id_sucursal int REFERENCES sucursal(id_sucursal)
);

CREATE TABLE contrato (
  id_contrato serial PRIMARY KEY,
  id_empleado int UNIQUE REFERENCES empleado(id_empleado),
  fecha_inicio date,
  fecha_termino date,
  es_indefinido boolean,
  contador_fallas int,
  cargo varchar
);

CREATE TABLE horario (
  id_asistencia serial PRIMARY KEY,
  id_empleado int REFERENCES empleado(id_empleado),
  dia_semana varchar,
  hora_entrada_estimada time,
  hora_salida_estimada time
);

CREATE TABLE turno (
  id_turno serial PRIMARY KEY,
  id_empleado int REFERENCES empleado(id_empleado),
  fecha date,
  hora_entrada_real time,
  hora_salida_real time
);

CREATE TABLE falla (
  id_falla serial PRIMARY KEY,
  id_contrato int REFERENCES contrato(id_contrato),
  gravedad int,
  fecha date,
  detalle varchar
);

CREATE TABLE cliente (
  id_cliente serial PRIMARY KEY,
  rut varchar,
  nombre varchar,
  apellido varchar,
  correo varchar,
  sexo char
);

CREATE TABLE maquina (
  id_maquina serial PRIMARY KEY,
  id_sucursal int REFERENCES sucursal(id_sucursal),
  fecha_ultima_limpieza timestamp,
  en_uso boolean,
  consumo decimal,
  sabor_actual varchar
);

CREATE TABLE producto (
  id_producto serial PRIMARY KEY,
  nombre varchar,
  stock int,
  es_vegano boolean,
  id_maquina int REFERENCES maquina(id_maquina)
);

CREATE TABLE caja (
  id_caja serial PRIMARY KEY,
  id_sucursal int REFERENCES sucursal(id_sucursal),
  numero_caja int,
  estado boolean,
  monto_apertura decimal,
  id_empleado_responsable int REFERENCES empleado(id_empleado)
);

CREATE TABLE transaccion (
  id_transaccion serial PRIMARY KEY,
  id_caja int REFERENCES caja (id_caja),
  id_empleado int REFERENCES empleado (id_empleado),
  id_cliente int REFERENCES cliente (id_cliente),
  monto_total decimal,
  fecha_hora timestamp
);

CREATE TABLE detalle_transaccion (
  id_detalle serial PRIMARY KEY,
  id_transaccion int REFERENCES transaccion (id_transaccion),
  id_producto int REFERENCES producto (id_producto),
  cantidad int
);
