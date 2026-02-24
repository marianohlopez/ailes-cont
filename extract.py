def extraer_datos_deudas(cursor):
    query = """
        SELECT c.NroComprobante, c.ImpTotal, c.cbteFch, c.fec_envio_os, c.factura_cobro_descrip, c.mes_anio, 
            o.os_nombre, p.alumno_nombre, p.alumno_apellido, c.factura_obs, e.etiqueta
        FROM v_comprobantes c
        LEFT JOIN v_etiquetas_facturas e ON c.id = e.comprobante_id
        JOIN v_os o ON c.os_id = o.os_id
        JOIN v_prestaciones p ON c.prestacion_id = p.prestacion_id
        WHERE YEAR(cbteFch) IN (2025, 2026)
          AND factura_cobro_descrip = 'PENDIENTE' COLLATE utf8mb4_0900_ai_ci
    """
    cursor.execute(query)
    return cursor.fetchall()

def extraer_datos_deudas_todos(cursor):
    query = """
        SELECT c.NroComprobante, c.ImpTotal, c.cbteFch, c.fec_envio_os, c.factura_cobro_descrip, c.mes_anio, 
            o.os_nombre, p.alumno_nombre, p.alumno_apellido, c.factura_obs, e.etiqueta
        FROM v_comprobantes c
        LEFT JOIN v_etiquetas_facturas e ON c.id = e.comprobante_id
        JOIN v_os o ON c.os_id = o.os_id
        JOIN v_prestaciones p ON c.prestacion_id = p.prestacion_id
        WHERE factura_cobro_descrip = 'PENDIENTE' COLLATE utf8mb4_0900_ai_ci
    """
    cursor.execute(query)
    return cursor.fetchall()

def extraer_datos_cobrados(cursor):
    query = """
        SELECT c.NroComprobante, c.ImpTotal, c.cbteFch, c.fec_envio_os,  c.cobro_fec, c.factura_cobro_descrip, 
            c.mes_anio, o.os_nombre, p.alumno_nombre, p.alumno_apellido, c.factura_obs, e.etiqueta
        FROM v_comprobantes c
        LEFT JOIN v_etiquetas_facturas e ON c.id = e.comprobante_id
        JOIN v_os o ON c.os_id = o.os_id
        JOIN v_prestaciones p ON c.prestacion_id = p.prestacion_id
        WHERE c.fec_envio_os IS NOT NULL
            AND YEAR(cbteFch) IN (2025, 2026)
            AND (
                c.factura_cobro_descrip = 'COBRADA TOTAL' COLLATE utf8mb4_0900_ai_ci OR
                c.factura_cobro_descrip = 'COBRADA PARCIAL' COLLATE utf8mb4_0900_ai_ci
            )
            AND STR_TO_DATE(c.cobro_fec, '%Y-%m-%d') 
                BETWEEN STR_TO_DATE(c.fec_envio_os, '%Y-%m-%d')
                    AND DATE_ADD(STR_TO_DATE(c.fec_envio_os, '%Y-%m-%d'), INTERVAL 60 DAY);
    """
    cursor.execute(query)
    return cursor.fetchall()

def extract_prest_sin_pa(cursor):
  query = """ 
    SELECT 
      p.prestacion_id,
      CONCAT(p.alumno_apellido, ", ",p.alumno_nombre) as alumno_completo,
      DATE_FORMAT(COALESCE(MAX(a.asignpa_pa_fec_baja), a.asignpa_fec1), '%d-%m%-%Y') AS ultima_fecha_sin_pa,
      DATEDIFF(CURDATE(), COALESCE(MAX(a.asignpa_pa_fec_baja), p.prestacion_fec_pase_activo)) AS dias_sin_pa
    FROM 
      v_prestaciones p
    LEFT JOIN 
      v_asignaciones_pa a 
      ON p.prestacion_id = a.asignpa_prest
    WHERE 
      p.prestipo_nombre_corto != 'TERAPIAS'
      AND p.prestacion_pa IS NULL
      AND p.prestacion_estado = 1
      AND p.prestacion_alumno != 522
    GROUP BY 
      p.prestacion_id, p.prestacion_alumno
    HAVING 
      dias_sin_pa > 60
	  ORDER BY dias_sin_pa;
    """
  cursor.execute(query)
  return cursor.fetchall()