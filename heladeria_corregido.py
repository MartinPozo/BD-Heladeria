import psycopg2
from datetime import datetime, timedelta

def Conectar():
    return psycopg2.connect(
        dbname = "Heladeria_Db",
        user = "postgres",
        password = "1234",
        host = "localhost",
        port = "5432"
    )

def Ejecutar(sql, parametros = None, retornar_datos = False):
    conn = Conectar()
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
    sentencias = [
        "SET search_path TO public;",
        """
        TRUNCATE TABLE 
            detalle_transaccion, transaccion, detalle_caja, caja, 
            lote_producto, producto, maquina, falla, contrato, 
            turno, horario, empleado, sucursal, cliente 
        RESTART IDENTITY CASCADE;
        """,
        """
        INSERT INTO sucursal (ciudad, direccion, numero_empleados, numero_ventas) VALUES
        ('Puerto Montt', 'Costanera 123', 5, 0),
        ('Puerto Varas', 'Walker Martínez 450', 5, 0),
        ('Castro', 'Plaza de Armas 10', 5, 0);
        """,
        """
        INSERT INTO maquina (id_sucursal, fecha_ultima_limpieza, en_uso, consumo, sabor_actual)
        SELECT 
            (i %% 3) + 1,
            NOW() - (random() * INTERVAL '15 days'),
            true,
            (random() * 50 + 100)::decimal(10,2), 
            (ARRAY['Frutilla', 'Chocolate', 'Vainilla', 'Lúcuma', 'Manjar'])[floor(random() * 5) + 1]
        FROM generate_series(1, 15) AS i;
        """,
        """
        INSERT INTO producto (precio, nombre, es_vegano, receta)
        SELECT 
            (ARRAY[1500, 2000, 2500, 3000])[floor(random() * 4) + 1],
            (ARRAY['Helado Chocolate Suizo', 'Helado Lúcuma Nuez', 'Helado Frambuesa', 'Helado Vainilla Bourbon', 'Helado Manjar Chips', 'Helado Pistacho', 'Helado Frutos Rojos', 'Helado Pasas al Ron', 'Helado Piña'])[floor(random() * 9) + 1],
            (random() > 0.8), 
            'Receta estándar de simulación'
        FROM generate_series(1, 30) AS i;
        """,
        """
        INSERT INTO lote_producto (coste_lote, stock, fecha_elaboracion, fecha_vencimiento, id_maquina, id_producto)
        SELECT
            floor(random() * 5000 + 2000)::int,
            floor(random() * 100 + 20)::int,
            CURRENT_DATE - 2,
            CURRENT_DATE + 30,
            (floor(random() * 15) + 1),
            (floor(random() * 30) + 1)
        FROM generate_series(1, 50) AS i;
        """,
        """
        INSERT INTO empleado (rut, nombre, apellido, id_sucursal)
        SELECT 
            (floor(random() * 5 + 15))::text || '.' || floor(random()*899+100)::text || '.' || floor(random()*899+100)::text || '-' || floor(random()*10)::text,
            (ARRAY['Quidel', 'Andy', 'Bastián', 'Catalina', 'Diego', 'Elena', 'Felipe', 'Gloria', 'Hugo', 'Isabel'])[floor(random() * 10) + 1],
            (ARRAY['Barriga', 'Briones', 'Andrade', 'Barría', 'Cárdenas', 'Díaz', 'Espinoza', 'Flores', 'Galdames', 'Henríquez'])[floor(random() * 10) + 1],
            (i %% 3) + 1
        FROM generate_series(1, 10) AS i;
        """,
        """
        INSERT INTO contrato (id_empleado, fecha_inicio, es_indefinido, cargo)
        SELECT id_empleado, '2024-01-01'::date, true, 'Vendedor/Operario' FROM empleado;
        """,
        """
        INSERT INTO caja (id_sucursal, numero_caja, estado)
        SELECT (id_empleado %% 3) + 1, 1, true FROM empleado WHERE id_empleado <= 3;
        """,
        """
        INSERT INTO detalle_caja (monto_apertura, monto_cierre, id_empleado_responsable, fecha, transacciones_del_dia, id_caja)
        SELECT 50000.00, NULL, id_empleado, CURRENT_DATE, 0, id_empleado FROM empleado WHERE id_empleado <= 3;
        """,
        """
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
        """,
        """
        INSERT INTO transaccion (id_caja, id_empleado, id_cliente, metodo_pago, monto_total, fecha_hora)
        SELECT 
            (floor(random() * 3) + 1),
            (floor(random() * 10) + 1),
            (floor(random() * 500) + 1), 
            (ARRAY['Efectivo', 'Débito', 'Crédito'])[floor(random() * 3) + 1],
            (random() * 10000 + 3000)::decimal(10,2),
            '2026-01-01 01:00:00'::timestamp + (i * INTERVAL '15 minutes')
        FROM generate_series(1, 2500) as i;
        """,
        """
        INSERT INTO detalle_transaccion (id_transaccion, id_lote_producto, cantidad)
        SELECT 
            i, 
            (floor(random() * 50) + 1),
            (floor(random() * 3) + 1)
        FROM generate_series(1, 2500) AS i;
        """,
    ]

    try:
        print("Insertando muestra ligera con nombres reales para la UI...")
        for sentencia in sentencias:
            Ejecutar(sentencia)
        print("¡Muestra de datos realistas creada con éxito!")
    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")


def ListarSucursales():
    sucursales = Ejecutar("SELECT id_sucursal, ciudad, direccion, numero_empleados, numero_ventas FROM sucursal ORDER BY id_sucursal ASC", retornar_datos=True)
    
    print('\n==================================================================================================')
    print('                                  LISTA DE SUCURSALES REGISTRADAS                                 ')
    print('==================================================================================================')
    
    if sucursales:
        print(f"{'ID':<6} | {'CIUDAD':<15} | {'DIRECCIÓN':<30} | {'EMPLEADOS':<10} | {'VENTAS':<10}")
        print('--------------------------------------------------------------------------------------------------')
        
        for suc in sucursales:
            print(f"{suc[0]:<6} | {suc[1]:<15} | {suc[2]:<30} | {suc[3]:<10} | {suc[4]:<10}")
    else:
        print('No hay sucursales registradas en el sistema.')
        
    print('==================================================================================================\n')


def AñadirSucursal():
    print('Ingrese los datos de la sucursal (Presione X para cancelar): ')
    
    ciudad = input('Ciudad de la sucursal: ')
    if ciudad.lower() == 'x': return

    direccion = input('Direccion de la sucursal: ')
    if direccion.lower() == 'x': return

    numero_empleados = 0
    numero_ventas = 0

    Ejecutar(
        """
        INSERT INTO sucursal (ciudad, direccion, numero_empleados, numero_ventas)
        VALUES (%s, %s, %s, %s)
        """,
        (ciudad, direccion, numero_empleados, numero_ventas)
    )


def ConsultarVentas():
    fecha_inicio = input('Fecha de inicio (AAAA-MM-DD) (Presione X para cancelar): ')
    if fecha_inicio.lower() == 'x': return

    fecha_fin = input('Fecha de fin (AAAA-MM-DD) (Presione X para cancelar): ')
    if fecha_fin.lower() == 'x': return

    filtro_ciudad = input('Ciudad para filtrar (Presione Enter para omitir o X para cancelar): ')
    if filtro_ciudad.lower() == 'x': return
    if filtro_ciudad == '':
        filtro_ciudad = None

    fecha_fin_completa = f"{fecha_fin} 23:59:59"

    sql = """
    SELECT 
        s.ciudad,
        s.direccion,
        COUNT(t.id_transaccion) AS cantidad_ventas,
        COALESCE(SUM(t.monto_total), 0) AS monto_total_ventas
    FROM sucursal s
    LEFT JOIN caja c ON s.id_sucursal = c.id_sucursal
    LEFT JOIN transaccion t ON c.id_caja = t.id_caja AND t.fecha_hora BETWEEN %s AND %s
    """
    
    parametros = [fecha_inicio, fecha_fin_completa]
    
    if filtro_ciudad:
        sql += " WHERE s.ciudad = %s"
        parametros.append(filtro_ciudad)
            
    sql += " GROUP BY s.id_sucursal, s.ciudad, s.direccion;"
    
    parametros_tupla = tuple(parametros)
    
    filas = Ejecutar(sql, parametros_tupla, retornar_datos=True)
    
    print(f"\n--- REPORTE DE VENTAS ENTRE {fecha_inicio} Y {fecha_fin} ---")
    if not filas:
        print("No se encontraron ventas para los criterios ingresados.")
    else:
        for fila in filas:
            print(f"Ciudad: {fila[0]} | Dirección: {fila[1]} | Cantidad de boletas: {fila[2]} | Total Recaudado: ${fila[3]:,.0f}")
            
    return filas

def ConsultarGastos():
    fecha_inicio = input('Fecha de inicio (AAAA-MM-DD) (Presione X para cancelar): ')
    if fecha_inicio.lower() == 'x': return

    fecha_fin = input('Fecha de fin (AAAA-MM-DD) (Presione X para cancelar): ')
    if fecha_fin.lower() == 'x': return

    sql = """
    WITH gasto_sueldos AS (
        SELECT 
            e.id_sucursal,
            COALESCE(SUM(CASE WHEN con.cargo = 'Administrador' THEN 1200000 ELSE 530000 END), 0) AS total_sueldos
        FROM empleado e
        JOIN contrato con ON e.id_empleado = con.id_empleado
        WHERE con.fecha_inicio <= %s AND (con.fecha_termino IS NULL OR con.fecha_termino >= %s)
        GROUP BY e.id_sucursal
    ),
    gasto_maquinas AS (
        SELECT 
            m.id_sucursal,
            COALESCE(SUM(m.consumo), 0) AS total_maquinas
        FROM maquina m
        GROUP BY m.id_sucursal
    ),
    gasto_lotes AS (
        SELECT 
            m.id_sucursal,
            COALESCE(SUM(l.coste_lote), 0) AS total_lotes
        FROM lote_producto l
        JOIN maquina m ON l.id_maquina = m.id_maquina
        WHERE l.fecha_elaboracion BETWEEN %s AND %s
        GROUP BY m.id_sucursal
    )
    SELECT 
        s.id_sucursal,
        s.ciudad,
        COALESCE(gs.total_sueldos, 0) AS sueldos,
        COALESCE(gm.total_maquinas, 0) AS maquinas,
        COALESCE(gl.total_lotes, 0) AS lotes,
        (COALESCE(gs.total_sueldos, 0) + COALESCE(gm.total_maquinas, 0) + COALESCE(gl.total_lotes, 0)) AS total
    FROM sucursal s
    LEFT JOIN gasto_sueldos gs ON s.id_sucursal = gs.id_sucursal
    LEFT JOIN gasto_maquinas gm ON s.id_sucursal = gm.id_sucursal
    LEFT JOIN gasto_lotes gl ON s.id_sucursal = gl.id_sucursal
    ORDER BY s.id_sucursal ASC;
    """
    
    parametros = (fecha_fin, fecha_inicio, fecha_inicio, fecha_fin)
    filas = Ejecutar(sql, parametros, retornar_datos=True)
    
    print(f"\n--- GASTOS TOTALES ENTRE {fecha_inicio} Y {fecha_fin} ---")
    if not filas:
        print("No se encontraron registros para calcular gastos.")
    else:
        for fila in filas:
            print(f"Sucursal: {fila[1]} (ID: {fila[0]}) | Sueldos: ${fila[2]:,.0f} | Máquinas: ${fila[3]:,.0f} | Lotes: ${fila[4]:,.0f} | Total Gastos: ${fila[5]:,.0f}")
            
    return filas


def ConsultarSucursal(Id):
    if str(Id).lower() == 'x': return

    sucursal = Ejecutar("SELECT ciudad, direccion, numero_empleados, numero_ventas FROM sucursal WHERE id_sucursal = %s", (Id,), retornar_datos=True)
    if not sucursal:
        print('  !!Id invalido!!  \n')
        return

    print('\n==================================================')
    print(f'          DATOS DE LA SUCURSAL ID: {Id}')
    print('==================================================')
    print(f'Ciudad: {sucursal[0][0]}')
    print(f'Dirección: {sucursal[0][1]}')
    print(f'Número de empleados registrados: {sucursal[0][2]}')
    print(f'Total ventas: {sucursal[0][3]}')

    empleados = Ejecutar("SELECT id_empleado, rut, nombre, apellido FROM empleado WHERE id_sucursal = %s", (Id,), retornar_datos=True)
    print('\n--- LISTA DE EMPLEADOS ---')
    if empleados:
        for emp in empleados:
            print(f'ID Empleado: {emp[0]} | RUT: {emp[1]} | Nombre: {emp[2]} {emp[3]}')
    else:
        print('No hay empleados registrados en esta sucursal.')

    maquinas = Ejecutar("SELECT id_maquina, sabor_actual, consumo FROM maquina WHERE id_sucursal = %s", (Id,), retornar_datos=True)
    print('\n--- LISTA DE MÁQUINAS Y ENERGÍA CONSUMIDA ---')
    if maquinas:
        for maq in maquinas:
            print(f'ID Maquina: {maq[0]} | Sabor Actual: {maq[1]} | Consumo: {maq[2]} KW')
    else:
        print('No hay maquinas registradas en esta sucursal.')

    cajas = Ejecutar("SELECT id_caja, numero_caja, estado FROM caja WHERE id_sucursal = %s", (Id,), retornar_datos=True)
    print('\n--- LISTA DE CAJAS Y SUS ESTADOS ---')
    if cajas:
        for caj in cajas:
            if caj[2] == True:
                estado_texto = 'Abierto'
            else:
                estado_texto = 'Cerrado'
            print(f'ID Caja: {caj[0]} | Número Caja: {caj[1]} | Estado: {estado_texto}')
    else:
        print('No hay cajas registradas en esta sucursal.')
    
    print('==================================================\n')

def RevisarRut(Rut):
    Rut = Rut.replace(".", "").upper()
    
    if len(Rut) < 9 or len(Rut) > 10:
        return False
        
    if Rut[-2] != "-":
        return False
        
    for i in Rut:
        if not (i.isnumeric() or i == "-" or i == "K"):
            return False
            
    return True

def VerificarFecha(Fecha):
    if len(Fecha) != 10:
        return False
        
    if Fecha[4] != "-" or Fecha[7] != "-":
        return False
    partes = Fecha.split("-")   
    
    ano = partes[0]
    mes = partes[1]
    dia = partes[2]
    
    if not (ano.isnumeric() and mes.isnumeric() and dia.isnumeric()):
        return False

    int_ano = int(ano)
    int_mes = int(mes)
    int_dia = int(dia)
    
    if int_ano < 1900 or int_ano > 2100: 
        return False
    if int_mes < 1 or int_mes > 12:
        return False
    if int_dia < 1 or int_dia > 31:
        return False
        
    return True

def BuscarEmpleadoId(Id, id_empleado):
    sql = """
    SELECT id_empleado, rut, nombre, apellido 
    FROM empleado 
    WHERE id_sucursal = %s AND id_empleado = %s;
    """
    
    parametros = (Id, id_empleado)
    
    return Ejecutar(sql, parametros, retornar_datos=True)

def AñadirVenta(Id):
    if str(Id).lower() == 'x': return

    while True:
        id_caja = input('Ingrese el ID de la caja que opera la venta (Presione X para cancelar): ')
        if id_caja.lower() == 'x': return
        existe_caja = Ejecutar("SELECT id_caja FROM caja WHERE id_caja = %s AND id_sucursal = %s", (id_caja, Id), retornar_datos=True)
        if existe_caja:
            break
        print('!La caja no existe o no pertenece a esta sucursal¡')

    while True:
        id_empleado = input('Ingrese el ID del empleado que realiza la venta (Presione X para cancelar): ')
        if id_empleado.lower() == 'x': return
        existe_emp = Ejecutar("SELECT id_empleado FROM empleado WHERE id_empleado = %s AND id_sucursal = %s", (id_empleado, Id), retornar_datos=True)
        if existe_emp:
            break
        print('!El empleado no existe o no pertenece a esta sucursal¡')

    id_cliente = None
    crear_cliente = input("¿Desea registrar los datos del cliente para esta venta? (S o N) (Presione X para cancelar): ").upper()
    if crear_cliente == 'X': return
    
    if crear_cliente == "S":
        while True:
            rut_cliente = input("Ingrese RUT del cliente: ").strip()
            if rut_cliente.lower() == 'x': return
            if RevisarRut(rut_cliente):
                break
            print("El Rut ingresado no es válido. Intente nuevamente.")

        nombre_c = input("Ingrese Nombre: ").strip()
        if nombre_c.lower() == 'x': return
        
        apellido_c = input("Ingrese Apellido: ").strip()
        if apellido_c.lower() == 'x': return
        
        while True:
            correo_c = input("Ingrese Correo (debe ser @gmail.com): ").strip().lower()
            if correo_c == 'x': return
            if correo_c.endswith("@gmail.com"):
                break
            print("[ERROR] El correo electrónico debe finalizar estrictamente con el dominio '@gmail.com'.")

        while True:
            sexo_c = input("Ingrese Sexo (M: Masculino, F: Femenino): ").upper().strip()
            if sexo_c.lower() == 'x': return
            if sexo_c in ["M", "F"]:
                break
            print("[ERROR] Opción inválida. Ingrese solamente 'M' o 'F'.")
        
        sql_cliente = """
        INSERT INTO cliente (rut, nombre, apellido, correo, sexo) 
        VALUES (%s, %s, %s, %s, %s) RETURNING id_cliente;
        """
        resultado_cliente = Ejecutar(sql_cliente, (rut_cliente, nombre_c, apellido_c, correo_c, sexo_c), retornar_datos=True)
        id_cliente = resultado_cliente[0][0]

    lista_productos = []
    print('\n--- ARMADO DEL CARRO DE PRODUCTOS ---')
    while True:
        prod_input = input('Ingrese ID del producto (O escriba 0 para finalizar el carro / X para cancelar): ')
        if prod_input.lower() == 'x': return
        if prod_input == '0':
            if not lista_productos:
                print('!Debe añadir al menos un producto al carro para continuar¡')
                continue
            break
        
        resultado_precio = Ejecutar("SELECT precio FROM producto WHERE id_producto = %s;", (prod_input,), retornar_datos=True)
        if not resultado_precio:
            print(f"[ERROR] El producto con ID {prod_input} no existe.")
            continue
            
        cant_input = input(f'Ingrese la cantidad deseada para el producto ID {prod_input}: ')
        if cant_input.lower() == 'x': return
        if not cant_input.isnumeric() or int(cant_input) <= 0:
            print('!Cantidad inválida¡')
            continue
            
        lista_productos.append((prod_input, int(cant_input)))

    monto_total = 0
    detalles_a_insertar = []
    
    for id_producto, cantidad_pedida in lista_productos:
        resultado_precio = Ejecutar("SELECT precio FROM producto WHERE id_producto = %s;", (id_producto,), retornar_datos=True)
        precio_unitario = resultado_precio[0][0]
        
        sql_lotes = """
        SELECT l.id_lote_producto, l.stock 
        FROM lote_producto l
        INNER JOIN maquina m ON l.id_maquina = m.id_maquina
        WHERE l.id_producto = %s AND l.stock > 0 AND (l.fecha_vencimiento >= CURRENT_DATE OR l.fecha_vencimiento IS NULL) AND m.id_sucursal = %s
        ORDER BY l.fecha_vencimiento ASC;
        """
        lotes_disponibles = Ejecutar(sql_lotes, (id_producto, Id), retornar_datos=True)
        
        cantidad_por_surtir = cantidad_pedida
        
        if lotes_disponibles:
            for id_lote, stock_lote in lotes_disponibles:
                if cantidad_por_surtir <= 0:
                    break
                cantidad_a_sacar = min(cantidad_por_surtir, stock_lote)
                detalles_a_insertar.append((id_lote, cantidad_a_sacar))
                cantidad_por_surtir -= cantidad_a_sacar
                
        if cantidad_por_surtir > 0:
            print(f"[ERROR] No hay suficiente stock en esta sucursal para el producto ID {id_producto}. Falta(n) {cantidad_por_surtir} unidad(es).")
            return
            
        monto_total += (precio_unitario * cantidad_pedida)

    metodo_pago = input('Ingrese método de pago (Efectivo/Debito/Credito) (Presione X para cancelar): ')
    if metodo_pago.lower() == 'x': return

    while True:
        descuento_input = input('Ingrese monto de descuento (Presione Enter para 0 o X para cancelar): ')
        if descuento_input.lower() == 'x': return
        if descuento_input == '':
            descuento = 0
            break
        if descuento_input.isnumeric():
            descuento = int(descuento_input)
            break
        print('!Valor incorrecto¡')

    monto_final = max(0, monto_total - descuento)

    sql_transaccion = """
    INSERT INTO transaccion (id_caja, id_empleado, id_cliente, metodo_pago, monto_total, descuento) 
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_transaccion;
    """
    res_tx = Ejecutar(sql_transaccion, (id_caja, id_empleado, id_cliente, metodo_pago, monto_final, descuento), retornar_datos=True)
    id_transaccion = res_tx[0][0]

    for id_lote, cantidad in detalles_a_insertar:
        sql_det = """
        INSERT INTO detalle_transaccion (id_transaccion, id_lote_producto, cantidad) 
        VALUES (%s, %s, %s);
        """
        Ejecutar(sql_det, (id_transaccion, id_lote, cantidad))
        
        sql_update_lote = """
        UPDATE lote_producto 
        SET stock = stock - %s,
            fecha_salida_sala = COALESCE(fecha_salida_sala, CURRENT_DATE)
        WHERE id_lote_producto = %s;
        """
        Ejecutar(sql_update_lote, (cantidad, id_lote))

    sql_caja_auditoria = """
    UPDATE detalle_caja 
    SET transacciones_del_dia = transacciones_del_dia + 1 
    WHERE id_caja = %s AND fecha = CURRENT_DATE;
    """
    Ejecutar(sql_caja_auditoria, (id_caja,))
    
    sql_sucursal_auditoria = """
    UPDATE sucursal 
    SET numero_ventas = COALESCE(numero_ventas, 0) + 1 
    WHERE id_sucursal = %s;
    """
    Ejecutar(sql_sucursal_auditoria, (Id,))

    print(f"\n[SISTEMA] ¡Venta realizada con éxito! ID Transacción: {id_transaccion} | Total cobrado: ${monto_final:,.0f}")


def AñadirLoteProductos(Id):
    if str(Id).lower() == 'x': return

    maquinas = Ejecutar("SELECT id_maquina, sabor_actual, en_uso FROM maquina WHERE id_sucursal = %s", (Id,), retornar_datos=True)
    
    print('\n==================================================')
    print(f'     MÁQUINAS DISPONIBLES EN LA SUCURSAL ID: {Id}')
    print('==================================================')
    if maquinas:
        for maq in maquinas:
            if maq[2] == True:
                estado = 'En uso'
            else:
                estado = 'Fuera de uso'
            print(f'ID Máquina: {maq[0]} | Sabor Actual: {maq[1]} | Estado: {estado}')
        print('==================================================\n')
    else:
        print('No hay máquinas registradas en esta sucursal. Debe añadir una máquina primero.')
        print('==================================================\n')
        return

    while True:
        id_maquina = input('Copie e ingrese el ID de la máquina seleccionada: ')
        if id_maquina.lower() == 'x': return
        es_valida = any(str(maq[0]) == str(id_maquina) for maq in maquinas)
        if es_valida:
            break
        print('!ID de máquina incorrecto o no pertenece a esta sucursal¡')

    while True:
        id_producto = input('Ingrese el ID del producto asociado: ')
        if id_producto.lower() == 'x': return
        existe_prod = Ejecutar("SELECT id_producto FROM producto WHERE id_producto = %s", (id_producto,), retornar_datos=True)
        if existe_prod:
            break
        print('!El ID del producto no existe en la base de datos¡')

    while True:
        coste_lote = input('Coste del lote: ')
        if coste_lote.lower() == 'x': return
        if coste_lote.isnumeric():
            break
        print('!Valor incorrecto¡')

    while True:
        stock = input('Stock inicial del lote: ')
        if stock.lower() == 'x': return
        if stock.isnumeric():
            break
        print('!Valor incorrecto¡')

    fecha_elaboracion = datetime.now().date()
    
    while True:
        f_venc = input('Fecha de vencimiento (AAAA-MM-DD): ')
        if f_venc.lower() == 'x': return
        try:
            fecha_vencimiento = datetime.strptime(f_venc, '%Y-%m-%d').date()
            break
        except ValueError:
            print('!Formato de fecha inválido¡')

    fecha_salida_sala = fecha_elaboracion

    Ejecutar(
        """
        INSERT INTO lote_producto (coste_lote, stock, fecha_elaboracion, fecha_vencimiento, fecha_salida_sala, id_maquina, id_producto)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (coste_lote, stock, fecha_elaboracion, fecha_vencimiento, fecha_salida_sala, id_maquina, id_producto)
    )


    
def AñadirProducto():
    print('Ingrese los datos del producto (Presione X para cancelar): ')
    
    nombre = input('Nombre del producto: ')
    if nombre.lower() == 'x': return

    while True:
        precio = input('Precio del producto: ')
        if precio.lower() == 'x': return
        if precio.isnumeric():
            break
        print('!Valor incorrecto¡')

    print('1. Es apto para veganos')
    print('2. No es apto para veganos')
    print('X. Cancelar y salir')
    es_vegano = input('Seleccione una opcion: ')
    while not (es_vegano == '1' or es_vegano == '2' or es_vegano.lower() == 'x'):
        es_vegano = input('!Valor incorrecto¡ -- Vegano: ')
    if es_vegano.lower() == 'x': return
    if es_vegano == '1': es_vegano = True
    else: es_vegano = False

    receta = input('Ingredientes y pasos de preparacion: ')
    if receta.lower() == 'x': return

    Ejecutar(
        """
        INSERT INTO producto (nombre, precio, es_vegano, receta)
        VALUES (%s, %s, %s, %s)
        """,
        (nombre, precio, es_vegano, receta)
    )

    
def ModificarProducto(Id):
    if str(Id).lower() == 'x': return

    print('Ingrese el ID del producto a modificar (Presione X para cancelar): ')
    id_producto = input('ID Producto: ')
    if id_producto.lower() == 'x': return

    existe = Ejecutar("SELECT id_producto FROM producto WHERE id_producto = %s", (id_producto,), retornar_datos=True)
    if not existe:
        print('¡El ID del producto no existe en la base de datos!')
        return

    print('¿Que desea editar?')
    print('1. Nombre')
    print('2. Precio')
    print('3. Estado vegano')
    print('4. Receta')
    print('X. Cancelar y salir')
    opcion = input('Seleccione una opcion: ')

    if opcion.lower() == 'x': return

    if opcion == '1':
        nombre = input('Nuevo Nombre: ')
        if nombre.lower() == 'x': return
        Ejecutar(
            "UPDATE producto SET nombre = %s WHERE id_producto = %s",
            (nombre, id_producto)
        )

    elif opcion == '2':
        while True:
            precio = input('Nuevo Precio: ')
            if precio.lower() == 'x': return
            if precio.isnumeric():
                break
            print('!Valor incorrecto¡')
        Ejecutar(
            "UPDATE producto SET precio = %s WHERE id_producto = %s",
            (precio, id_producto)
        )

    elif opcion == '3':
        print('1. Es apto para veganos')
        print('2. No es apto para veganos')
        print('X. Cancelar y salir')
        es_vegano = input('Seleccione una opcion: ')
        while not (es_vegano == '1' or es_vegano == '2' or es_vegano.lower() == 'x'):
            es_vegano = input('!Valor incorrecto¡ -- Vegano: ')
        if es_vegano.lower() == 'x': return
        if es_vegano == '1': es_vegano = True
        else: es_vegano = False
        Ejecutar(
            "UPDATE producto SET es_vegano = %s WHERE id_producto = %s",
            (es_vegano, id_producto)
        )

    elif opcion == '4':
        receta = input('Nueva Receta (Ingredientes y pasos): ')
        if receta.lower() == 'x': return
        Ejecutar(
            "UPDATE producto SET receta = %s WHERE id_producto = %s",
            (receta, id_producto)
        )


def EliminarLote(Id):
    if str(Id).lower() == 'x': return

    print('Ingrese el ID del lote a eliminar (Presione X para cancelar): ')
    id_lote = input('ID Lote: ')
    if id_lote.lower() == 'x': return

    lote_origen = Ejecutar(
        "SELECT id_producto, stock FROM lote_producto WHERE id_lote_producto = %s", 
        (id_lote,), 
        retornar_datos=True
    )
    if not lote_origen:
        print('¡El ID del lote no existe en la base de datos!')
        return

    id_producto = lote_origen[0][0]
    stock_origen = lote_origen[0][1]

    ventas_asociadas = Ejecutar(
        """
        SELECT DT.id_detalle, DT.id_transaccion, DT.cantidad, T.id_caja, T.monto_total
        FROM detalle_transaccion DT
        JOIN transaccion T ON DT.id_transaccion = T.id_transaccion
        WHERE DT.id_lote_producto = %s
        """,
        (id_lote,),
        retornar_datos=True
    )

    if ventas_asociadas:
        fecha_actual = datetime.now().date()
        lote_destino = Ejecutar(
            """
            SELECT id_lote_producto 
            FROM lote_producto 
            WHERE id_producto = %s 
              AND id_lote_producto != %s 
              AND fecha_vencimiento >= %s
            ORDER BY fecha_vencimiento ASC 
            LIMIT 1
            """,
            (id_producto, id_lote, fecha_actual),
            retornar_datos=True
        )

        transferido = False
        if lote_destino:
            id_lote_nuevo = lote_destino[0][0]
            print('Se detectaron ventas asociadas a este lote.')
            print(f'¿Desea transferir las ventas al lote alternativo más próximo a vencer (ID Lote: {id_lote_nuevo})?')
            print('1. Si, transferir ventas y eliminar lote')
            print('2. No, eliminar ventas y el lote')
            print('X. Cancelar y salir')
            opcion = input('Seleccione una opcion: ')
            
            if opcion.lower() == 'x': return
            
            if opcion == '1':
                for venta in ventas_asociadas:
                    id_detalle = venta[0]
                    cantidad = venta[2]
                    
                    Ejecutar(
                        "UPDATE detalle_transaccion SET id_lote_producto = %s WHERE id_detalle = %s",
                        (id_lote_nuevo, id_detalle)
                    )
                    Ejecutar(
                        "UPDATE lote_producto SET stock = stock - %s WHERE id_lote_producto = %s",
                        (cantidad, id_lote_nuevo)
                    )
                transferido = True

        if not transferido:
            if not lote_destino:
                print('Se detectaron ventas asociadas, pero no existen otros lotes vigentes para este producto.')
                print('Se procederá a mostrar y eliminar las siguientes ventas vinculadas de forma automática:')
            else:
                print('Eliminando las siguientes ventas vinculadas de forma automática:')
                
            print('\n======================================================================')
            print(f"{'ID DETALLE':<12} | {'ID TRANSACCION':<15} | {'CANTIDAD':<10} | {'MONTO TOTAL':<12}")
            print('----------------------------------------------------------------------')
            for venta in ventas_asociadas:
                print(f"{venta[0]:<12} | {venta[1]:<15} | {venta[2]:<10} | {venta[4]:<12}")
            print('======================================================================\n')

            for venta in ventas_asociadas:
                id_detalle = venta[0]
                id_transaccion = venta[1]
                id_caja = venta[3]

                Ejecutar(
                    "DELETE FROM detalle_transaccion WHERE id_detalle = %s",
                    (id_detalle,)
                )

                restantes = Ejecutar(
                    "SELECT COUNT(*) FROM detalle_transaccion WHERE id_transaccion = %s",
                    (id_transaccion,),
                    retornar_datos=True
                )
                
                if restantes[0][0] == 0:
                    Ejecutar(
                        """
                        UPDATE detalle_caja 
                        SET transacciones_del_dia = transacciones_del_dia - 1 
                        WHERE id_caja = %s AND fecha = %s
                        """,
                        (id_caja, fecha_actual)
                    )
                    Ejecutar(
                        "UPDATE sucursal SET numero_ventas = numero_ventas - 1 WHERE id_sucursal = %s",
                        (Id,)
                    )
                    Ejecutar(
                        "DELETE FROM transaccion WHERE id_transaccion = %s",
                        (id_transaccion,)
                    )

    Ejecutar(
        "DELETE FROM lote_producto WHERE id_lote_producto = %s",
        (id_lote,)
    )


def EliminarVenta(Id):
    if str(Id).lower() == 'x': return

    ultima_transaccion = Ejecutar(
        """
        SELECT T.id_transaccion, T.id_caja, T.monto_total 
        FROM transaccion T
        JOIN caja C ON T.id_caja = C.id_caja
        WHERE C.id_sucursal = %s
        ORDER BY T.fecha_hora DESC
        LIMIT 1
        """, 
        (Id,), 
        retornar_datos=True
    )

    if not ultima_transaccion:
        print('¡No hay ventas registradas en esta sucursal para eliminar!')
        return

    id_transaccion = ultima_transaccion[0][0]
    id_caja = ultima_transaccion[0][1]
    monto_total = ultima_transaccion[0][2]

    print(f'¿Está seguro de que desea eliminar la última venta (ID Transacción: {id_transaccion})?')
    print('1. Si, eliminar')
    print('X. No, cancelar')
    confirmacion = input('Seleccione una opcion: ')
    if confirmacion.lower() == 'x': return

    if confirmacion == '1':
        detalles = Ejecutar(
            "SELECT id_lote_producto, cantidad FROM detalle_transaccion WHERE id_transaccion = %s", 
            (id_transaccion,), 
            retornar_datos=True
        )

        if detalles:
            for det in detalles:
                id_lote = det[0]
                cantidad = det[1]
                
                Ejecutar(
                    "UPDATE lote_producto SET stock = stock + %s WHERE id_lote_producto = %s",
                    (cantidad, id_lote)
                )

        fecha_actual = datetime.now().date()
        Ejecutar(
            """
            UPDATE detalle_caja 
            SET transacciones_del_dia = transacciones_del_dia - 1 
            WHERE id_caja = %s AND fecha = %s
            """,
            (id_caja, fecha_actual)
        )

        Ejecutar(
            "UPDATE sucursal SET numero_ventas = numero_ventas - 1 WHERE id_sucursal = %s",
            (Id,)
        )

        Ejecutar(
            "DELETE FROM detalle_transaccion WHERE id_transaccion = %s",
            (id_transaccion,)
        )

        Ejecutar(
            "DELETE FROM transaccion WHERE id_transaccion = %s",
            (id_transaccion,)
        )

        
def ConsultarStock(Id):
    sql = """
    SELECT
        l.id_lote_producto AS nro_lote,
        p.nombre AS producto,
        l.stock,
        l.fecha_elaboracion,
        l.fecha_vencimiento,
        m.id_maquina
    FROM sucursal s
    INNER JOIN maquina m ON s.id_sucursal = m.id_sucursal
    INNER JOIN lote_producto l ON m.id_maquina = l.id_maquina
    INNER JOIN producto p ON l.id_producto = p.id_producto
    WHERE s.id_sucursal = %s
    ORDER BY l.fecha_vencimiento ASC;
    """

    parametros = (Id,)

    filas = Ejecutar(sql, parametros, retornar_datos=True)

    print(f"\n--- DETALLE DE STOCK POR LOTE (SUCURSAL ID: {Id}) ---")
    if not filas:
        print("No hay lotes de stock registrados para esta sucursal.")
    else:
        for fila in filas:
            print(f"Lote N°: {fila[0]} | Producto: {fila[1]} | Stock: {fila[2]} ud. | F. Elab: {fila[3]} | F. Venc: {fila[4]} | Máquina ID: {fila[5]}")

    return filas



def AñadirMaquina(Id):
    if str(Id).lower() == 'x': return
    print('Ingrese los datos de la máquina (Presione X para cancelar)')
    sabor = input('Sabor: ')
    if sabor.lower() == 'x': return
    
    while True:
        consumo = input('Consumo: ')
        if consumo.lower() == 'x': return
        try:
            float(consumo)
            break
        except ValueError:
            print('!Valor incorrecto¡')

    print('1. Esta en uso')
    print('2. No esta en uso')
    print('X. Cancelar y salir')
    uso = input('uso: ')
    while not (uso == '1' or uso == '2' or uso.lower() == 'x'):
        uso = input('!Valor incorrecto¡ -- uso: ')
    if uso.lower() == 'x': return 
    if uso == '1': uso = True
    else: uso = False

    fecha = datetime.now().date()
    
    Ejecutar(
        """
        INSERT INTO maquina (fecha_ultima_limpieza, en_uso, sabor_actual, consumo, id_sucursal)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fecha, uso, sabor, consumo, Id)
    )


def EditarMaquina():
    print('Ingrese el ID de la maquina a editar (Presione X para cancelar): ')
    id_maquina = input('ID Maquina: ')
    if id_maquina.lower() == 'x': return

    existe = Ejecutar("SELECT id_maquina FROM maquina WHERE id_maquina = %s", (id_maquina,), retornar_datos=True)
    if not existe:
        print('¡El ID de la maquina no existe en la base de datos!')
        return

    print('¿Que desea editar?')
    print('1. Sabor actual')
    print('2. Estado de uso')
    print('3. Consumo')
    print('4. ID de la sucursal')
    print('5. Registrar limpieza hoy')
    print('X. Cancelar y salir')
    opcion = input('Seleccione una opcion: ')

    if opcion.lower() == 'x': return

    if opcion == '1':
        print('Ingrese el nuevo sabor (Presione X para cancelar): ')
        sabor = input('Nuevo Sabor: ')
        if sabor.lower() == 'x': return
        Ejecutar(
            "UPDATE maquina SET sabor_actual = %s WHERE id_maquina = %s",
            (sabor, id_maquina)
        )

    elif opcion == '2':
        print('1. Esta en uso')
        print('2. No esta en uso')
        print('X. Cancelar y salir')
        uso = input('uso: ')
        while not (uso == '1' or uso == '2' or uso.lower() == 'x'):
            uso = input('!Valor incorrecto¡ -- uso: ')
        if uso.lower() == 'x': return
        if uso == '1': uso = True
        else: uso = False
        Ejecutar(
            "UPDATE maquina SET en_uso = %s WHERE id_maquina = %s",
            (uso, id_maquina)
        )

    elif opcion == '3':
        while True:
            print('Ingrese el nuevo consumo (Presione X para cancelar): ')
            consumo = input('Nuevo Consumo: ')
            if consumo.lower() == 'x': return
            try:
                float(consumo)
                break
            except ValueError:
                print('!Valor incorrecto¡')
        Ejecutar(
            "UPDATE maquina SET consumo = %s WHERE id_maquina = %s",
            (consumo, id_maquina)
        )

    elif opcion == '4':
        while True:
            print('Ingrese el nuevo ID de la sucursal (Presione X para cancelar): ')
            sucursal = input('Nuevo ID de la sucursal: ')
            if sucursal.lower() == 'x': return
            if sucursal.isnumeric():
                break
            print('!Valor incorrecto¡')
        Ejecutar(
            "UPDATE maquina SET id_sucursal = %s WHERE id_maquina = %s",
            (sucursal, id_maquina)
        )

    elif opcion == '5':
        fecha = datetime.now().date()
        Ejecutar(
            "UPDATE maquina SET fecha_ultima_limpieza = %s WHERE id_maquina = %s",
            (fecha, id_maquina)
        )

def AñadirCaja(Id):
    print('Ingrese los datos de la caja (Presione X para cancelar): ')
    
    while True:
        numero_caja = input('Numero correlativo de caja: ')
        if numero_caja.lower() == 'x': return
        if numero_caja.isnumeric():
            break
        print('!Valor incorrecto¡')

    print('1. Operativa')
    print('2. Cerrada')
    print('X. Cancelar y salir')
    estado = input('Estado: ')
    while not (estado == '1' or estado == '2' or estado.lower() == 'x'):
        estado = input('!Valor incorrecto¡ -- Estado: ')
    if estado.lower() == 'x': return
    if estado == '1': estado = True
    else: estado = False

    Ejecutar(
        """
        INSERT INTO caja (id_sucursal, numero_caja, estado)
        VALUES (%s, %s, %s)
        """,
        (Id, numero_caja, estado)
    )
    
def EditarCaja(Id):
    if str(Id).lower() == 'x': return
    print('Ingrese el ID de la caja a editar (Presione X para cancelar): ')
    id_caja = input('ID Caja: ')
    if id_caja.lower() == 'x': return

    existe = Ejecutar("SELECT id_caja FROM caja WHERE id_caja = %s", (id_caja,), retornar_datos=True)
    if not existe:
        print('¡El ID de la caja no existe en la base de datos!')
        return

    print('¿Que desea editar?')
    print('1. Estado de la caja')
    print('2. Numero correlativo de caja')
    print('3. Eliminar la caja')
    print('X. Cancelar y salir')
    opcion = input('Seleccione una opcion: ')

    if opcion.lower() == 'x': return

    if opcion == '1':
        print('1. Operativa')
        print('2. Cerrada')
        print('X. Cancelar y salir')
        estado = input('Estado: ')
        while not (estado == '1' or estado == '2' or estado.lower() == 'x'):
            estado = input('!Valor incorrecto¡ -- Estado: ')
        if estado.lower() == 'x': return
        if estado == '1': estado = True
        else: estado = False
        Ejecutar(
            "UPDATE caja SET estado = %s WHERE id_caja = %s",
            (estado, id_caja)
        )

    elif opcion == '2':
        while True:
            print('Ingrese el nuevo numero correlativo (Presione X para cancelar): ')
            numero_caja = input('Numero correlativo de caja: ')
            if numero_caja.lower() == 'x': return
            if numero_caja.isnumeric():
                break
            print('!Valor incorrecto¡')
        Ejecutar(
            "UPDATE caja SET numero_caja = %s WHERE id_caja = %s",
            (numero_caja, id_caja)
        )

    elif opcion == '3':
        print('¿Esta seguro de que desea eliminar esta caja?')
        print('1. Si, eliminar')
        print('X. No, cancelar')
        confirmacion = input('Seleccione una opcion: ')
        if confirmacion.lower() == 'x': return
        if confirmacion == '1':
            Ejecutar(
                "DELETE FROM caja WHERE id_caja = %s",
                (id_caja,)
            )


def AñadirEmpleado(Id):
    if str(Id).lower() == 'x': return

    while True:
        rut = input("RUT del empleado (Formato XXXXXXXX-X) (Presione X para cancelar): ").strip()
        if rut.lower() == 'x': return
        if RevisarRut(rut):
            break
        print("El RUT ingresado no es válido. Intente nuevamente.")

    nombre = input("Nombre del empleado: ").strip()
    if nombre.lower() == 'x': return

    apellido = input("Apellido del empleado: ").strip()
    if apellido.lower() == 'x': return

    while True:
        fecha_inicio = input("Fecha de inicio de contrato (AAAA-MM-DD) (Presione X para cancelar): ").strip()
        if fecha_inicio.lower() == 'x': return
        if VerificarFecha(fecha_inicio):
            break
        print("Fecha incorrecta. Asegúrese de usar el formato AAAA-MM-DD.")

    cargo = input("Cargo del empleado (Ej: Administrador, Cajero, etc.): ").strip()
    if cargo.lower() == 'x': return

    print('1. Contrato Indefinido')
    print('2. Contrato a Plazo Fijo')
    print('X. Cancelar y salir')
    tipo_contrato = input('Seleccione tipo de contrato: ')
    while not (tipo_contrato == '1' or tipo_contrato == '2' or tipo_contrato.lower() == 'x'):
        tipo_contrato = input('!Valor incorrecto¡ -- Tipo de contrato: ')
    if tipo_contrato.lower() == 'x': return

    fecha_termino = None
    es_indefinido = True

    if tipo_contrato == '2':
        es_indefinido = False
        while True:
            fecha_termino = input("Fecha de término de contrato (AAAA-MM-DD) (Presione X para cancelar): ").strip()
            if fecha_termino.lower() == 'x': return
            if VerificarFecha(fecha_termino) and fecha_termino > fecha_inicio:
                break
            print("Fecha inválida o anterior a la fecha de inicio. Intente nuevamente.")

    sql_emp = """
    INSERT INTO empleado (rut, nombre, apellido, id_sucursal) 
    VALUES (%s, %s, %s, %s) RETURNING id_empleado;
    """
    res_emp = Ejecutar(sql_emp, (rut, nombre, apellido, Id), retornar_datos=True)
    if not res_emp:
        print("[ERROR] No se pudo registrar al empleado.")
        return
    id_empleado = res_emp[0][0]

    sql_con = """
    INSERT INTO contrato (id_empleado, fecha_inicio, fecha_termino, es_indefinido, cargo) 
    VALUES (%s, %s, %s, %s, %s) RETURNING id_contrato;
    """
    Ejecutar(sql_con, (id_empleado, fecha_inicio, fecha_termino, es_indefinido, cargo))

    print('\n--- ASIGNACIÓN DE HORARIOS SEMANALES ---')
    sql_hor = """
    INSERT INTO horario (id_empleado, dia_semana, hora_entrada_estimada, hora_salida_estimada) 
    VALUES (%s, %s, %s, %s);
    """
    
    while True:
        dia = input('Día de la semana (Ej: Lunes, Martes / Escriba 0 para finalizar / X para cancelar): ').strip()
        if dia.lower() == 'x': return
        if dia == '0':
            break
            
        entrada = input(f'Hora de entrada estimada para el {dia} (HH:MM:SS): ').strip()
        if entrada.lower() == 'x': return
        
        salida = input(f'Hora de salida estimada para el {dia} (HH:MM:SS): ').strip()
        if salida.lower() == 'x': return

        Ejecutar(sql_hor, (id_empleado, dia, entrada, salida))

    print(f"\n[SISTEMA] Empleado registrado exitosamente con ID {id_empleado} en la sucursal {Id}.")
    

def ConsultarEdicionEmpleado(Id):
    if str(Id).lower() == 'x': return

    while True:
        Comprobacion = input("¿Cómo desea buscar al empleado a editar? (I: Por ID, N: Nombre y apellido, R: Por RUT) (Presione X para cancelar): ").upper()        
        if Comprobacion == 'X': return
        if Comprobacion in ["I", "N", "R"]:
            break
        print("Opción inválida. Ingrese I, N o R.")
            
    resultados = []
    
    if Comprobacion == "I":
        while True:
            id_ingresado = input("Ingrese el ID a buscar (Presione X para cancelar): ")
            if id_ingresado.lower() == 'x': return
            if id_ingresado.isnumeric():
                resultados = BuscarEmpleadoId(Id, int(id_ingresado))
                break
            print("[ERROR] El ID debe ser un número entero.")
            
    elif Comprobacion == "N":
        Nombre = input("Ingrese Nombre a buscar (Presione X para cancelar): ").strip()
        if Nombre.lower() == 'x': return
        Apellido = input("Ingrese Apellido a buscar (Presione X para cancelar): ").strip()
        if Apellido.lower() == 'x': return
        resultados = BuscarEmpleadoNA(Id, Nombre, Apellido)
        
    else:
        while True:
            Rut = input("Ingrese RUT a buscar (Presione X para cancelar): ").strip()
            if Rut.lower() == 'x': return
            if RevisarRut(Rut):
                resultados = BuscarEmpleadoRut(Id, Rut)
                break
            Ver = input("RUT incorrecto!! ¿Desea reintentar? (S o N): ").upper()
            if Ver != "S":
                return

    print("\n--- RESULTADOS DE LA BÚSQUEDA ---")
    if not resultados:
        print("No se encontraron empleados con los criterios ingresados para editar.")
        return resultados
    else:
        for emp in resultados:
            print(f"ID Empleado: {emp[0]} | RUT: {emp[1]} | Nombre: {emp[2]} {emp[3]}")

    print("\n" + "-"*50)
    
    if len(resultados) == 1:
        id_final = resultados[0][0]  
        print(f"[SISTEMA] Empleado único encontrado. Abriendo menú de edición para el ID: {id_final}...")
        EditarEmpleado(id_final)
        
    else:
        id_elegido = input("Se encontraron varios empleados. Ingrese el ID específico que desea editar (Presione X para cancelar): ")
        if id_elegido.lower() == 'x': return
        if id_elegido.isnumeric() and int(id_elegido) in [emp[0] for emp in resultados]:
            EditarEmpleado(int(id_elegido))
        else:
            print("[ERROR] ID inválido o no pertenece a la lista de resultados.")
            
    return resultados


def EditarEmpleado(id_empleado):
    sql_contrato = """
    SELECT c.id_contrato, e.nombre, e.apellido, c.fecha_termino 
    FROM empleado e
    LEFT JOIN contrato c ON e.id_empleado = c.id_empleado
    WHERE e.id_empleado = %s;
    """
    datos_contrato = Ejecutar(sql_contrato, (id_empleado,), retornar_datos=True)
    
    if not datos_contrato:
        print("[ERROR] El ID de empleado no existe en el sistema.")
        return
        
    id_contrato, nombre_emp, apellido_emp, fecha_termino = datos_contrato[0]

    print(f"\n" + "="*50)
    print(f"MENÚ DE EDICIÓN: {nombre_emp.upper()} {apellido_emp.upper()} (ID: {id_empleado})")
    print("="*50)
    print("1. Cambiar Horario")
    print("2. Despedir Empleado (Cerrar Contrato)")
    print("3. Añadir Falla / Amonestación")
    print("X. Cancelar y salir")
    print("-"*50)
    
    opcion = input("Seleccione una opción de edición (1, 2, 3 o X): ").strip().lower()

    if opcion == 'x': return

    if opcion == "1":
        print("\n--- RECONFIGURACIÓN DE JORNADA LABORAL ---")
        horarios_nuevos = []
        dias_validos = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for dia in dias_validos:
            asiste = input(f"¿Trabaja el día {dia}? (S/N) (Presione X para cancelar): ").upper().strip()
            if asiste == 'X': return
            if asiste == "S":
                entrada = input(f"  Hora de entrada para el {dia} (HH:MM): ").strip()
                if entrada.lower() == 'x': return
                salida = input(f"  Hora de salida para el {dia} (HH:MM): ").strip()
                if salida.lower() == 'x': return
                horarios_nuevos.append((dia, f"{entrada}:00", f"{salida}:00"))
                
        Ejecutar("DELETE FROM horario WHERE id_empleado = %s;", (id_empleado,))
        
        sql_ins_horario = """
        INSERT INTO horario (id_empleado, dia_semana, hora_entrada_estimada, hora_salida_estimada) 
        VALUES (%s, %s, %s, %s);
        """
        for dia, ent, sal in horarios_nuevos:
            Ejecutar(sql_ins_horario, (id_empleado, dia, ent, sal))
        print("[SISTEMA] El nuevo horario se ha guardado exitosamente.")

    elif opcion == "2":
        if not id_contrato or fecha_termino is not None:
            print("[ERROR] Este empleado no cuenta con un contrato activo en el sistema.")
            return
            
        confirmar = input(f"¿Confirmar despido y cierre de contrato de {nombre_emp}? (S/N) (Presione X para cancelar): ").upper().strip()
        if confirmar == 'X': return
        if confirmar == "S":
            sql_despido = "UPDATE contrato SET fecha_termino = CURRENT_DATE, es_indefinido = FALSE WHERE id_contrato = %s;"
            Ejecutar(sql_despido, (id_contrato,))
            print("[SISTEMA] El contrato ha sido cerrado con la fecha de hoy. Empleado desvinculado.")

    elif opcion == "3":
        if not id_contrato:
            print("[ERROR] No se pueden asociar fallas a un empleado que no posee contrato.")
            return
            
        detalle_falla = input("Ingrese el detalle o motivo del incumplimiento (Presione X para cancelar): ").strip()
        if detalle_falla.lower() == 'x': return
        
        while True:
            gravedad_input = input("Ingrese la gravedad del asunto (Número entero de 0 a 9) (Presione X para cancelar): ").strip()
            if gravedad_input.lower() == 'x': return
            try:
                gravedad_num = int(gravedad_input)
                if 0 <= gravedad_num <= 9:
                    break
                print("[ERROR] El rango permitido de gravedad es de 0 a 9.")
            except ValueError:
                print("[ERROR] Debe ingresar un número entero válido.")
                
        sql_ins_falla = "INSERT INTO falla (id_contrato, gravedad, fecha, detalle) VALUES (%s, %s, CURRENT_DATE, %s);"
        Ejecutar(sql_ins_falla, (id_contrato, gravedad_num, detalle_falla))
        
        sql_sumar_falla = "UPDATE contrato SET contador_fallas = COALESCE(contador_fallas, 0) + 1 WHERE id_contrato = %s;"
        Ejecutar(sql_sumar_falla, (id_contrato,))
        print("[SISTEMA] Falla añadida y registrada con éxito en el historial de contratación.")
    else:
        print("[ERROR] Opción de menú no válida.")

def BuscarEmpleadoNA(Id, nombre, apellido):
    sql = """
    SELECT id_empleado, rut, nombre, apellido 
    FROM empleado 
    WHERE id_sucursal = %s AND nombre ILIKE %s AND apellido ILIKE %s;
    """
    parametros = (Id, f"%{nombre}%", f"%{apellido}%")
    return Ejecutar(sql, parametros, retornar_datos=True)

def BuscarEmpleadoRut(Id, Rut):
    Rut_Limpio = Rut.replace(".", "").upper()
    
    sql = """
    SELECT id_empleado, rut, nombre, apellido 
    FROM empleado 
    WHERE id_sucursal = %s AND rut = %s;
    """
    parametros = (Id, Rut_Limpio)
    return Ejecutar(sql, parametros, retornar_datos=True)

def MostrarFichaCompletaEmpleado(id_empleado):
    sql_personal = """
    SELECT 
        e.rut, e.nombre, e.apellido, 
        c.cargo, c.fecha_inicio, c.fecha_termino, c.es_indefinido
    FROM empleado e
    LEFT JOIN contrato c ON e.id_empleado = c.id_empleado
    WHERE e.id_empleado = %s;
    """
    datos_personales = Ejecutar(sql_personal, (id_empleado,), retornar_datos=True)
    
    if not datos_personales:
        print("\n[ERROR] No se encontraron datos para el ID de empleado ingresado.")
        return

    rut, nombre, apellido, cargo, f_inicio, f_termino, es_indefinido = datos_personales[0]

    sql_horario = """
    SELECT h.dia_semana, h.hora_entrada_estimada, h.hora_salida_estimada 
    FROM horario h 
    WHERE h.id_empleado = %s
    ORDER BY CASE 
        WHEN h.dia_semana = 'Lunes' THEN 1 
        WHEN h.dia_semana = 'Martes' THEN 2 
        WHEN h.dia_semana = 'Miércoles' THEN 3 
        WHEN h.dia_semana = 'Jueves' THEN 4 
        WHEN h.dia_semana = 'Viernes' THEN 5 
        WHEN h.dia_semana = 'Sábado' THEN 6 
        WHEN h.dia_semana = 'Domingo' THEN 7 
    END;
    """
    horarios = Ejecutar(sql_horario, (id_empleado,), retornar_datos=True)

    sql_fallas = """
    SELECT f.fecha, f.detalle, f.gravedad 
    FROM falla f 
    INNER JOIN contrato c ON f.id_contrato = c.id_contrato
    WHERE c.id_empleado = %s 
    ORDER BY f.fecha DESC;
    """
    fallas = Ejecutar(sql_fallas, (id_empleado,), retornar_datos=True)

    print("\n" + "=" * 60)
    print(f"FICHA TÉCNICA DEL EMPLEADO: {nombre.upper()} {apellido.upper()}")
    print("=" * 60)
    print(f"RUT:              {rut}")
    print(f"Cargo Actual:     {cargo if cargo else 'Sin contrato vigente registrado'}")
    print(f"Fecha de Inicio:  {f_inicio if f_inicio else 'N/A'}")
    
    if cargo is None:
        print("Tipo de Contrato: Sin contrato activo")
    elif es_indefinido:
        print("Tipo de Contrato: Indefinido")
    else:
        print(f"Tipo de Contrato: Plazo Fijo (Fecha de término: {f_termino})")
        
    print("-" * 60)
    print("JORNADA LABORAL Y HORARIOS ASIGNADOS:")
    if not horarios:
        print("  El empleado no registra bloques de horario asignados.")
    else:
        for hor in horarios:
            print(f"  - {hor[0]}: {hor[1]} a {hor[2]}")

    print("-" * 60)
    print(f"HISTORIAL DE INCUMPLIMIENTOS / ANOTACIONES ({len(fallas)}):")
    if not fallas:
        print("  Excelente. El empleado no registra anotaciones en el sistema.")
    else:
        for fal in fallas:
            gravedad_texto = "CRÍTICA" if fal[2] > 5 else "Leve"
            print(f"  - [{fal[0]}] Gravedad: {fal[2]} ({gravedad_texto}) | Detalle: {fal[1]}")
            
    print("=" * 60 + "\n")

def ConsultarDetallesEmpleado(Id):
    if str(Id).lower() == 'x': return

    while True:
        Comprobacion = input("¿Cómo desea buscar? (I: Por ID, N: Nombre y apellido, R: Por RUT) (Presione X para cancelar): ").upper()        
        if Comprobacion == 'X': return
        if Comprobacion in ["I", "N", "R"]:
            break
        print("Opción inválida. Ingrese I, N o R.")
            
    resultados = []
    if Comprobacion == "I":
        while True:
            id_ingresado = input("Ingrese el ID a buscar (Presione X para cancelar): ")
            if id_ingresado.lower() == 'x': return
            if id_ingresado.isnumeric():
                resultados = BuscarEmpleadoId(Id, int(id_ingresado))
                break
            print("[ERROR] El ID debe ser un número entero.")
            
    elif Comprobacion == "N":
        Nombre = input("Ingrese Nombre a buscar (Presione X para cancelar): ").strip()
        if Nombre.lower() == 'x': return
        Apellido = input("Ingrese Apellido a buscar (Presione X para cancelar): ").strip()
        if Apellido.lower() == 'x': return
        resultados = BuscarEmpleadoNA(Id, Nombre, Apellido)
        
    else:
        while True:
            Rut = input("Ingrese RUT a buscar (Presione X para cancelar): ").strip()
            if Rut.lower() == 'x': return
            if RevisarRut(Rut):
                resultados = BuscarEmpleadoRut(Id, Rut)
                break
            Ver = input("RUT incorrecto!! ¿Desea reintentar? (S o N): ").upper()
            if Ver != "S":
                return

    print("\n--- RESULTADOS DE LA BÚSQUEDA ---")
    if not resultados:
        print("No se encontraron empleados con los criterios ingresados.")
        return resultados
    else:
        for emp in resultados:
            print(f"ID Empleado: {emp[0]} | RUT: {emp[1]} | Nombre: {emp[2]} {emp[3]}")

    print("\n" + "-"*50)
    
    if len(resultados) == 1:
        id_final = resultados[0][0]  
        print(f"[SISTEMA] Empleado único encontrado. Cargando ficha del ID: {id_final}...")
        MostrarFichaCompletaEmpleado(id_final)
        
    else:
        id_elegido = input("Se encontraron varios empleados. Ingrese el ID específico para ver su ficha (Presione X para cancelar): ")
        if id_elegido.lower() == 'x': return
        if id_elegido.isnumeric() and int(id_elegido) in [emp[0] for emp in resultados]:
            MostrarFichaCompletaEmpleado(int(id_elegido))
        else:
            print("[ERROR] ID inválido o no pertenece a la lista de resultados.")
            
    return resultados





def Menu():

    CargarDatosSinteticos()
    print(' --##--  Sistema Gestion de Heladerias  --##--\n')
    
    while True:
        print('1. Listar Sucursales')
        print('2. Añadir Sucursal')
        print('3. Hacer Resumenes')
        print('4. Entrar En Sucursal')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ") 
    
        if opcion == '1':
            print ('\n')
            ListarSucursales()
        elif opcion == '2':
            print ('\n')
            AñadirSucursal()
        elif opcion == '3':
            print ('\n')
            MenuResumenes()
        elif opcion == '4':
            Id = input("Introdusca ID (Presione X para cancelar): ")
            if Id.lower() == 'x': continue
            existe = Ejecutar("SELECT id_sucursal FROM sucursal WHERE id_sucursal = %s", (Id,), retornar_datos=True)
            if existe:
                print('\n')
                MenuSucursal(Id)
            else:
                print('  !!Id invalido!!  \n')
        elif opcion.lower() == 'x':
            break
        else:
            print('  !!Opcion no valida!!  \n')





def MenuResumenes():
    print(' --##--  Resumenes de informacion  --##--\n')

    while True:
        print('1. ConsultarVentas')
        print('2. ConsultarGastos')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ") 
    
        if opcion == '1':
            print ('\n')
            ConsultarVentas()
        elif opcion == '2':
            print ('\n')
            ConsultarGastos()
        elif opcion.lower() == 'x':
            print ('\n')
            print(' --##--  Sistema Gestion de Heladerias  --##--\n')
            break
        else:
            print('  !!Opcion no valida!!  \n')



    
def MenuSucursal(Id):
    if str(Id).lower() == 'x': return
    ConsultarSucursal(Id)

    while True:
        print('1. GestionInfrestructura')
        print('2. GestionProductos')
        print('3. GestionEmpleados')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            print ('\n')
            MenuInfrestructura(Id)
        elif opcion == '2':
            print ('\n')
            MenuProductos(Id)
        elif opcion == '3':
            print ('\n')
            MenuEmpleados(Id)
        elif opcion.lower() == 'x':
            print ('\n')
            print(' --##--  Sistema Gestion de Heladerias  --##--\n')
            break
        else:
            print('  !!Opcion no valida!!  \n')




            

def MenuInfrestructura(Id):
    if str(Id).lower() == 'x': return
    print(' --##--  Gestion Infrestructura  --##-- \n')
    
    while True:
        print('1. Añadir Maquina')
        print('2. Editar Maquina')
        print('3. Añadir Caja')
        print('4. Editar Caja')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            print ('\n')
            AñadirMaquina(Id)
        elif opcion == '2':
            print ('\n')
            EditarMaquina()
        elif opcion == '3':
            print ('\n')
            AñadirCaja(Id)
        elif opcion == '4':
            print ('\n')
            EditarCaja(Id)
        elif opcion.lower() == 'x':
            print ('\n')
            ConsultarSucursal(Id)
            break
        else:
            print('  !!Opcion no valida!!  \n')



def MenuProductos(Id):
    if str(Id).lower() == 'x': return
    print(' --##--  Gestion Productos  --##--\n')
    
    while True:
        print('1. Añadir Venta')
        print('2. Eliminar Venta')
        print('-----------------------------')
        print('3. Añadir Lote de Productos')
        print('4. Eliminar Lote')
        print('-----------------------------')
        print('5. Añadir Producto')
        print('6. Modificar Producto')
        print('7. Consultar stock')
        print('-----------------------------')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            print ('\n')
            AñadirVenta(Id)
        elif opcion == '2':
            print ('\n')
            EliminarVenta(Id)
        elif opcion == '3':
            print ('\n')
            AñadirLoteProductos(Id)
        elif opcion == '4':
            print ('\n')
            EliminarLote(Id)
        elif opcion == '5':
            print ('\n')
            AñadirProducto()
        elif opcion == '6':
            print('\n')
            ModificarProducto(Id)
        elif opcion == '7':
            print ('\n')
            ConsultarStock(Id)
        elif opcion.lower() == 'x':
            print ('\n')
            ConsultarSucursal(Id)
            break
        else:
            print('  !!Opcion no valida!!  \n')



            

def MenuEmpleados(Id):
    if str(Id).lower() == 'x': return
    print(' --##--  Gestion Empleados  --##--\n')
    
    while True:
        print('1. Añadir Empleado')
        print('2. Editar Empleado')
        print('3. Consultar Detalles de Empleado')
        print('X. Salir \n')

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            print ('\n')
            AñadirEmpleado(Id)
        elif opcion == '2':
            print ('\n')
            ConsultarEdicionEmpleado(Id)
        elif opcion == '3':
            print ('\n')
            ConsultarDetallesEmpleado(Id)
        elif opcion.lower() == 'x':
            print ('\n')
            ConsultarSucursal(Id)
            break
        else:
            print('  !!Opcion no valida!!  \n')


if __name__ == "__main__":
    Menu()
    # Tester()

def Tester():
    print('\n==================================================')
    print('       INICIANDO TESTER DE NAVEGACIÓN MASIVA      ')
    print('==================================================\n')

    datos_test = {
        "AñadirSucursal": [],
        "IdSucursal": ["1"],
        "ConsultarVentas": [],
        "ConsultarGastos": [],
        "AñadirMaquina": [],
        "EditarMaquina": [],
        "AñadirCaja": [],
        "EditarCaja": [],
        "EliminarVenta": [],
        "AñadirVenta": [],
        "EliminarLote": [],
        "AñadirLoteProductos": [],
        "AñadirProducto": [],
        "ModificarProducto": [],
        "ConsultarStock": [],
        "AñadirEmpleado": [],
        "EditarEmpleado": [],
        "ConsultarDetallesEmpleado": []
    }

    secuencia_base = [
        '1',
        '2', *datos_test["AñadirSucursal"],
        '3', '1', *datos_test["ConsultarVentas"], '2', *datos_test["ConsultarGastos"], 'x',
        '4', *datos_test["IdSucursal"],
            '1', 
                '1', *datos_test["AñadirMaquina"], 
                '2', *datos_test["EditarMaquina"], 
                '3', *datos_test["AñadirCaja"], 
                '4', *datos_test["EditarCaja"], 
                'x',
            '2', 
                '2', *datos_test["EliminarVenta"],
                '1', *datos_test["AñadirVenta"], 
                '4', *datos_test["EliminarLote"],
                '3', *datos_test["AñadirLoteProductos"], 
                '5', *datos_test["AñadirProducto"], 
                '6', *datos_test["ModificarProducto"], 
                '7', *datos_test["ConsultarStock"], 
                'x',
            '3', 
                '1', *datos_test["AñadirEmpleado"], 
                '2', *datos_test["EditarEmpleado"], 
                '3', *datos_test["ConsultarDetallesEmpleado"], 
                'x',
            'x',
    ]

    secuencia_navegacion = secuencia_base + secuencia_base + secuencia_base + ['x']

    it = iter(secuencia_navegacion)
    input_original = __builtins__.input

    def input_simulado(prompt=""):
        try:
            valor = next(it)
            print(f"{prompt}{valor}")
            return valor
        except StopIteration:
            return 'x'

    __builtins__.input = input_simulado

    try:
        Menu()
    finally:
        __builtins__.input = input_original

    print('\n==================================================')
    print('       TEST DE NAVEGACIÓN COMPLETADO CON ÉXITO    ')
    print('==================================================\n')
