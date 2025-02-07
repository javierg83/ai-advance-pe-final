#!/usr/bin/env python

"""
Este módulo se encarga de la generación de una orden médica en formato Word,
a partir de la información proporcionada por el usuario y el asistente médico.
"""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def agregar_separador(document):
    """
    Agrega un separador visual (una línea de guiones) al documento.
    """
    parrafo_sep = document.add_paragraph()
    run_sep = parrafo_sep.add_run("-" * 80)
    run_sep.font.size = Pt(10)
    parrafo_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER

def generar_orden_medica(openai_client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento, respuesta_asistente_medico) -> str:
    """
    Genera una orden médica en formato Word a partir de la información proporcionada.
    
    Parámetros:
    ----------
    openai_client : 
        objeto cliente (para futuras integraciones).
    datos_paciente : 
        diccionario con los datos del paciente.
    sintomas : 
        cadena de texto con los síntomas ingresados por el paciente.
    respuestas_adicionales : 
        diccionario o lista de diccionarios con pares pregunta-respuesta.
    base_conocimiento : 
        información o referencia (no se utiliza en este ejemplo).
    respuesta_asistente_medico : _typ_
        diccionario con claves 'analisis', 'diagnostico' y 'recomendacion'.

    Retorna
    -------
    str
        Nombre del archivo generado.
    """
    
    document = Document()

    # Configurar fuente base (ej. Arial 12 pt)
    estilo = document.styles['Normal']
    estilo.font.name = 'Arial'
    estilo.font.size = Pt(12)

    # Título principal
    titulo = document.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_titulo = titulo.add_run("ORDEN MÉDICA")
    run_titulo.bold = True
    run_titulo.font.size = Pt(16)

    document.add_paragraph()  # Línea en blanco

    # Sección: Datos del Paciente
    encabezado_paciente = document.add_paragraph()
    encabezado_paciente.add_run("Datos del Paciente:\n").bold = True
    encabezado_paciente.add_run(f"Nombre: {datos_paciente.get('nombre', '')}\n")
    encabezado_paciente.add_run(f"Edad: {datos_paciente.get('edad', '')}\n")
    encabezado_paciente.add_run(f"Peso: {datos_paciente.get('peso', '')}\n")
    encabezado_paciente.add_run(f"RUT: {datos_paciente.get('rut', '')}\n")

    agregar_separador(document)

    # Sección: Síntomas y Preguntas Adicionales
    parrafo_sintomas = document.add_paragraph()
    parrafo_sintomas.add_run("Síntomas reportados por el paciente:\n").bold = True
    parrafo_sintomas.add_run(sintomas)

    document.add_paragraph()  # Espacio antes de la tabla

    # Crear la tabla para preguntas adicionales
    tabla = document.add_table(rows=1, cols=2)
    tabla.style = 'LightShading-Accent1'
    
    # Encabezados de la tabla
    hdr_cells = tabla.rows[0].cells
    hdr_cells[0].text = 'Pregunta'
    hdr_cells[1].text = 'Respuesta'

    # Agregar cada par pregunta-respuesta según el tipo de dato
    if isinstance(respuestas_adicionales, dict):
        
        for pregunta, respuesta in respuestas_adicionales.items():
            row_cells = tabla.add_row().cells
            row_cells[0].text = pregunta
            row_cells[1].text = respuesta
    elif isinstance(respuestas_adicionales, list):
        for item in respuestas_adicionales:
            pregunta = item.get('pregunta', '')
            respuesta = item.get('respuesta', '')
            
            row_cells = tabla.add_row().cells
            row_cells[0].text = pregunta
            row_cells[1].text = respuesta
    else:
        row_cells = tabla.add_row().cells
        row_cells[0].text = "No se proporcionaron datos válidos."
        row_cells[1].text = ""

    agregar_separador(document)

    # Sección: Datos del Asistente Médico
    parrafo_asistente = document.add_paragraph()
    parrafo_asistente.add_run("Datos generados por el Asistente Médico:\n").bold = True

    # Sub-sección: Análisis de los síntomas
    sub_analisis = document.add_paragraph()
    sub_analisis.add_run("Análisis de los síntomas:\n").bold = True
    sub_analisis.add_run(respuesta_asistente_medico)

    document.add_paragraph()  # Espacio

    # Sub-sección: Posible diagnóstico
    sub_diagnostico = document.add_paragraph()
    sub_diagnostico.add_run("Posible diagnóstico:\n").bold = True
    sub_diagnostico.add_run(respuesta_asistente_medico)

    document.add_paragraph()  # Espacio

    # Sub-sección: Recomendación médica
    sub_recomendacion = document.add_paragraph()
    sub_recomendacion.add_run("Recomendación médica:\n").bold = True
    sub_recomendacion.add_run(respuesta_asistente_medico)

    agregar_separador(document)

    # Guardar el documento
    nombre_archivo = "orden_medica.docx"
    document.save(nombre_archivo)
    print(f"Documento guardado como '{nombre_archivo}'")
    return nombre_archivo


def generar_orden_medica_web(
    openai_client,
    datos_paciente,
    sintomas,
    respuestas_adicionales,
    base_conocimiento,
    respuesta_asistente_medico,
):
    """
    Función para entornos web: genera la orden médica usando la función original y devuelve
    la ruta del archivo generado para que se pueda descargar desde la aplicación web.
    """
    archivo = generar_orden_medica(openai_client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento, respuesta_asistente_medico)
    return archivo


# Ejemplo de llamada para consola (no se ejecuta en modo web)
if __name__ == "__main__":
    # Simulación de datos de entrada para modo escritorio
    openai_client = None  # Se puede pasar None o un objeto de OpenAI si se requiere
    datos_paciente = {
        'nombre': 'Juan Pérez',
        'edad': '35',
        'peso': '80kg',
        'rut': '12.345.678-9'
    }
    sintomas = "El paciente presenta dolor abdominal, fiebre y náuseas."

    # Puedes probar con un diccionario:
    # respuestas_adicionales = {
    #     "¿Ha presentado vómitos?": "Sí, de forma intermitente.",
    #     "¿Cuál es la duración de los síntomas?": "Aproximadamente 3 días."
    # }
    #
    # O con una lista de diccionarios:
    respuestas_adicionales = [
        {'pregunta': 'Claro, aquí tienes cinco preguntas relevantes para obtener más información sobre el dolor abdominal del paciente:', 'respuesta': ''},
        {'pregunta': '1. ¿Desde hace cuánto tiempo ha estado experimentando este dolor en la "guata" y cómo describiría la intensidad del dolor en una escala del 1 al 10?', 'respuesta': '2 dias intensidad 7'},
        {'pregunta': '2. ¿El dolor es constante o intermitente? ¿Hay algún momento del día en que se sienta peor?', 'respuesta': 'constante'},
        {'pregunta': '3. ¿Ha notado algún cambio en sus hábitos intestinales, como diarrea, estreñimiento o presencia de sangre en las heces?', 'respuesta': 'no'},
        {'pregunta': '4. ¿Ha experimentado otros síntomas asociados, como náuseas, vómitos, pérdida de apetito, fiebre o pérdida de peso reciente?', 'respuesta': 'vomitos'},
        {'pregunta': '5. ¿Tiene antecedentes médicos relevantes, como enfermedades gastrointestinales, cirugías previas o condiciones crónicas como diabetes o hipertensión?', 'respuesta': 'no'}
    ]
    
    base_conocimiento = "Base de datos de conocimiento médico."  # No se utiliza en este ejemplo
    respuesta_asistente_medico = {
        'analisis': "Los síntomas sugieren una posible infección gastrointestinal.",
        'diagnostico': "Gastroenteritis aguda.",
        'recomendacion': "Se recomienda reposo, hidratación y, en caso de empeoramiento, acudir a urgencias."
    }

    generar_orden_medica(
        openai_client,
        datos_paciente,
        sintomas,
        respuestas_adicionales,
        base_conocimiento,
        respuesta_asistente_medico,
    )
