import psycopg2
from datetime import datetime

def ConectarBaseTransaccional():
    return psycopg2.connect(
        dbname = "Heladeria",
        user = "postgres",
        password = "13456",
        host = "localhost",
        port = "5432"
    )

def Ejecutar(sql, Funcion, parametros=None, retornar_datos=False):
    conn = Funcion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, parametros)
        if retornar_datos:
            resultados = cursor.fetchall()
            return resultados
        else:
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def CargarDatosSinteticos():
    sql_script = """
    SET search_path TO public;

    TRUNCATE TABLE 
        detalle_transaccion, transaccion, detalle_caja, caja, 
        lote_producto, producto, maquina, falla, contrato, 
        turno, horario, empleado, sucursal, cliente 
    RESTART IDENTITY CASCADE;

    -- =============================================
    -- DATOS BASE (sin fecha crítica)
    -- =============================================

    INSERT INTO sucursal (ciudad, direccion, numero_empleados, numero_ventas) VALUES
    ('Puerto Montt', 'Costanera 123', 0, 0),
    ('Puerto Varas', 'Walker Martínez 450', 0, 0),
    ('Castro', 'Plaza de Armas 10', 0, 0);

    -- 5 máquinas por sucursal = 15 total
    INSERT INTO maquina (id_sucursal, fecha_ultima_limpieza, en_uso, consumo, sabor_actual)
    SELECT 
        (i % 3) + 1,
        NOW() - (random() * INTERVAL '15 days'),
        true,
        (random() * 50 + 100)::decimal(10,2), 
        (ARRAY['Frutilla', 'Chocolate', 'Vainilla', 'Lúcuma', 'Manjar'])[floor(random() * 5) + 1]
    FROM generate_series(1, 15) AS i;

    INSERT INTO producto (precio, nombre, es_vegano, receta)
    SELECT 
        (ARRAY[1500, 2000, 2500, 3000])[floor(random() * 4) + 1],
        (ARRAY['Helado Chocolate Suizo', 'Helado Lúcuma Nuez', 'Helado Frambuesa',
               'Helado Vainilla Bourbon', 'Helado Manjar Chips', 'Helado Pistacho',
               'Helado Frutos Rojos', 'Helado Pasas al Ron', 'Helado Piña'])[floor(random() * 9) + 1],
        (random() > 0.8),
        'Receta estándar de simulación'
    FROM generate_series(1, 30) AS i;

    -- 4 empleados por sucursal = 12 total (múltiplo de 3 para distribuir bien)
    INSERT INTO empleado (rut, nombre, apellido, id_sucursal)
    SELECT 
        (floor(random() * 5 + 15))::text || '.' ||
        floor(random()*899+100)::text || '.' ||
        floor(random()*899+100)::text || '-' ||
        floor(random()*10)::text,
        (ARRAY['Quidel','Andy','Bastián','Catalina','Diego',
               'Elena','Felipe','Gloria','Hugo','Isabel',
               'Javiera','Rodrigo'])[floor(random() * 12) + 1],
        (ARRAY['Barriga','Briones','Andrade','Barría','Cárdenas',
               'Díaz','Espinoza','Flores','Galdames','Henríquez',
               'Ibáñez','Jara'])[floor(random() * 12) + 1],
        (i % 3) + 1
    FROM generate_series(1, 12) AS i;

    -- Contrato para cada empleado
    INSERT INTO contrato (id_empleado, fecha_inicio, es_indefinido, cargo)
    SELECT id_empleado, '2024-01-01'::date, true, 'Vendedor/Operario'
    FROM empleado;

    -- Horario laboral (Lunes a Viernes, 09:00–18:00)
    INSERT INTO horario (id_empleado, dia_semana, hora_entrada_estimada, hora_salida_estimada)
    SELECT 
        e.id_empleado,
        dia,
        '09:00:00'::time,
        '18:00:00'::time
    FROM empleado e
    CROSS JOIN unnest(ARRAY['Lunes','Martes','Miércoles','Jueves','Viernes']) AS dia;

    -- 1 caja por sucursal (3 en total)
    INSERT INTO caja (id_sucursal, numero_caja, estado)
    VALUES (1, 1, true), (2, 1, true), (3, 1, true);

    -- 500 clientes
    INSERT INTO cliente (rut, nombre, apellido, correo, sexo)
    SELECT 
        (floor(random() * 10 + 12))::text || '.' ||
        floor(random()*899+100)::text || '.' ||
        floor(random()*899+100)::text || '-' ||
        (ARRAY['0','1','2','3','4','5','6','7','8','9','K'])[floor(random() * 11) + 1],
        nom, ape,
        LOWER(nom || '.' || ape || i || '@gmail.com'),
        sex
    FROM (
        SELECT 
            i,
            (ARRAY['M','F'])[floor(random() * 2) + 1] AS sex,
            (ARRAY['Juan','María','Carlos','Ana','Pedro','Laura','Luis','Sofía',
                   'Diego','Camila','José','Valentina','Andrés','Francisca','Javier','Antonia']
            )[floor(random() * 16) + 1] AS nom,
            (ARRAY['González','Muñoz','Rojas','Díaz','Pérez','Soto','Contreras','Silva',
                   'Martínez','Sepúlveda','Morales','Rodríguez','López','Fuentes','Vergara','Ony']
            )[floor(random() * 16) + 1] AS ape
        FROM generate_series(1, 500) AS i
    ) subconsulta;

    -- =============================================
    -- DATOS DE AYER (los que carga el ETL)
    -- =============================================

    -- Lotes elaborados AYER → ETL hecho_suministro
    INSERT INTO lote_producto (coste_lote, stock, fecha_elaboracion, fecha_vencimiento, fecha_salida_sala, id_maquina, id_producto)
    SELECT
        floor(random() * 5000 + 2000)::int,
        floor(random() * 100 + 20)::int,
        CURRENT_DATE - 1,                  -- ← AYER
        CURRENT_DATE + 30,
        CURRENT_DATE - 1,
        (floor(random() * 15) + 1),
        (floor(random() * 30) + 1)
    FROM generate_series(1, 50) AS i;

    -- Detalle de caja de AYER
    INSERT INTO detalle_caja (monto_apertura, monto_cierre, id_empleado_responsable, fecha, transacciones_del_dia, id_caja)
    SELECT 50000.00, NULL, id_empleado, CURRENT_DATE - 1, 0, id_empleado  -- ← AYER
    FROM empleado WHERE id_empleado <= 3;

    -- Turnos de AYER para todos los empleados → ETL hecho_empleado_diario
    INSERT INTO turno (id_empleado, fecha, hora_entrada_real, hora_entrada_colacion, hora_salida_colacion, hora_salida_real, horas_extras)
    SELECT
        id_empleado,
        CURRENT_DATE - 1,                                                           -- ← AYER
        '09:00:00'::time + (floor(random() * 20) || ' minutes')::interval,
        '13:00:00'::time,
        '14:00:00'::time,
        '18:00:00'::time + (floor(random() * 90) || ' minutes')::interval,
        CASE WHEN random() < 0.3 THEN 1 ELSE 0 END
    FROM empleado;

    -- Fallas de AYER (~30% de empleados) → ETL hecho_empleado_diario
    INSERT INTO falla (id_contrato, gravedad, fecha, detalle)
    SELECT
        c.id_contrato,
        floor(random() * 5)::int,
        CURRENT_DATE - 1,                  -- ← AYER
        (ARRAY['Llegada tarde', 'Incumplimiento de protocolo', 'Ausencia no justificada',
               'Uso indebido de equipo', 'Trato inadecuado a cliente'])[floor(random() * 5) + 1]
    FROM contrato c
    WHERE random() < 0.3;

    -- 2500 transacciones de AYER entre 09:00 y 21:00 → ETL hecho_venta
    INSERT INTO transaccion (id_caja, id_empleado, id_cliente, metodo_pago, monto_total, fecha_hora)
    SELECT 
        (floor(random() * 3) + 1),
        (floor(random() * 12) + 1),
        (floor(random() * 500) + 1),
        (ARRAY['Efectivo','Débito','Crédito'])[floor(random() * 3) + 1],
        (random() * 10000 + 3000)::decimal(10,2),
        (CURRENT_DATE - 1)::timestamp                -- ← AYER
            + INTERVAL '9 hours'
            + (random() * INTERVAL '12 hours')
    FROM generate_series(1, 2500) AS i;

    -- Detalle por transacción
    INSERT INTO detalle_transaccion (id_transaccion, id_lote_producto, cantidad)
    SELECT 
        i,
        (floor(random() * 50) + 1),
        (floor(random() * 3) + 1)
    FROM generate_series(1, 2500) AS i;

    -- Actualizar contadores de sucursal
    UPDATE sucursal s
    SET numero_empleados = (
        SELECT COUNT(*) FROM empleado e WHERE e.id_sucursal = s.id_sucursal
    );
    """

    try:
        print(f"Cargando datos sintéticos para AYER ({datetime.now().date()} - 1 día)...")
        Ejecutar(sql_script, ConectarBaseTransaccional)
        print("¡Datos de ayer cargados con éxito! Ya puedes ejecutar el scheduler.")
    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")

CargarDatosSinteticos()
