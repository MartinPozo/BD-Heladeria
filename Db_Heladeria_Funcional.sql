SET search_path TO public;

TRUNCATE TABLE detalle_transaccion, transaccion, falla, contrato, turno, horario, empleado, caja, producto, maquina, sucursal, cliente RESTART IDENTITY CASCADE;

INSERT INTO sucursal (ciudad, direccion, numero_empleados, numero_ventas) VALUES
('Puerto Montt', 'Costanera 123', 5, 0),
('Puerto Varas', 'Walker Martínez 450', 5, 0),
('Castro', 'Plaza de Armas 10', 5, 0);


INSERT INTO maquina (id_sucursal, fecha_ultima_limpieza, en_uso, consumo, sabor_actual)
SELECT 
    (i % 3) + 1,
    NOW() - (random() * INTERVAL '15 days'),
    true,
    (random() * 50 + 100)::decimal(10,2), 
    (ARRAY['Congelador Horizontal Ventus', 'Mantecadora Maigas', 'Vitrina Gelatera Boia', 'Batidora Industrial KitchenAid', 'Sistema de Refrigeración Central'])[floor(random() * 5) + 1]
FROM generate_series(1, 15) AS i; 

INSERT INTO producto (nombre, stock, es_vegano, id_maquina)
SELECT 
    (ARRAY['Helado Chocolate Suizo', 'Helado Lúcuma Nuez', 'Helado Frambuesa', 'Helado Vainilla Bourbon', 'Helado Manjar Chips', 'Helado Pistacho', 'Helado Frutos Rojos', 'Helado Pasas al Ron', 'Helado Pina'])[floor(random() * 8) + 1],
    floor(random() * 100 + 20)::int,
    (random() > 0.8), 
    (floor(random() * 15) + 1) 
FROM generate_series(1, 30) AS i;

INSERT INTO empleado (rut, nombre, apellido, id_sucursal)
SELECT 
    (floor(random() * 5 + 15))::text || '.' || floor(random()*899+100)::text || '.' || floor(random()*899+100)::text || '-' || floor(random()*10)::text,
    (ARRAY['Quidel', 'Andy', 'Bastián', 'Catalina', 'Diego', 'Elena', 'Felipe', 'Gloria', 'Hugo', 'Isabel', 'Joaquín', 'Karla'])[floor(random() * 10) + 1],
    (ARRAY['Barriga', 'Briones', 'Andrade', 'Barría', 'Cárdenas', 'Díaz', 'Espinoza', 'Flores', 'Galdames', 'Henríquez', 'Iturra', 'Jara'])[floor(random() * 10) + 1],
    (i % 3) + 1
FROM generate_series(1, 10) AS i;

INSERT INTO contrato (id_empleado, fecha_inicio, es_indefinido, cargo)
SELECT id_empleado, '2024-01-01'::date, true, 'Vendedor/Operario' FROM empleado;

INSERT INTO caja (id_sucursal, numero_caja, estado, monto_apertura, id_empleado_responsable)
SELECT id_sucursal, 1, true, 50000.00, id_empleado FROM empleado WHERE id_empleado <= 3;

INSERT INTO cliente (rut, nombre, apellido, correo, sexo)
SELECT 
    '1' || floor(random()*9)::text || '.000.000-K',
    'Cliente_' || i, 'Apellido_' || i, 'test' || i || '@mail.com', 'M'
FROM generate_series(1, 15000) AS i;

INSERT INTO transaccion (id_caja, id_empleado, id_cliente, metodo_pago, monto_total, fecha_hora)
SELECT 
    (floor(random() * 3) + 1),
    (floor(random() * 10) + 1),
    (floor(random() * 15000) + 1),
    (ARRAY['Efectivo', 'Débito', 'Crédito'])[floor(random() * 3) + 1],
    (random() * 10000 + 3000)::decimal(10,2),
    '2022-01-01 01:00:00'::timestamp + (i * INTERVAL '5 minutes')
FROM generate_series(1, 400000) as i;

INSERT INTO detalle_transaccion (id_transaccion, id_producto, cantidad)
SELECT 
    i, 
    (floor(random() * 30) + 1),
    (floor(random() * 3) + 1)
FROM generate_series(1, 400000) AS i;
