import schedule
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

def ConectarBaseAnalitica():
    return psycopg2.connect(
        dbname = "HeladeriaAnalitica",
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

        
def limpiar_rut_a_int(rut_str):
    if not rut_str:
        return None
    numeros = ''.join(filter(str.isdigit, str(rut_str)))
    return int(numeros) if numeros else None


def MeterDatos():

    # Hecho Venta ---------------------------------------------------------
    
    conn_trans = ConectarBaseTransaccional()
    conn_analitica = ConectarBaseAnalitica()
    
    cursor_trans = conn_trans.cursor()
    cursor_analitica = conn_analitica.cursor()
    
    sql_extraccion = """
        SELECT 
            t.id_transaccion,
            t.fecha_hora,
            s.ciudad,
            s.numero_empleados,
            e.nombre AS emp_nombre,
            e.apellido AS emp_apellido,
            co.cargo AS emp_cargo,
            e.rut AS emp_rut,
            c.numero_caja,
            cl.rut AS cli_rut,
            cl.nombre AS cli_nombre,
            cl.apellido AS cli_apellido,
            cl.sexo AS cli_sexo,
            p.nombre AS prod_nombre,
            p.es_vegano AS prod_vegano,
            (dt.cantidad * p.precio) AS monto_linea
        FROM Transaccion t
        JOIN Detalle_Transaccion dt ON t.id_transaccion = dt.id_transaccion
        JOIN lote_producto lp ON dt.id_lote_producto = lp.id_lote_producto
        JOIN Producto p ON lp.id_producto = p.id_producto
        JOIN Empleado e ON t.id_empleado = e.id_empleado
        LEFT JOIN Contrato co ON e.id_empleado = co.id_empleado -- Extrae el cargo actual
        JOIN Caja c ON t.id_caja = c.id_caja
        JOIN Sucursal s ON c.id_sucursal = s.id_sucursal
        LEFT JOIN Cliente cl ON t.id_cliente = cl.id_cliente
        WHERE t.fecha_hora::date = CURRENT_DATE - 1;
    """
    
    try:
        cursor_trans.execute(sql_extraccion)
        filas_ventas = cursor_trans.fetchall()
        
        for venta in filas_ventas:
            (id_transaccion, fecha_hora, ciudad, num_emp, emp_nombre, emp_apellido, 
             emp_cargo, emp_rut, num_caja, cli_rut, cli_nombre, cli_apellido, 
             cli_sexo, prod_nombre, prod_vegano, monto_linea) = venta
            

            fecha_solo = fecha_hora.date()
            cursor_analitica.execute("SELECT id_dimension_fecha FROM dimension_fecha WHERE fecha = %s", (fecha_solo,))
            res_fecha = cursor_analitica.fetchone()
            if res_fecha:
                id_dim_fecha = res_fecha[0]
            else:
                cursor_analitica.execute(
                    "INSERT INTO dimension_fecha (fecha, dia, mes, ano) VALUES (%s, %s, %s, %s) RETURNING id_dimension_fecha",
                    (fecha_solo, str(fecha_solo.day), str(fecha_solo.month), str(fecha_solo.year))
                )
                id_dim_fecha = cursor_analitica.fetchone()[0]
                
            hora_solo = fecha_hora.time()
            if 6 <= hora_solo.hour < 12:
                rango = "Mañana"
            elif 12 <= hora_solo.hour < 19:
                rango = "Tarde"
            else:
                rango = "Noche"
                
            cursor_analitica.execute("SELECT id_dimension_hora FROM dimension_hora WHERE hora = %s", (hora_solo,))
            res_hora = cursor_analitica.fetchone()
            if res_hora:
                id_dim_hora = res_hora[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_hora (hora, rango_horario) VALUES (%s, %s) RETURNING id_dimension_hora", (hora_solo, rango))
                id_dim_hora = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("SELECT id_dimension_sucursal FROM dimension_sucursal WHERE ciudad = %s", (ciudad,))
            res_suc = cursor_analitica.fetchone()
            if res_suc:
                id_dim_sucursal = res_suc[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_sucursal (ciudad, num_empleados) VALUES (%s, %s) RETURNING id_dimension_sucursal", (ciudad, num_emp))
                id_dim_sucursal = cursor_analitica.fetchone()[0]

            emp_rut_int = limpiar_rut_a_int(emp_rut)
            cursor_analitica.execute("SELECT id_dimension_empleado FROM dimension_empleado WHERE rut = %s", (emp_rut_int,))
            res_emp = cursor_analitica.fetchone()
            if res_emp:
                id_dim_empleado = res_emp[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_empleado (nombre, apellido, cargo, rut) VALUES (%s, %s, %s, %s) RETURNING id_dimension_empleado", (emp_nombre, emp_apellido, emp_cargo, emp_rut_int))
                id_dim_empleado = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("SELECT id_dimension_caja FROM dimension_caja WHERE numero = %s", (num_caja,))
            res_caja = cursor_analitica.fetchone()
            if res_caja:
                id_dim_caja = res_caja[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_caja (numero) VALUES (%s) RETURNING id_dimension_caja", (num_caja,))
                id_dim_caja = cursor_analitica.fetchone()[0]

            id_dim_cliente = None
            if cli_rut:
                cli_rut_int = limpiar_rut_a_int(cli_rut)
                cursor_analitica.execute("SELECT id_dimension_cliente FROM dimension_cliente WHERE rut = %s", (cli_rut_int,))
                res_cli = cursor_analitica.fetchone()
                if res_cli:
                    id_dim_cliente = res_cli[0]
                else:
                    cursor_analitica.execute("INSERT INTO dimension_cliente (rut, nombre, apellido, sexo) VALUES (%s, %s, %s, %s) RETURNING id_dimension_cliente", (cli_rut_int, cli_nombre, cli_apellido, cli_sexo))
                    id_dim_cliente = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("SELECT id_dimension_producto FROM dimension_producto WHERE nombre = %s", (prod_nombre,))
            res_prod = cursor_analitica.fetchone()
            if res_prod:
                id_dim_producto = res_prod[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_producto (nombre, es_vegano) VALUES (%s, %s) RETURNING id_dimension_producto", (prod_nombre, prod_vegano))
                id_dim_producto = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("""
                SELECT 1 FROM hecho_venta 
                WHERE trasaccion_id = %s AND id_dimension_producto = %s
            """, (id_transaccion, id_dim_producto))
            
            if not cursor_analitica.fetchone():
                cursor_analitica.execute("""
                    INSERT INTO hecho_venta (
                        id_dimension_fecha, id_dimension_hora, id_dimension_sucursal, 
                        id_dimension_empleado, id_dimension_caja, id_dimension_cliente, 
                        id_dimension_producto, trasaccion_id, monto
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_dim_fecha, id_dim_hora, id_dim_sucursal, id_dim_empleado, id_dim_caja, id_dim_cliente, id_dim_producto, id_transaccion, int(monto_linea)))

        conn_analitica.commit()
        print(f"Éxito: Se han procesado {len(filas_ventas)} registros de líneas de venta.")

    except Exception as e:
        conn_analitica.rollback()
        print(f"Error crítico en el proceso ETL de ventas: {e}")
        
    finally:
        cursor_trans.close()
        conn_trans.close()
        cursor_analitica.close()
        conn_analitica.close()

    # Hecho Suministro -------------------------------------------------------------------------
    
    conn_trans = ConectarBaseTransaccional()
    conn_analitica = ConectarBaseAnalitica()
    
    cursor_trans = conn_trans.cursor()
    cursor_analitica = conn_analitica.cursor()
    
    sql_extraccion = """
        SELECT 
            lp.id_lote_producto,
            lp.fecha_elaboracion,
            s.ciudad,
            s.numero_empleados,
            p.nombre AS prod_nombre,
            p.es_vegano AS prod_vegano,
            lp.stock AS cantidad_suministrada,
            lp.coste_lote AS costo_total
        FROM lote_producto lp
        JOIN Producto p ON lp.id_producto = p.id_producto
        JOIN Maquina m ON lp.id_maquina = m.id_maquina
        JOIN Sucursal s ON m.id_sucursal = s.id_sucursal
        WHERE lp.fecha_elaboracion = CURRENT_DATE - 1;
    """
    
    try:
        cursor_trans.execute(sql_extraccion)
        filas_suministros = cursor_trans.fetchall()
        
        for suministro in filas_suministros:
            (lote_id, fecha_elaboracion, ciudad, num_emp, 
             prod_nombre, prod_vegano, cantidad_suministrada, costo_total) = suministro
            
            cursor_analitica.execute("SELECT id_dimension_fecha FROM dimension_fecha WHERE fecha = %s", (fecha_elaboracion,))
            res_fecha = cursor_analitica.fetchone()
            if res_fecha:
                id_dim_fecha = res_fecha[0]
            else:
                cursor_analitica.execute(
                    "INSERT INTO dimension_fecha (fecha, dia, mes, ano) VALUES (%s, %s, %s, %s) RETURNING id_dimension_fecha",
                    (fecha_elaboracion, str(fecha_elaboracion.day), str(fecha_elaboracion.month), str(fecha_elaboracion.year))
                )
                id_dim_fecha = cursor_analitica.fetchone()[0]
                
            cursor_analitica.execute("SELECT id_dimension_sucursal FROM dimension_sucursal WHERE ciudad = %s", (ciudad,))
            res_suc = cursor_analitica.fetchone()
            if res_suc:
                id_dim_sucursal = res_suc[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_sucursal (ciudad, num_empleados) VALUES (%s, %s) RETURNING id_dimension_sucursal", (ciudad, num_emp))
                id_dim_sucursal = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("SELECT id_dimension_producto FROM dimension_producto WHERE nombre = %s", (prod_nombre,))
            res_prod = cursor_analitica.fetchone()
            if res_prod:
                id_dim_producto = res_prod[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_producto (nombre, es_vegano) VALUES (%s, %s) RETURNING id_dimension_producto", (prod_nombre, prod_vegano))
                id_dim_producto = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("""
                SELECT 1 FROM hecho_suministro 
                WHERE lote_id = %s
            """, (lote_id,))
            
            if not cursor_analitica.fetchone():
                cursor_analitica.execute("""
                    INSERT INTO hecho_suministro (
                        id_dimension_fecha, id_dimension_sucursal, id_dimension_producto, 
                        lote_id, cantidad_suministrada, costo_total
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_dim_fecha, id_dim_sucursal, id_dim_producto, lote_id, int(cantidad_suministrada), int(costo_total)))

        conn_analitica.commit()
        print(f"Éxito: Se han procesado {len(filas_suministros)} lotes en hecho_suministro.")

    except Exception as e:
        conn_analitica.rollback()
        print(f"Error crítico en el proceso ETL de suministros: {e}")
        
    finally:
        cursor_trans.close()
        conn_trans.close()
        cursor_analitica.close()
        conn_analitica.close()
        
    # Hecho Empleados Dia -------------------------------------------------------------------------    
    conn_trans = ConectarBaseTransaccional()
    conn_analitica = ConectarBaseAnalitica()
    
    cursor_trans = conn_trans.cursor()
    cursor_analitica = conn_analitica.cursor()
    
    sql_extraccion = """
        WITH turnos_agg AS (
            SELECT 
                id_empleado,
                fecha,
                SUM(COALESCE(
                    (EXTRACT(EPOCH FROM (hora_salida_real - hora_entrada_real)) - 
                     EXTRACT(EPOCH FROM (COALESCE(hora_salida_colacion, hora_entrada_colacion) - hora_entrada_colacion))) / 3600.0, 
                    0
                )) AS horas_trabajadas,
                SUM(COALESCE(horas_extras, 0)) AS horas_extras
            FROM Turno
            WHERE fecha = CURRENT_DATE - 1
            GROUP BY id_empleado, fecha
        ),
        fallas_agg AS (
            SELECT 
                c.id_empleado,
                f.fecha,
                COUNT(f.id_falla) AS total_fallas
            FROM Falla f
            JOIN Contrato c ON f.id_contrato = c.id_contrato
            WHERE f.fecha = CURRENT_DATE - 1
            GROUP BY c.id_empleado, f.fecha
        ),
        universo_dias AS (
            SELECT id_empleado, fecha FROM turnos_agg
            UNION
            SELECT id_empleado, fecha FROM fallas_agg
        )
        SELECT 
            ud.id_empleado,
            ud.fecha,
            e.nombre AS emp_nombre,
            e.apellido AS emp_apellido,
            e.rut AS emp_rut,
            co.cargo AS emp_cargo,
            s.ciudad AS suc_ciudad,
            s.numero_empleados AS suc_num_emp,
            COALESCE(t.horas_trabajadas, 0) AS horas_trabajadas,
            COALESCE(t.horas_extras, 0) AS horas_extras,
            COALESCE(f.total_fallas, 0) AS fallas
        FROM universo_dias ud
        JOIN Empleado e ON ud.id_empleado = e.id_empleado
        JOIN Sucursal s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN Contrato co ON e.id_empleado = co.id_empleado
        LEFT JOIN turnos_agg t ON ud.id_empleado = t.id_empleado AND ud.fecha = t.fecha
        LEFT JOIN fallas_agg f ON ud.id_empleado = f.id_empleado AND ud.fecha = f.fecha;
    """
    
    try:
        cursor_trans.execute(sql_extraccion)
        filas_empleados = cursor_trans.fetchall()
        
        for registro in filas_empleados:
            (id_empleado, fecha, emp_nombre, emp_apellido, emp_rut, emp_cargo, 
             suc_ciudad, suc_num_emp, horas_trabajadas, horas_extras, fallas) = registro
            
            cursor_analitica.execute("SELECT id_dimension_fecha FROM dimension_fecha WHERE fecha = %s", (fecha,))
            res_fecha = cursor_analitica.fetchone()
            if res_fecha:
                id_dim_fecha = res_fecha[0]
            else:
                cursor_analitica.execute(
                    "INSERT INTO dimension_fecha (fecha, dia, mes, ano) VALUES (%s, %s, %s, %s) RETURNING id_dimension_fecha",
                    (fecha, str(fecha.day), str(fecha.month), str(fecha.year))
                )
                id_dim_fecha = cursor_analitica.fetchone()[0]
                
            cursor_analitica.execute("SELECT id_dimension_sucursal FROM dimension_sucursal WHERE ciudad = %s", (suc_ciudad,))
            res_suc = cursor_analitica.fetchone()
            if res_suc:
                id_dim_sucursal = res_suc[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_sucursal (ciudad, num_empleados) VALUES (%s, %s) RETURNING id_dimension_sucursal", (suc_ciudad, suc_num_emp))
                id_dim_sucursal = cursor_analitica.fetchone()[0]

            emp_rut_int = limpiar_rut_a_int(emp_rut)
            cursor_analitica.execute("SELECT id_dimension_empleado FROM dimension_empleado WHERE rut = %s", (emp_rut_int,))
            res_emp = cursor_analitica.fetchone()
            if res_emp:
                id_dim_empleado = res_emp[0]
            else:
                cursor_analitica.execute("INSERT INTO dimension_empleado (nombre, apellido, cargo, rut) VALUES (%s, %s, %s, %s) RETURNING id_dimension_empleado", (emp_nombre, emp_apellido, emp_cargo, emp_rut_int))
                id_dim_empleado = cursor_analitica.fetchone()[0]

            cursor_analitica.execute("""
                SELECT 1 FROM hecho_empleado_diario 
                WHERE id_dimension_empleado = %s AND id_dimension_fecha = %s
            """, (id_dim_empleado, id_dim_fecha))
            
            if not cursor_analitica.fetchone():
                cursor_analitica.execute("""
                    INSERT INTO hecho_empleado_diario (
                        id_dimension_empleado, id_dimension_fecha, id_dimension_sucursal, 
                        horas_trabajadas, horas_extras, fallas
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_dim_empleado, id_dim_fecha, id_dim_sucursal, float(horas_trabajadas), float(horas_extras), int(fallas)))

        conn_analitica.commit()
        print(f"Éxito: Se han procesado {len(filas_empleados)} reportes diarios de gestión de empleados.")

    except Exception as e:
        conn_analitica.rollback()
        print(f"Error crítico en el proceso ETL de empleados diarios: {e}")
        
    finally:
        cursor_trans.close()
        conn_trans.close()
        cursor_analitica.close()
        conn_analitica.close()




schedule.every().day.at("01:00").do(MeterDatos)
# schedule.every(10).seconds.do(MeterDatos)
while True:
    schedule.run_pending()
    time.sleep(1)

