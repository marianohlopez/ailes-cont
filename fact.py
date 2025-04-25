import mysql.connector
from datetime import datetime
from openpyxl import Workbook
import yagmail
from dotenv import load_dotenv
import os

# Cargar el archivo .env
load_dotenv()

# --- CONFIGURACIÓN ---
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
MAIL_AUTOR = os.getenv("MAIL_AUTOR")
APP_GMAIL_PASS = os.getenv("APP_GMAIL_PASS")

print("PORT RECIBIDO", DB_PORT)

# --- CONEXIÓN MYSQL ---
conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
)

cursor = conn.cursor()

# --- CONSULTA DE FECHAS ---
cursor.execute(
    "SELECT NroComprobante, cobro_fec_calc, factura_cobro_descrip FROM v_comprobantes")
registros = cursor.fetchall()

hoy = datetime.now()

# --- DATOS PARA EXCEL ---
datos_para_excel = []

for id, fecha_str, descrip in registros:
    if fecha_str != "" and descrip == "PENDIENTE":
        fecha = fecha_str if isinstance(
            fecha_str, datetime) else datetime.strptime(str(fecha_str), '%Y-%m-%d')
        diferencia = (hoy - fecha).days
        if diferencia > 60:
            datos_para_excel.append([id, fecha.date(), diferencia, descrip])

# --- EXPORTAR A EXCEL ---
if datos_para_excel:
    wb = Workbook()
    ws = wb.active
    ws.title = "Alertas"

    # Cabeceras
    ws.append(["ID", "Fecha de última revisión",
              "Días desde la revisión", "Estado"])

    # Datos
    for fila in datos_para_excel:
        ws.append(fila)

    # Ruta de salida
    fecha_actual_str = hoy.strftime('%Y-%m-%d')
    nombre_archivo = f"alerta_fechas_{fecha_actual_str}.xlsx"
    """ ruta_salida = os.path.join(os.getcwd(), nombre_archivo) """

    wb.save(nombre_archivo)

    yag = yagmail.SMTP(MAIL_AUTOR, APP_GMAIL_PASS)

    yag.send(
        to="ml.3012@gmail.com",
        subject="prueba",
        contents="Reporte de deudas",
        attachments=nombre_archivo
    )

    print(f"Excel generado en: {nombre_archivo}")
else:
    print("No hay registros con más de 60 días.")

# --- CIERRE ---
cursor.close()
conn.close()
