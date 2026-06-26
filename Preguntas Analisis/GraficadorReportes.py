import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# -------------------------------
# Codigo encargado de generar los graficos (Generado por IA)
# -------------------------------




# Configuración estética global de los gráficos
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.titlesize': 16
})

# Crear la carpeta de destino para las imágenes
CARPETA_INPUT = "reportes"
CARPETA_OUTPUT = "reportes_imagenes"
os.makedirs(CARPETA_OUTPUT, exist_ok=True)

print("=== Iniciando Generación de Gráficos Analíticos ===\n")

# -------------------------------------------------------------------------
# GRAFICO 1: Beneficio Neto por Sucursal
# -------------------------------------------------------------------------
archivo_1 = os.path.join(CARPETA_INPUT, "1.csv")
if os.path.exists(archivo_1):
    df1 = pd.read_csv(archivo_1)
    
    plt.figure(figsize=(10, 6))
    # Creamos un gráfico de barras comparando Ingresos vs Beneficio Neto
    df_melted = df1.melt(id_vars="ciudad", value_vars=["total_ventas", "beneficio_neto"], 
                         var_name="Métrica", value_name="Monto ($)")
    
    sns.barplot(data=df_melted, x="ciudad", y="Monto ($)", hue="Métrica", palette="Blues_r")
    plt.title("Rendimiento Financiero Histórico por Sucursal\n(Ventas Totales vs Beneficio Neto)")
    plt.xlabel("Sucursal (Ciudad)")
    plt.ylabel("Monto en Pesos ($)")
    plt.tight_layout()
    
    plt.savefig(os.path.join(CARPETA_OUTPUT, "1.png"), dpi=150)
    plt.close()
    print("[✓] Gráfico 1 generado: Beneficio Neto por Sucursal (1.png)")

# -------------------------------------------------------------------------
# GRAFICO 2: Preferencia de Sabores/Productos según el Sexo
# -------------------------------------------------------------------------
archivo_2 = os.path.join(CARPETA_INPUT, "2.csv")
if os.path.exists(archivo_2):
    df2 = pd.read_csv(archivo_2)
    
    # Para no saturar el gráfico, filtramos solo los 8 productos más vendidos en total
    top_productos = df2.groupby("producto")["ingresos_totales"].sum().nlargest(8).index
    df2_filtrado = df2[df2["producto"].isin(top_productos)]
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df2_filtrado, x="producto", y="ingresos_totales", hue="sexo", palette="pastel")
    plt.title("Top Sabores/Productos más Rentables según el Sexo del Cliente")
    plt.xlabel("Producto")
    plt.ylabel("Ingresos Totales ($)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    
    plt.savefig(os.path.join(CARPETA_OUTPUT, "2.png"), dpi=150)
    plt.close()
    print("[✓] Gráfico 2 generado: Preferencia de Sabores por Sexo (2.png)")

# -------------------------------------------------------------------------
# GRAFICO 3: Ventas por Hora Exacta (Línea de Tiempo)
# -------------------------------------------------------------------------
archivo_3 = os.path.join(CARPETA_INPUT, "3.csv")
if os.path.exists(archivo_3):
    df3 = pd.read_csv(archivo_3).sort_values(by="hora_exacta")
    
    plt.figure(figsize=(11, 5))
    # Un gráfico de línea es perfecto para ver tendencias de tiempo (horas pico)
    sns.lineplot(data=df3, x="hora_exacta", y="monto_total_ventas", marker="o", color="coral", linewidth=2.5)
    plt.title("Curva de Demanda Histórica: Monto de Ventas por Hora del Día")
    plt.xlabel("Hora del Día (Formato 24h)")
    plt.ylabel("Monto Total Vendido ($)")
    plt.xticks(df3["hora_exacta"].unique())
    plt.tight_layout()
    
    plt.savefig(os.path.join(CARPETA_OUTPUT, "3.png"), dpi=150)
    plt.close()
    print("[✓] Gráfico 3 generado: Ventas por Bloque Horario (3.png)")

# -------------------------------------------------------------------------
# GRAFICO 4: Desempeño Comercial del Empleado (Ventas Totales)
# -------------------------------------------------------------------------
archivo_4 = os.path.join(CARPETA_INPUT, "4.csv")
if os.path.exists(archivo_4):
    df4 = pd.read_csv(archivo_4)
    
    plt.figure(figsize=(10, 6))
    # Gráfico de barras horizontal para leer cómodamente los nombres de los empleados
    sns.barplot(data=df4.head(10), x="total_vendido", y="empleado", hue="cargo", dodge=False, palette="viridis")
    plt.title("Ranking de Empleados por Monto Total de Ventas\n(Top 10)")
    plt.xlabel("Monto Total Vendido ($)")
    plt.ylabel("Empleado")
    plt.tight_layout()
    
    plt.savefig(os.path.join(CARPETA_OUTPUT, "4.png"), dpi=150)
    plt.close()
    print("[✓] Gráfico 4 generado: Desempeño Comercial de Empleados (4.png)")

# -------------------------------------------------------------------------
# GRAFICO 5: Gasto Histórico en Suministros por Sucursal y Producto
# -------------------------------------------------------------------------
archivo_5 = os.path.join(CARPETA_INPUT, "5.csv")
if os.path.exists(archivo_5):
    df5 = pd.read_csv(archivo_5)
    
    plt.figure(figsize=(12, 6))
    # Mostramos qué productos le cuestan más abastecer a cada ciudad
    sns.barplot(data=df5, x="ciudad", y="costo_total_suministro", hue="producto", palette="Set2")
    plt.title("Distribución del Gasto en Abastecimiento de Lotes por Sucursal")
    plt.xlabel("Sucursal")
    plt.ylabel("Costo de Suministros ($)")
    plt.legend(title="Producto", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig(os.path.join(CARPETA_OUTPUT, "5.png"), dpi=150)
    plt.close()
    print("[✓] Gráfico 5 generado: Gasto Histórico en Suministros (5.png)")

print("\n=== ¡Proceso Finalizado! Revisa la carpeta 'reportes_imagenes' ===")
