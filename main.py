#!/usr/bin/env python

"""Documentación del archivo de la Aplicación principal"""

# Importar módulos
import os
from dotenv import load_dotenv

import openai
from openai import OpenAI

import datosBasicosYSintomas
import moderador
import consultaBaseConocimiento
import asistenteMedico

# Load the environment variables from .env file
load_dotenv()

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")


# Configuración de API Key de OpenAI
client = OpenAI(api_key=openai_api_key)


def analizar_datos(datos_paciente, sintomas, respuestas):
    """Realiza un análisis basado en los datos recopilados."""
    print("\nAnalizando datos...")

    prompt = (
        f"Paciente: {datos_paciente['nombre']}\n"
        f"Edad: {datos_paciente['edad']}\n"
        f"Sexo: {datos_paciente['sexo']}\n"
        f"Peso: {datos_paciente['peso']} kg\n"
        f"Síntomas: {', '.join(sintomas)}\n"
        f"Respuestas adicionales: {respuestas}\n"
        "Proporcione un análisis médico y una recomendación general. Si la certeza del diagnóstico es mayor al 90%, detenga las preguntas."
    )

    try:
        messages = [
            {
                "role": "system",
                "content": "Eres un médico virtual que proporciona diagnósticos y recomendaciones basadas en los datos proporcionados.",
            },
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Ajustado al modelo compatible
            messages=messages,
            temperature=0,
            max_tokens=500,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error al procesar el análisis: {str(e)}"


def main():
    print("################ INICIO PROGRAMA ################\n")

    usoModeradores = False
    usoRag = True
    usoAgente = True

    # Paso 1: Recopilar datos personales del paciente
    datos_paciente = datosBasicosYSintomas.obtener_datos_paciente()

    # Paso 2: Registrar los síntomas
    sintomas = datosBasicosYSintomas.registrar_sintomas()

    # Paso 3: Realizar preguntas relevantes basadas en los síntomas
    respuestas_adicionales = datosBasicosYSintomas.realizar_preguntas_relevantes(
        datos_paciente, sintomas, client
    )

    # Paso 3: Aplica el uso de moderadores
    if(usoModeradores):
        moderador.moderador_generico()

        moderador.moderador_intencion()

    # Paso 3: Se Utiliza llamada a RAG
    if(usoRag):

        base_conocimiento = consultaBaseConocimiento.busqueda_base_conocimiento(client)


    # Paso 3: Se llamada a IA
    respuesta_asistente_medico = asistenteMedico.realizar_recomendacion_medica(client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento)

    print(respuesta_asistente_medico)




if __name__ == "__main__":
    main()
