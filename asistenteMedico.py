#!/usr/bin/env python

"""Documentación del archivo del Asistente Médico"""

# Librerías a importar


# Plantilla del prompt con inclusión de la base de conocimiento
prompt_recomendacion_medica = """
Actúa como un médico virtual con experiencia clínica en diagnóstico general.
Tu objetivo es analizar la información del paciente y proporcionar posibles 
diagnósticos y recomendaciones.
Sé claro, organizado y conciso.

Paciente:
- Nombre: {nombre}
- Edad: {edad}
- Sexo: {sexo}
- Peso: {peso} kg
- Síntomas: {sintomas}
- Respuestas adicionales: {respuestas}
- Base de conocimiento: {base_conocimiento}

Instrucciones para la respuesta:
1. Proporciona un análisis detallado de los síntomas y factores del paciente.
2. Enuncia posibles diagnósticos.
3. Ofrece recomendaciones o sugerencias de pasos siguientes (consultas, pruebas, medidas básicas de cuidado), indicando medicamentos específicos si fuera necesario.
4. Genera una lista de examenes o procedimientos medicos sugeridos que ayudar a confirmar el diagnostico.
5. Si la certeza del diagnóstico es mayor al 80%, concluye la sesión sin más preguntas.

Nota: La información proporcionada es solo para fines de orientación y no debe considerarse como consejo médico definitivo.
"""

def realizar_recomendacion_medica(client, datos_paciente_json, respuestas_adicionales_json, sintomas, base_conocimiento):
    """Genera una recomendación médica utilizando los datos y respuestas proporcionadas."""
    
    # Convertir los datos a diccionarios (si ya vienen en memoria, se asume que es un dict)
    datos_paciente = datos_paciente_json
    respuestas_adicionales = respuestas_adicionales_json

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
    prompt = prompt_recomendacion_medica.format(
        nombre=datos_paciente.get('nombre', 'Desconocido'),
        edad=datos_paciente.get('edad', 'No especificado'),
        sexo=datos_paciente.get('sexo', 'No especificado'),
        peso=datos_paciente.get('peso', 'No especificado'),
        sintomas=', '.join(sintomas),
        respuestas=respuestas_texto,
        base_conocimiento=base_conocimiento_texto
    )

    #print("Prompt generado:")
    #print(prompt)
    
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



def realizar_recomendacion_medica_web(client, datos_paciente_json, sintomas, respuestas_adicionales_json, base_conocimiento):
    """
    Genera una recomendación médica utilizando los datos del paciente, las respuestas adicionales,
    los síntomas y la base de conocimiento. Devuelve la respuesta generada que se mostrará como conclusión.
    """
    # Se reutiliza la lógica original, adaptando el prompt para el entorno web.
    # Asegurarse de que 'sintomas' sea una lista de strings.
    sintomas = [str(s) for s in sintomas]

    if isinstance(respuestas_adicionales_json, list) and respuestas_adicionales_json:
        lista_respuestas = [
            f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
            for r in respuestas_adicionales_json if isinstance(r, dict)
        ]
        respuestas_texto = '; '.join(lista_respuestas)
    else:
        respuestas_texto = ''

    base_conocimiento_texto = str(base_conocimiento) if base_conocimiento is not None else ''

    prompt = prompt_recomendacion_medica.format(
        nombre=datos_paciente_json.get('nombre', 'Desconocido'),
        edad=datos_paciente_json.get('edad', 'No especificado'),
        sexo=datos_paciente_json.get('sexo', 'No especificado'),
        peso=datos_paciente_json.get('peso', 'No especificado'),
        sintomas=', '.join(sintomas),
        respuestas=respuestas_texto,
        base_conocimiento=base_conocimiento_texto
    )

    # Para depuración, se puede imprimir o loguear el prompt.
    # Aquí se usa print() para fines ilustrativos.
    #print("Prompt para recomendación médica (web):")
    #print(prompt)
    
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
    return reply