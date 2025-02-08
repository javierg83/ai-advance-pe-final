#!/usr/bin/env python

"""Documentación del archivo del Supervisor Evaluador Medico"""

# Librerías a importar
import logging
import json  # Si los datos provienen de un JSON

# Configuración del logging para depuración
logging.basicConfig(level=logging.INFO)


# Plantilla del prompt con inclusión de la base de conocimiento
prompt_supervisor_medico = """
Actúas como un médico con más de 30 años de experiencia y experto en diagnóstico clínico.
Tu objetivo es evaluar antecedentes obtenidos de ejecuciones previas, consolidarlos y determinar si los datos permiten alcanzar al menos un 70%, de certeza en el diagnóstico.
En caso contrario, debes recomendar acudir a un médico para una evaluación presencial.

### **Paciente:**
- **Nombre**: {nombre}
- **Edad**: {edad}
- **Sexo**: {sexo}
- **Peso**: {peso} kg
- **Síntomas**: {sintomas}
- **Respuestas adicionales**: {respuestas}
- **Base de conocimiento**: {base_conocimiento}
- **Recomendacion**:{recomendacion_ia}

### **Instrucciones para la respuesta:**
1. **Análisis detallado**: Evalúa síntomas, antecedentes y factores de riesgo.
2. **Correlación clínica**: Determina la relación entre síntomas y posibles diagnósticos.
3. **Evaluación de certeza**:
   - Si la certeza es ≥ 70%, proporciona diagnóstico, tratamiento y órdenes clínicas.
   - Si la certeza es < 70%, recomienda acudir a consulta presencial.

### **Formato de respuesta JSON:**
1. **Nivel de certeza (%)**
2. **Síntesis de antecedentes**
3. **Diagnóstico o recomendación de acudir al médico**
4. **Recomendaciones adicionales (si aplica)**

Nota: La información proporcionada es solo de orientación y no sustituye una consulta médica presencial.
"""

def revision_recomendacion_medica(client, datos_paciente_json, sintomas, respuestas_adicionales_json, base_conocimiento, respuesta_asistente_medico_json):
    """Evalúa la recomendación médica utilizando los datos y respuestas proporcionadas previamente y genera la respuesta final"""
    print("################ EVALUACION SUPERVISOR MEDICO################\n")
    
    # Convertir los datos a diccionarios (si ya vienen en memoria, se asume que es un dict)
    datos_paciente = datos_paciente_json
    respuestas_adicionales = respuestas_adicionales_json
    respuesta_asistente_medico=respuesta_asistente_medico_json

    # Asegurarse de que `sintomas` contenga solo cadenas de texto
    sintomas = [str(sintoma) for sintoma in sintomas]

    # Procesar respuestas adicionales si es una lista de diccionarios
    if isinstance(respuestas_adicionales, list) and respuestas_adicionales:
        lista_respuestas = [
            f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
            for r in respuestas_adicionales if isinstance(r, dict)
        ]
        respuestas_texto = '; '.join(lista_respuestas)
    else:
        respuestas_texto = ''

    # Asegurarse de que base_conocimiento sea una cadena
    base_conocimiento_texto = str(base_conocimiento) if base_conocimiento is not None else ''

    # Crear el prompt utilizando los datos del paciente, respuestas adicionales y base de conocimiento
    prompt = prompt_supervisor_medico.format(
        nombre=datos_paciente.get('nombre', 'Desconocido'),
        edad=datos_paciente.get('edad', 'No especificado'),
        sexo=datos_paciente.get('sexo', 'No especificado'),
        peso=datos_paciente.get('peso', 'No especificado'),
        sintomas=', '.join(sintomas),
        respuestas=respuestas_texto,
        base_conocimiento=base_conocimiento_texto,
        recomendacion_ia=respuesta_asistente_medico if respuesta_asistente_medico else "No se genero una Recomendacion."
    )

    print("Prompt generado:")
    print(prompt)
    
    # Preparar los mensajes para enviar al modelo
    messages = [{"role": "system", "content": prompt}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    try:
        answer = reply
    except Exception:
        answer = 'Lo siento, no pude entender tu pregunta. ¿Podrías reformularla por favor?'
    
    return answer