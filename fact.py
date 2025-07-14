import mysql.connector
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
import yagmail
from dotenv import load_dotenv
import os

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
MAIL_AUTOR = os.getenv("MAIL_AUTOR")
APP_GMAIL_PASS = os.getenv("APP_GMAIL_PASS")
MAIL_DESTINO = os.getenv("MAIL_DESTINO")


def conectar_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print("Conexión a la base de datos exitosa.")
        return conn
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        exit(1)


def extraer_datos(cursor):
    query = """
        SELECT c.NroComprobante, c.cbteFch, c.factura_cobro_descrip, c.mes_anio, o.os_nombre,
               p.alumno_nombre, p.alumno_apellido, c.factura_obs, e.etiqueta
        FROM v_comprobantes c
        LEFT JOIN v_etiquetas_facturas e ON c.id = e.comprobante_id
        JOIN v_os o ON c.os_id = o.os_id
        JOIN v_prestaciones p ON c.prestacion_id = p.prestacion_id
        WHERE YEAR(cbteFch) = 2025
          AND factura_cobro_descrip = 'PENDIENTE' COLLATE utf8mb4_0900_ai_ci
    """
    cursor.execute(query)
    return cursor.fetchall()


def transformar_datos(registros, hoy):
    resultados = []
    for id, fecha_str, descrip, periodo, oSocial, alum_nombre, alum_apellido, obs, etiqueta in registros:
        if fecha_str:
            try:
                fecha = fecha_str if isinstance(fecha_str, datetime) else datetime.strptime(str(fecha_str), '%Y-%m-%d')
                dias = (hoy - fecha).days
                if dias > 45:
                    resultados.append([
                        id,
                        fecha.date(),
                        dias,
                        descrip,
                        periodo,
                        oSocial,
                        f"{alum_apellido}, {alum_nombre}",
                        obs,
                        etiqueta
                    ])
            except Exception as e:
                print(f"Error procesando la fecha {fecha_str} para ID {id}: {e}")
    return resultados


def exportar_excel(datos, hoy):
    wb = Workbook()
    ws = wb.active
    ws.title = "Alertas"

    headers = ["ID_Factura", "Fecha de fact.", "Días desde fecha de fact.", "Estado", "Periodo",
               "OS", "Alumno", "Observaciones", "Etiqueta"]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for fila in datos:
        ws.append(fila)

    nombre_archivo = f"alerta_fechas_{hoy.strftime('%Y-%m-%d')}.xlsx"
    wb.save(nombre_archivo)
    print(f"Archivo Excel generado: {nombre_archivo}")
    return nombre_archivo


def enviar_correo(nombre_archivo):
    try:
        yag = yagmail.SMTP(MAIL_AUTOR, APP_GMAIL_PASS)
        yag.send(
            to=MAIL_DESTINO,
            subject="Reporte de Facturas emitidas - Cobros",
            contents="Buenos días, se adjunta el reporte de deudas. ¡Saludos!",
            attachments=nombre_archivo
        )
        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)


def main():
    hoy = datetime.now()

    conn = conectar_db()
    cursor = conn.cursor()

    registros = extraer_datos(cursor)
    print(f"Registros extraídos: {len(registros)}")

    datos_filtrados = transformar_datos(registros, hoy)

    if datos_filtrados:
        archivo_excel = exportar_excel(datos_filtrados, hoy)
        enviar_correo(archivo_excel)
    else:
        print("No hay registros con más de 45 días.")

    cursor.close()
    conn.close()
    print("Conexión cerrada.")


if __name__ == "__main__":
    main()
