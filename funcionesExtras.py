import re
# ----------------------------
# Función para parsear la respuesta del asistente médico
# ----------------------------
def parse_respuesta_asistente_medico(texto: str) -> dict:
    """
    Parsea el texto recibido del asistente médico en cinco secciones:
      - Análisis de Síntomas y Factores del Paciente
      - Posibles Diagnósticos
      - Recomendaciones y Pasos Siguientes
      - Exámenes o Procedimientos Médicos Sugeridos
      - Conclusión

    Retorna un diccionario con las claves:
      - analisis
      - diagnosticos
      - recomendaciones
      - examenes (lista de diccionarios, cada uno con la clave 'nombre')
      - conclusion
    """
    sections = {
        "Análisis de Síntomas y Factores del Paciente": "",
        "Posibles Diagnósticos": "",
        "Recomendaciones y Pasos Siguientes": "",
        "Exámenes o Procedimientos Médicos Sugeridos": "",
        "Conclusión": ""
    }

    current_key = None
    for line in texto.splitlines():
        line = line.strip()
        if line.startswith("###"):
            header = line.strip("# ").strip()
            # Verifica si el header coincide con alguna de las secciones definidas
            for key in sections.keys():
                if header.lower().startswith(key.lower()):
                    current_key = key
                    break
        else:
            if current_key:
                sections[current_key] += line + "\n"

    # Limpiar espacios adicionales
    for key in sections:
        sections[key] = sections[key].strip()

    # Procesar la sección de exámenes: se espera que esté en formato de lista numerada
    examenes_text = sections["Exámenes o Procedimientos Médicos Sugeridos"]
    examenes_list = []
    for line in examenes_text.splitlines():
        line = line.strip()
        match = re.match(r"^\d+\.\s*(.*)", line)
        if match:
            examenes_list.append({"nombre": match.group(1).strip()})
    if examenes_list:
        sections["Exámenes o Procedimientos Médicos Sugeridos"] = examenes_list

    return {
        "analisis": sections["Análisis de Síntomas y Factores del Paciente"],
        "diagnosticos": sections["Posibles Diagnósticos"],
        "recomendaciones": sections["Recomendaciones y Pasos Siguientes"],
        "examenes": sections["Exámenes o Procedimientos Médicos Sugeridos"],
        "conclusion": sections["Conclusión"]
    }