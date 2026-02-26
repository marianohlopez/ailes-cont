from datetime import datetime
from db import conectar_db
from extract import (extract_prest_sin_pa, extraer_datos_cobrados, extraer_datos_deudas, 
                     extraer_datos_deudas_todos)
from transform import enviar_correo, exportar_excel, transformar_datos

def main():
    hoy = datetime.now()

    conn = conectar_db()
    cursor = conn.cursor()

    registros_alertas = extraer_datos_deudas(cursor)
    print(f"Registros de alerta extraídos: {len(registros_alertas)}")

    datos_alertas = transformar_datos(registros_alertas, hoy, '')

    registros_alertas_todos = extraer_datos_deudas_todos(cursor)
    print(f"Registros de alerta (todos) extraídos: {len(registros_alertas_todos)}")

    datos_alertas_todos = transformar_datos(registros_alertas_todos, hoy, 'todas')

    registros_cobrados = extraer_datos_cobrados(cursor)
    print(f"Registros de cobradas recientes: {len(registros_cobrados)}")

    prest_sin_pa = extract_prest_sin_pa(cursor)
    print(f"Registros de prestaciones sin pa > 60 días: {len(prest_sin_pa)}")

    if datos_alertas or registros_cobrados:
        archivo_excel = exportar_excel(datos_alertas, datos_alertas_todos, registros_cobrados, 
                                       prest_sin_pa, hoy)
        enviar_correo(archivo_excel)
    else:
        print("No hay registros relevantes para exportar.")

    cursor.close()
    conn.close()
    print("Conexión cerrada.")

if __name__ == "__main__":
    main()
