#!/usr/bin/env python

"""Documentación del archivo del Asistente Médico"""

# Plantilla del prompt
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

    Instrucciones para la respuesta:
    1. Proporciona un análisis detallado de los síntomas y factores del paciente.
    2. Enuncia posibles diagnósticos.
    3. Ofrece recomendaciones o sugerencias de pasos siguientes (consultas, pruebas, medidas básicas de cuidado), indicando medicamentos específicos si fuera necesario.
    4. Si la certeza del diagnóstico es mayor al 80%, concluye la sesión sin más preguntas.
    
    Nota: La información proporcionada es solo para fines de orientación y no debe considerarse como consejo médico definitivo.
"""

def realizar_recomendacion_medica(client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento):
    # Creación del prompt con los datos de entrada entregados por el paciente
    prompt = prompt_recomendacion_medica.format(
        nombre=datos_paciente['nombre'],
        edad=datos_paciente['edad'],
        sexo=datos_paciente['sexo'],
        peso=datos_paciente['peso'],
        sintomas=', '.join(sintomas),
        respuestas='; '.join(respuestas_adicionales)
    )


    # Mensajes que se envían al modelo
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
    except:
        answer = 'Lo siento, no pude entender tu pregunta. ¿Podrías reformularla por favor?'
    
    return answer
