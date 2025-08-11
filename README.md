# 📌 Pipeline de Alerta Contable

Este proyecto automatiza la extracción, análisis y envío de reportes sobre facturas con estado "pendiente" emitidas desde una plataforma de gestión administrativa con conexión a una base de datos MySQL. El objetivo es facilitar el seguimiento contable de aquellas facturas que llevan más de 45 días sin ser cobradas, generando alertas para su gestión.

---

### 🧠 Propósito del proyecto

- Automatizar el monitoreo de facturas en estado pendiente.
- Calcular los días transcurridos desde la emisión.
- Filtrar aquellas facturas que superan los 45 días sin cobro.
- Filtrar aquellas facturas que se cobraron dentro de los 60 días.
- Generar un reporte en Excel con información clave (observaciones, etiquetas, obra social, alumno).
- Enviar el reporte automáticamente al sector contable.

<img width="1344" height="544" alt="pipeline-aletacont2" src="https://github.com/user-attachments/assets/78345915-843a-4435-a482-13b63c1095c7" />

El script está pensado para ejecutarse de forma local o automática mediante GitHub Actions, permitiendo su integración en entornos de trabajo sin servidores dedicados.

---

### ⚙️ Tecnologías utilizadas

- **Python 3.10**
- **MySQL** (origen de datos)
- **openpyxl** (generación de archivos Excel)
- **yagmail** (envío de emails con adjunto)
- **python-dotenv** (manejo de credenciales y variables)
- **GitHub Actions** (automatización del flujo)

---

#### 4. Automatización con GitHub Actions

El archivo `main.yml` ejecuta el script los lunes a las 11:00 (hora UTC).

---

### 📊 Resultado del proceso

- Se genera un archivo Excel llamado `reporte_facturas_YYYY-MM-DD.xlsx` que incluye:

  - ID de factura
  - Fecha de emisión
  - Días transcurridos desde la emisión
  - Fecha de envio
  - Fecha de cobro
  - Estado
  - Periodo
  - Obra social correspondiente
  - Nombre del cliente
  - Observaciones
  - Etiquetas

- El archivo se envía automáticamente por email al sector contable.
