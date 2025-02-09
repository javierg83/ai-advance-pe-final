from fpdf import FPDF
import os
import openai
import re  # Para extraer solo números de la respuesta
import math  # Para el cálculo de líneas en celdas
from datetime import datetime  # Para generar la fecha en el nombre del archivo

def obtener_codigo_prestacion(examen_nombre):
    """
    Función que obtiene el código de prestación médica desde la API de OpenAI.
    """
    client = openai.OpenAI()  # Inicializar el cliente
    prompt = (
        f"Dado el siguiente examen médico: '{examen_nombre}', proporciona únicamente el código de prestación de salud en Chile. "
        f"El código es un número y no debe incluir texto adicional."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un asistente especializado en el catálogo de prestaciones de salud en Chile."},
            {"role": "user", "content": prompt}
        ]
    )
    respuesta_texto = response.choices[0].message.content.strip()
    codigo_numerico = re.search(r"\b\d+\b", respuesta_texto)
    if codigo_numerico:
        return codigo_numerico.group(0)
    else:
        return "Código no encontrado"

def generar_orden_medica_pdf(openai_client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento, respuesta_asistente_medico):
    """
    Genera una orden médica en formato PDF utilizando la información del paciente y
    la respuesta del asistente médico. Se espera que 'respuesta_asistente_medico' sea un
    diccionario con las siguientes claves:
      - analisis
      - diagnosticos
      - recomendaciones
      - examenes (lista de diccionarios, cada uno con 'nombre')
      - conclusion
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Agregar logo si existe
    logo_path = os.path.join("static", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=40)
    
    pdf.ln(20)
    pdf.set_font("Arial", style='B', size=18)
    pdf.cell(210, 10, "ORDEN MÉDICA", ln=True, align='C')
    pdf.ln(10)
    
    # Datos del Paciente
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Datos del Paciente:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Nombre: {datos_paciente.get('nombre', '')}", ln=True)
    pdf.cell(0, 8, f"Edad: {datos_paciente.get('edad', '')}", ln=True)
    pdf.cell(0, 8, f"Peso: {datos_paciente.get('peso', '')}", ln=True)
    pdf.cell(0, 8, f"RUT: {datos_paciente.get('rut', '')}", ln=True)
    pdf.ln(5)
    
    # Separador
    pdf.set_draw_color(0, 0, 255)
    pdf.cell(0, 1, "", ln=True, fill=True)
    pdf.ln(5)
    
    # Síntomas reportados
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Síntomas reportados:", ln=True)
    pdf.set_font("Arial", size=12)
    sintomas_texto = "\n".join(sintomas) if isinstance(sintomas, list) else sintomas
    pdf.multi_cell(0, 8, sintomas_texto)
    pdf.ln(5)
    
    # Preguntas adicionales
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(95, 10, "Pregunta", 1, 0, 'C', True)
    pdf.cell(95, 10, "Respuesta", 1, 1, 'C', True)
    pdf.set_font("Arial", size=12)
    
    # Función auxiliar para calcular el número de líneas que ocupará un texto en una celda de ancho 'w'
    def nb_lines(pdf_obj, w, txt):
        # Divide el texto en líneas (por saltos de línea) y calcula cuántas líneas se requerirán
        lines = txt.split("\n")
        total = 0
        for line in lines:
            if not line:
                total += 1
            else:
                total += math.ceil(pdf_obj.get_string_width(line) / w)
        return total

    col_width = 95
    line_height = 8
    for item in respuestas_adicionales:
        pregunta_text = item.get('pregunta', '')
        respuesta_text = item.get('respuesta', '')
        n_lines_pregunta = nb_lines(pdf, col_width, pregunta_text)
        n_lines_respuesta = nb_lines(pdf, col_width, respuesta_text)
        row_lines = max(n_lines_pregunta, n_lines_respuesta)
        # Guardamos la posición inicial
        x_initial = pdf.get_x()
        y_initial = pdf.get_y()
        
        # Dibujar la celda de "Pregunta" con multi_cell para que envuelva el texto
        pdf.multi_cell(col_width, line_height, pregunta_text, border=1)
        y_after_pregunta = pdf.get_y()
        
        # Volver a la misma línea para la celda "Respuesta"
        pdf.set_xy(x_initial + col_width, y_initial)
        pdf.multi_cell(col_width, line_height, respuesta_text, border=1)
        
        # Establecer la posición para la siguiente fila
        y_after_row = max(pdf.get_y(), y_after_pregunta)
        pdf.set_xy(x_initial, y_after_row)
    pdf.ln(5)
    
    # Separador
    pdf.cell(0, 1, "", ln=True, fill=True)
    pdf.ln(5)
    
    # Información del Asistente Médico
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Informe del Asistente Médico:", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, "Análisis de Síntomas y Factores del Paciente:\n" +
                         respuesta_asistente_medico.get('analisis', ''))
    pdf.ln(5)
    pdf.multi_cell(0, 8, "Posibles Diagnósticos:\n" +
                         respuesta_asistente_medico.get('diagnosticos', ''))
    pdf.ln(5)
    pdf.multi_cell(0, 8, "Recomendaciones y Pasos Siguientes:\n" +
                         respuesta_asistente_medico.get('recomendaciones', ''))
    pdf.ln(5)
    pdf.cell(0, 10, "Exámenes o Procedimientos Médicos Sugeridos:", ln=True)
    pdf.ln(2)
    examenes = respuesta_asistente_medico.get('examenes', [])
    if isinstance(examenes, list):
        for examen in examenes:
            codigo = obtener_codigo_prestacion(examen.get('nombre', ''))
            pdf.multi_cell(0, 8, f"{examen.get('nombre', '')} (Código: {codigo})", border=1)
    else:
        pdf.multi_cell(0, 8, examenes)
    pdf.ln(5)
    pdf.multi_cell(0, 8, "Conclusión:\n" +
                         respuesta_asistente_medico.get('conclusion', ''))
    pdf.ln(5)
    
    # Nota de advertencia
    pdf.set_font("Arial", style='I', size=10)
    pdf.multi_cell(0, 8, "Esta evaluación es una orientación médica que no reemplaza el diagnóstico de un médico.")
    pdf.ln(5)
    
    # Página para exámenes (opcional)
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, "ORDEN DE EXÁMENES", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "Exámenes o Procedimientos Médicos Sugeridos:", ln=True)
    pdf.set_font("Arial", size=12)
    if isinstance(examenes, list):
        for examen in examenes:
            codigo = obtener_codigo_prestacion(examen.get('nombre', ''))
            pdf.multi_cell(0, 8, f"{examen.get('nombre', '')} (Código: {codigo})", border=1)
    else:
        pdf.multi_cell(0, 8, examenes)
    pdf.ln(20)
    
    # Firma médica
    pdf.cell(0, 10, "____________________", ln=True, align='C')
    pdf.cell(0, 10, "Firma del Médico", ln=True, align='C')
    
    # Generar el nombre del archivo:
    # - Se extrae el rut y el nombre (eliminando espacios) de datos_paciente
    # - Se añade la constante OM
    # - Se agrega la fecha en formato: yyyymmddhhMMssmmm (año, mes, día, hora, minuto, segundo, milisegundos)
    rut = datos_paciente.get('rut', 'SINRUT')
    nombre = datos_paciente.get('nombre', 'SINNOMBRE').replace(" ", "")
    now = datetime.now()
    fecha_str = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond//1000:03d}"
    nombre_archivo = f"{rut}_{nombre}_OM_{fecha_str}.pdf"
    
    pdf.output(nombre_archivo)
    print(f"Documento guardado como '{nombre_archivo}'")
    return nombre_archivo

def generar_orden_medica_web(openai_client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento, respuesta_asistente_medico):
    return generar_orden_medica_pdf(openai_client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento, respuesta_asistente_medico)

if __name__ == "__main__":
    generar_orden_medica_pdf(
        None,
        {'nombre': 'Juan Pérez', 'edad': '35', 'peso': '80kg', 'rut': '12.345.678-9'},
        ["Dolor abdominal"],
        [
            {'pregunta': '¿Ha presentado fiebre?', 'respuesta': 'Sí, moderada.'},
            {'pregunta': '¿Ha tenido tos?', 'respuesta': 'No.'},
            {'pregunta': '¿Sufre de alguna enfermedad crónica?', 'respuesta': 'No.'},
            {'pregunta': '¿Está tomando algún medicamento?', 'respuesta': 'No.'},
            {'pregunta': '¿Ha viajado recientemente?', 'respuesta': 'No.'}
        ],
        "Base médica",
        {
            'analisis': "Gastroenteritis.",
            'diagnosticos': "Infección leve.",
            'recomendaciones': "Reposo e hidratación.",
            'examenes': [
                {'nombre': 'Hemograma Completo'},
                {'nombre': 'Radiografía de Tórax'}
            ],
            'conclusion': "Se recomienda seguimiento médico en caso de empeoramiento."
        }
    )
