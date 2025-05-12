import mysql.connector
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
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
MAIL_DESTINO = os.getenv("MAIL_DESTINO")

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
    "SELECT c.NroComprobante, c.cbteFch, c.factura_cobro_descrip, o.os_nombre, p.alumno_nombre, p.alumno_apellido, c.factura_obs" +
    " FROM v_comprobantes c JOIN v_os o ON c.os_id = o.os_id " +
    " JOIN v_prestaciones p ON c.prestacion_id = p.prestacion_id" +
    " WHERE YEAR(cbteFch) = 2025 AND factura_cobro_descrip = 'PENDIENTE' COLLATE utf8mb4_0900_ai_ci")
registros = cursor.fetchall()

hoy = datetime.now()

# --- DATOS PARA EXCEL ---
datos_para_excel = []

for id, fecha_str, descrip, oSocial, alum_nombre, alum_apellido, obs in registros:
    if fecha_str != "":
        alum_completo = f"{alum_apellido}, {alum_nombre}"
        fecha = fecha_str if isinstance(
            fecha_str, datetime) else datetime.strptime(str(fecha_str), '%Y-%m-%d')
        diferencia = (hoy - fecha).days
        if diferencia > 45:
            datos_para_excel.append(
                [id, fecha.date(), diferencia, descrip, oSocial, alum_completo, obs])

# --- EXPORTAR A EXCEL ---
if datos_para_excel:
    wb = Workbook()
    ws = wb.active
    ws.title = "Alertas"

    # Cabeceras
    ws.append(["ID_Factura", "Fecha de fact.",
              "Días desde fecha de fact.", "Estado", "OS", "Alumno", "Observaciones"])

    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Datos
    for fila in datos_para_excel:
        ws.append(fila)

    # Ruta de salida
    fecha_actual_str = hoy.strftime('%Y-%m-%d')
    nombre_archivo = f"alerta_fechas_{fecha_actual_str}.xlsx"

    wb.save(nombre_archivo)

    yag = yagmail.SMTP(MAIL_AUTOR, APP_GMAIL_PASS)

    yag.send(
        to=MAIL_DESTINO,
        subject="Reporte de Facturas emitidas-Cobros",
        contents="Buenos días, se adjunta el reporte de deudas. ¡Saludos!",
        attachments=nombre_archivo
    )

    print(f"Excel generado en: {nombre_archivo}")
else:
    print("No hay registros con más de 60 días.")

# --- CIERRE ---
cursor.close()
conn.close()
