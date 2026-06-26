import psycopg2
from datetime import datetime

def ConectarBaseTransaccional():
    return psycopg2.connect(
        dbname="Heladeria",
        user="postgres",
        password="13456",
        host="localhost",
        port="5432"
    )

def ConectarBaseAnalitica():
    return psycopg2.connect(
        dbname="HeladeriaAnalitica",
        user="postgres",
        password="13456",
        host="localhost",
        port="5432"
    )

def limpiar_rut_a_int(rut_str):
    if not rut_str:
        return None
    numeros = ''.join(filter(str.isdigit, str(rut_str)))
    return int(numeros) if numeros else None

def _dim_fecha(cursor, fecha):
    cursor.execute("SELECT id_dimension_fecha FROM dimension_fecha WHERE fecha = %s", (fecha,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_fecha (fecha, dia, mes, ano) VALUES (%s, %s, %s, %s) RETURNING id_dimension_fecha",
        (fecha, str(fecha.day), str(fecha.month), str(fecha.year))
    )
    return cursor.fetchone()[0]

def _dim_hora(cursor, hora):
    cursor.execute("SELECT id_dimension_hora FROM dimension_hora WHERE hora = %s", (hora,))
    res = cursor.fetchone()
    if res:
        return res[0]
    if 6 <= hora.hour < 12:
        rango = "Mañana"
    elif 12 <= hora.hour < 19:
        rango = "Tarde"
    else:
        rango = "Noche"
    cursor.execute(
        "INSERT INTO dimension_hora (hora, rango_horario) VALUES (%s, %s) RETURNING id_dimension_hora",
        (hora, rango)
    )
    return cursor.fetchone()[0]

def _dim_sucursal(cursor, ciudad, num_emp):
    cursor.execute("SELECT id_dimension_sucursal FROM dimension_sucursal WHERE ciudad = %s", (ciudad,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_sucursal (ciudad, num_empleados) VALUES (%s, %s) RETURNING id_dimension_sucursal",
        (ciudad, num_emp)
    )
    return cursor.fetchone()[0]

def _dim_empleado(cursor, nombre, apellido, cargo, rut):
    rut_int = limpiar_rut_a_int(rut)
    cursor.execute("SELECT id_dimension_empleado FROM dimension_empleado WHERE rut = %s", (rut_int,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_empleado (nombre, apellido, cargo, rut) VALUES (%s, %s, %s, %s) RETURNING id_dimension_empleado",
        (nombre, apellido, cargo, rut_int)
    )
    return cursor.fetchone()[0]

def _dim_caja(cursor, numero):
    cursor.execute("SELECT id_dimension_caja FROM dimension_caja WHERE numero = %s", (numero,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_caja (numero) VALUES (%s) RETURNING id_dimension_caja",
        (numero,)
    )
    return cursor.fetchone()[0]

def _dim_cliente(cursor, rut, nombre, apellido, sexo):
    if not rut:
        return None
    rut_int = limpiar_rut_a_int(rut)
    cursor.execute("SELECT id_dimension_cliente FROM dimension_cliente WHERE rut = %s", (rut_int,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_cliente (rut, nombre, apellido, sexo) VALUES (%s, %s, %s, %s) RETURNING id_dimension_cliente",
        (rut_int, nombre, apellido, sexo)
    )
    return cursor.fetchone()[0]

def _dim_producto(cursor, nombre, es_vegano):
    cursor.execute("SELECT id_dimension_producto FROM dimension_producto WHERE nombre = %s", (nombre,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO dimension_producto (nombre, es_vegano) VALUES (%s, %s) RETURNING id_dimension_producto",
        (nombre, es_vegano)
    )
    return cursor.fetchone()[0]


def _etl_ventas(cursor_trans, cursor_analitica, conn_analitica, fecha):
    cursor_trans.execute("""
        SELECT 
            t.id_transaccion, t.fecha_hora,
            s.ciudad, s.numero_empleados,
            e.nombre, e.apellido, co.cargo, e.rut,
            c.numero_caja,
            cl.rut, cl.nombre, cl.apellido, cl.sexo,
            p.nombre, p.es_vegano,
            (dt.cantidad * p.precio)
        FROM Transaccion t
        JOIN Detalle_Transaccion dt ON t.id_transaccion = dt.id_transaccion
        JOIN lote_producto lp ON dt.id_lote_producto = lp.id_lote_producto
        JOIN Producto p ON lp.id_producto = p.id_producto
        JOIN Empleado e ON t.id_empleado = e.id_empleado
        LEFT JOIN Contrato co ON e.id_empleado = co.id_empleado
        JOIN Caja c ON t.id_caja = c.id_caja
        JOIN Sucursal s ON c.id_sucursal = s.id_sucursal
        LEFT JOIN Cliente cl ON t.id_cliente = cl.id_cliente
        WHERE t.fecha_hora::date = %s
    """, (fecha,))
    filas = cursor_trans.fetchall()
    
    insertadas = 0
    for venta in filas:
        (id_transaccion, fecha_hora, ciudad, num_emp, emp_nombre, emp_apellido,
         emp_cargo, emp_rut, num_caja, cli_rut, cli_nombre, cli_apellido,
         cli_sexo, prod_nombre, prod_vegano, monto_linea) = venta
        id_dim_fecha = _dim_fecha(cursor_analitica, fecha_hora.date())
        id_dim_hora = _dim_hora(cursor_analitica, fecha_hora.time())
        id_dim_sucursal = _dim_sucursal(cursor_analitica, ciudad, num_emp)
        id_dim_empleado = _dim_empleado(cursor_analitica, emp_nombre, emp_apellido, emp_cargo, emp_rut)
        id_dim_caja = _dim_caja(cursor_analitica, num_caja)
        id_dim_cliente = _dim_cliente(cursor_analitica, cli_rut, cli_nombre, cli_apellido, cli_sexo)
        id_dim_producto = _dim_producto(cursor_analitica, prod_nombre, prod_vegano)
        
        cursor_analitica.execute(
            "SELECT 1 FROM hecho_venta WHERE trasaccion_id = %s AND id_dimension_producto = %s",
            (id_transaccion, id_dim_producto)
        )
        if not cursor_analitica.fetchone():
            cursor_analitica.execute("""
                INSERT INTO hecho_venta (
                    id_dimension_fecha, id_dimension_hora, id_dimension_sucursal,
                    id_dimension_empleado, id_dimension_caja, id_dimension_cliente,
                    id_dimension_producto, trasaccion_id, monto
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_dim_fecha, id_dim_hora, id_dim_sucursal, id_dim_empleado,
                  id_dim_caja, id_dim_cliente, id_dim_producto, id_transaccion, int(monto_linea)))
            insertadas += 1
            
    conn_analitica.commit()
    return insertadas


def _etl_suministros(cursor_trans, cursor_analitica, conn_analitica, fecha):
    cursor_trans.execute("""
        SELECT 
            lp.id_lote_producto, lp.fecha_elaboracion,
            s.ciudad, s.numero_empleados,
            p.nombre, p.es_vegano,
            lp.stock, lp.coste_lote
        FROM lote_producto lp
        JOIN Producto p ON lp.id_producto = p.id_producto
        JOIN Maquina m ON lp.id_maquina = m.id_maquina
        JOIN Sucursal s ON m.id_sucursal = s.id_sucursal
        WHERE lp.fecha_elaboracion = %s
    """, (fecha,))
    filas = cursor_trans.fetchall()
    
    insertadas = 0
    for suministro in filas:
        (lote_id, fecha_elaboracion, ciudad, num_emp,
         prod_nombre, prod_vegano, cantidad_suministrada, costo_total) = suministro
        id_dim_fecha = _dim_fecha(cursor_analitica, fecha_elaboracion)
        id_dim_sucursal = _dim_sucursal(cursor_analitica, ciudad, num_emp)
        id_dim_producto = _dim_producto(cursor_analitica, prod_nombre, prod_vegano)
        
        cursor_analitica.execute(
            "SELECT 1 FROM hecho_suministro WHERE lote_id = %s", (lote_id,)
        )
        if not cursor_analitica.fetchone():
            cursor_analitica.execute("""
                INSERT INTO hecho_suministro (
                    id_dimension_fecha, id_dimension_sucursal, id_dimension_producto,
                    lote_id, cantidad_suministrada, costo_total
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_dim_fecha, id_dim_sucursal, id_dim_producto,
                  lote_id, int(cantidad_suministrada), int(costo_total)))
            insertadas += 1
            
    conn_analitica.commit()
    return insertadas


def _etl_empleados(cursor_trans, cursor_analitica, conn_analitica, fecha):
    cursor_trans.execute("""
        WITH turnos_agg AS (
            SELECT 
                id_empleado, fecha,
                SUM(COALESCE(
                    (EXTRACT(EPOCH FROM (hora_salida_real - hora_entrada_real)) -
                     EXTRACT(EPOCH FROM (COALESCE(hora_salida_colacion, hora_entrada_colacion) - hora_entrada_colacion))) / 3600.0,
                0)) AS horas_trabajadas,
                SUM(COALESCE(horas_extras, 0)) AS horas_extras
            FROM Turno
            WHERE fecha = %s
            GROUP BY id_empleado, fecha
        ),
        fallas_agg AS (
            SELECT c.id_empleado, f.fecha, COUNT(f.id_falla) AS total_fallas
            FROM Falla f
            JOIN Contrato c ON f.id_contrato = c.id_contrato
            WHERE f.fecha = %s
            GROUP BY c.id_empleado, f.fecha
        ),
        universo_dias AS (
            SELECT id_empleado, fecha FROM turnos_agg
            UNION
            SELECT id_empleado, fecha FROM fallas_agg
        )
        SELECT 
            ud.id_empleado, ud.fecha,
            e.nombre, e.apellido, e.rut, co.cargo,
            s.ciudad, s.numero_empleados,
            COALESCE(t.horas_trabajadas, 0),
            COALESCE(t.horas_extras, 0),
            COALESCE(f.total_fallas, 0)
        FROM universo_dias ud
        JOIN Empleado e ON ud.id_empleado = e.id_empleado
        JOIN Sucursal s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN Contrato co ON e.id_empleado = co.id_empleado
        LEFT JOIN turnos_agg t ON ud.id_empleado = t.id_empleado AND ud.fecha = t.fecha
        LEFT JOIN fallas_agg f ON ud.id_empleado = f.id_empleado AND ud.fecha = f.fecha
    """, (fecha, fecha))
    filas = cursor_trans.fetchall()
    
    insertadas = 0
    for registro in filas:
        (id_empleado, fecha_reg, emp_nombre, emp_apellido, emp_rut, emp_cargo,
         suc_ciudad, suc_num_emp, horas_trabajadas, horas_extras, fallas) = registro
        id_dim_fecha = _dim_fecha(cursor_analitica, fecha_reg)
        id_dim_sucursal = _dim_sucursal(cursor_analitica, suc_ciudad, suc_num_emp)
        id_dim_empleado = _dim_empleado(cursor_analitica, emp_nombre, emp_apellido, emp_cargo, emp_rut)
        
        cursor_analitica.execute(
            "SELECT 1 FROM hecho_empleado_diario WHERE id_dimension_empleado = %s AND id_dimension_fecha = %s",
            (id_dim_empleado, id_dim_fecha)
        )
        if not cursor_analitica.fetchone():
            cursor_analitica.execute("""
                INSERT INTO hecho_empleado_diario (
                    id_dimension_empleado, id_dimension_fecha, id_dimension_sucursal,
                    horas_trabajadas, horas_extras, fallas
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_dim_empleado, id_dim_fecha, id_dim_sucursal,
                  float(horas_trabajadas), float(horas_extras), int(fallas)))
            insertadas += 1
            
    conn_analitica.commit()
    return insertadas


def CargarHistorico():
    conn_trans = ConectarBaseTransaccional()
    conn_analitica = ConectarBaseAnalitica()
    cursor_trans = conn_trans.cursor()
    cursor_analitica = conn_analitica.cursor()

    try:
        cursor_trans.execute("""
            SELECT DISTINCT d FROM (
                SELECT fecha_hora::date  AS d FROM transaccion
                UNION
                SELECT fecha_elaboracion AS d FROM lote_producto WHERE fecha_elaboracion IS NOT NULL
                UNION
                SELECT fecha             AS d FROM turno          WHERE fecha IS NOT NULL
                UNION
                SELECT fecha             AS d FROM falla          WHERE fecha IS NOT NULL
            ) fechas
            ORDER BY d
        """)
        fechas = [row[0] for row in cursor_trans.fetchall()]

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando procesamiento histórico para {len(fechas)} fechas...")

        # Variables acumuladoras
        total_ventas = 0
        total_suministros = 0
        total_empleados = 0
        total_errores = 0

        for fecha in fechas:
            try:
                total_ventas += _etl_ventas(cursor_trans, cursor_analitica, conn_analitica, fecha)
            except Exception as e:
                conn_analitica.rollback()
                total_errores += 1
                print(f"  [ERROR CRÍTICO] Ventas en fecha {fecha}: {e}")
                
            try:
                total_suministros += _etl_suministros(cursor_trans, cursor_analitica, conn_analitica, fecha)
            except Exception as e:
                conn_analitica.rollback()
                total_errores += 1
                print(f"  [ERROR CRÍTICO] Suministros en fecha {fecha}: {e}")
                
            try:
                total_empleados += _etl_empleados(cursor_trans, cursor_analitica, conn_analitica, fecha)
            except Exception as e:
                conn_analitica.rollback()
                total_errores += 1
                print(f"  [ERROR CRÍTICO] Empleados en fecha {fecha}: {e}")

        # Mensaje de éxito consolidado al final
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Carga histórica finalizada.")
        print("==================================================")
        print("     RESUMEN GLOBAL DE REGISTROS NUEVOS CARGADOS   ")
        print("==================================================")
        print(f"  - Total de fechas analizadas     : {len(fechas)}")
        print(f"  - Nuevos Hechos Ventas           : {total_ventas}")
        print(f"  - Nuevos Hechos Suministros      : {total_suministros}")
        print(f"  - Nuevos Hechos Empleados Diario : {total_empleados}")
        print(f"  - Total de fallas u omisiones    : {total_errores}")
        print("==================================================")

    finally:
        cursor_trans.close()
        conn_trans.close()
        cursor_analitica.close()
        conn_analitica.close()


CargarHistorico()
