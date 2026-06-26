import time
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

def Ejecutar(sql, Funcion, parametros = None, retornar_datos = False):
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
        (ARRAY['Frutilla', 'Chocolate', 'Vainilla', 'Lúcuma', 'Manjar'])[floor(random() * 5) + 1]
    FROM generate_series(1, 15) AS i; 

    INSERT INTO producto (precio, nombre, es_vegano, receta)
    SELECT 
        (ARRAY[1500, 2000, 2500, 3000])[floor(random() * 4) + 1],
        (ARRAY['Helado Chocolate Suizo', 'Helado Lúcuma Nuez', 'Helado Frambuesa', 'Helado Vainilla Bourbon', 'Helado Manjar Chips', 'Helado Pistacho', 'Helado Frutos Rojos', 'Helado Pasas al Ron', 'Helado Piña'])[floor(random() * 9) + 1],
        (random() > 0.8), 
        'Receta estándar de simulación'
    FROM generate_series(1, 30) AS i;

    INSERT INTO lote_producto (coste_lote, stock, fecha_elaboracion, fecha_vencimiento, id_maquina, id_producto)
    SELECT
        floor(random() * 5000 + 2000)::int,
        floor(random() * 100 + 20)::int,
        f_elab,
        f_elab + INTERVAL '30 days',
        (floor(random() * 15) + 1),
        (floor(random() * 30) + 1)
    FROM (
        SELECT CURRENT_DATE - (floor(random() * 1458) + 2) * INTERVAL '1 day' AS f_elab
        FROM generate_series(1, 50)
    ) AS subconsulta_lote;

    INSERT INTO empleado (rut, nombre, apellido, id_sucursal)
    SELECT 
        (floor(random() * 5 + 15))::text || '.' || floor(random()*899+100)::text || '.' || floor(random()*899+100)::text || '-' || floor(random()*10)::text,
        (ARRAY['Quidel', 'Andy', 'Bastián', 'Catalina', 'Diego', 'Elena', 'Felipe', 'Gloria', 'Hugo', 'Isabel'])[floor(random() * 10) + 1],
        (ARRAY['Barriga', 'Briones', 'Andrade', 'Barría', 'Cárdenas', 'Díaz', 'Espinoza', 'Flores', 'Galdames', 'Henríquez'])[floor(random() * 10) + 1],
        (i % 3) + 1
    FROM generate_series(1, 10) AS i;

    INSERT INTO contrato (id_empleado, fecha_inicio, es_indefinido, cargo)
    SELECT id_empleado, '2024-01-01'::date, true, 'Vendedor/Operario' FROM empleado;

    INSERT INTO caja (id_sucursal, numero_caja, estado)
    SELECT (id_empleado % 3) + 1, 1, true FROM empleado WHERE id_empleado <= 3;

    INSERT INTO detalle_caja (monto_apertura, monto_cierre, id_empleado_responsable, fecha, transacciones_del_dia, id_caja)
    SELECT 50000.00, NULL, id_empleado, CURRENT_DATE - (floor(random() * 1458) + 2) * INTERVAL '1 day', 0, id_empleado FROM empleado WHERE id_empleado <= 3;

    INSERT INTO cliente (rut, nombre, apellido, correo, sexo)
    SELECT 
        (floor(random() * 10 + 12))::text || '.' || floor(random()*899+100)::text || '.' || floor(random()*899+100)::text || '-' || (ARRAY['0','1','2','3','4','5','6','7','8','9','K'])[floor(random() * 11) + 1],
        nom, 
        ape,
        LOWER(nom || '.' || ape || i || '@gmail.com'),
        sex
    FROM (
        SELECT 
            i,
            (ARRAY['M', 'F'])[floor(random() * 2) + 1] as sex,
            (ARRAY['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Luis', 'Sofía', 'Diego', 'Camila', 'José', 'Valentina', 'Andrés', 'Francisca', 'Javier', 'Antonia'])[floor(random() * 16) + 1] as nom,
            (ARRAY['González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras', 'Silva', 'Martínez', 'Sepúlveda', 'Morales', 'Rodríguez', 'López', 'Fuentes', 'Vergara', 'Ony'])[floor(random() * 16) + 1] as ape
        FROM generate_series(1, 500) AS i
    ) subconsulta;

    INSERT INTO transaccion (id_caja, id_empleado, id_cliente, metodo_pago, monto_total, fecha_hora)
    SELECT 
        (floor(random() * 3) + 1),
        (floor(random() * 10) + 1),
        (floor(random() * 500) + 1), 
        (ARRAY['Efectivo', 'Débito', 'Crédito'])[floor(random() * 3) + 1],
        (random() * 10000 + 3000)::decimal(10,2),
        CURRENT_DATE - (random() * 1458 + 2) * INTERVAL '1 day'
    FROM generate_series(1, 2500) as i;

    INSERT INTO detalle_transaccion (id_transaccion, id_lote_producto, cantidad)
    SELECT 
        i, 
        (floor(random() * 50) + 1),
        (floor(random() * 3) + 1)
    FROM generate_series(1, 2500) AS i;
    UPDATE sucursal s
        SET numero_empleados = (
            SELECT COUNT(*) FROM empleado e WHERE e.id_sucursal = s.id_sucursal
        );
    """

    try:
        print("Insertando muestra ligera con nombres reales para la UI...")
        Ejecutar(sql_script, ConectarBaseTransaccional)
        print("¡Muestra de datos realistas creada con éxito!")
    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")

CargarDatosSinteticos()
