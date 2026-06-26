import time
import psycopg2
from datetime import datetime
import os
import csv

def ConectarBaseAnalitica():
    return psycopg2.connect(
        dbname = "HeladeriaAnalitica",
        user = "postgres",
        password = "13456",
        host = "localhost",
        port = "5432"
    )

def EjecutarYExportarCSV(sql, nombre_archivo):
    carpeta = "reportes"
    os.makedirs(carpeta, exist_ok=True)
    ruta_completa = os.path.join(carpeta, nombre_archivo)
    
    conn = ConectarBaseAnalitica()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        
        columnas = [desc[0] for desc in cursor.description]
        resultados = cursor.fetchall()

        with open(ruta_completa, mode='w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow(columnas)
            writer.writerows(resultados)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Éxito: Reporte guardado en '{ruta_completa}' con {len(resultados)} filas.")
        
    except Exception as e:
        print(f"Error al procesar el reporte {nombre_archivo}: {e}")
    finally:
        cursor.close()
        conn.close()

def GenerarTodosLosReportes():
    print(f"=== Iniciando el proceso de Análisis de Negocio ===\n")
    
    reportes_config = {
        "1.csv": """
            SELECT 
                s.ciudad,
                COALESCE(v.total_ventas, 0) AS total_ventas,
                COALESCE(sumi.total_costo, 0) AS total_costo_suministro,
                (COALESCE(v.total_ventas, 0) - COALESCE(sumi.total_costo, 0)) AS beneficio_neto
            FROM dimension_sucursal s
            LEFT JOIN (
                SELECT id_dimension_sucursal, SUM(monto) AS total_ventas
                FROM hecho_venta
                GROUP BY id_dimension_sucursal
            ) v ON s.id_dimension_sucursal = v.id_dimension_sucursal
            LEFT JOIN (
                SELECT id_dimension_sucursal, SUM(costo_total) AS total_costo
                FROM hecho_suministro
                GROUP BY id_dimension_sucursal
            ) sumi ON s.id_dimension_sucursal = sumi.id_dimension_sucursal
            ORDER BY beneficio_neto DESC;
        """,
        
        "2.csv": """
            SELECT 
                c.sexo,
                p.nombre AS producto,
                COUNT(v.id_hecho_venta) AS cantidad_ventas,
                SUM(v.monto) AS ingresos_totales
            FROM hecho_venta v
            JOIN dimension_cliente c ON v.id_dimension_cliente = c.id_dimension_cliente
            JOIN dimension_producto p ON v.id_dimension_producto = p.id_dimension_producto
            GROUP BY c.sexo, p.nombre
            ORDER BY c.sexo, ingresos_totales DESC;
        """,
        
        "3.csv": """
            SELECT 
                h.rango_horario,
                EXTRACT(HOUR FROM h.hora) AS hora_exacta,
                SUM(v.monto) AS monto_total_ventas,
                COUNT(DISTINCT v.trasaccion_id) AS total_transacciones
            FROM hecho_venta v
            JOIN dimension_hora h ON v.id_dimension_hora = h.id_dimension_hora
            GROUP BY h.rango_horario, EXTRACT(HOUR FROM h.hora)
            ORDER BY monto_total_ventas DESC;
        """,
        
        "4.csv": """
            SELECT 
                e.rut,
                e.nombre || ' ' || e.apellido AS empleado,
                e.cargo,
                COALESCE(v.total_monto, 0) AS total_vendido,
                COALESCE(g.total_horas_extras, 0) AS total_horas_extras,
                COALESCE(g.total_fallas, 0) AS total_fallas
            FROM dimension_empleado e
            LEFT JOIN (
                SELECT id_dimension_empleado, SUM(monto) AS total_monto
                FROM hecho_venta
                GROUP BY id_dimension_empleado
            ) v ON e.id_dimension_empleado = v.id_dimension_empleado
            LEFT JOIN (
                SELECT id_dimension_empleado, SUM(horas_extras) AS total_horas_extras, SUM(fallas) AS total_fallas
                FROM hecho_empleado_diario
                GROUP BY id_dimension_empleado
            ) g ON e.id_dimension_empleado = g.id_dimension_empleado
            ORDER BY total_vendido DESC;
        """,
        
        "5.csv": """
            SELECT 
                s.ciudad,
                p.nombre AS producto,
                SUM(hs.cantidad_suministrada) AS unidades_suministradas,
                SUM(hs.costo_total) AS costo_total_suministro
            FROM hecho_suministro hs
            JOIN dimension_sucursal s ON hs.id_dimension_sucursal = s.id_dimension_sucursal
            JOIN dimension_producto p ON hs.id_dimension_producto = p.id_dimension_producto
            GROUP BY s.ciudad, p.nombre
            ORDER BY s.ciudad, costo_total_suministro DESC;
        """
    }
    
    for archivo, query in reportes_config.items():
        EjecutarYExportarCSV(query, archivo)
        
    print(f"\n=== Todos los reportes analíticos se han generado de forma exitosa ===")

if __name__ == "__main__":
    GenerarTodosLosReportes()
        
