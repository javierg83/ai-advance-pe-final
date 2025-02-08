#!/usr/bin/env python

"""
Este módulo contiene los diferentes moderadores que son utilizados en el flujo.

Funciones disponibles:
- moderador_generico: Se activa revisión con moderador genérico de Open AI.
- moderador_intencion: Moderador que controla que las preguntas estén en el ámbito medico. (REVISAR)
"""

import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from rich import traceback

# Activa traceback para mejorar la depuración de excepciones
traceback.install()

# Load the environment variables from .env file
if load_dotenv(find_dotenv(usecwd=True)):
    print("Archivo '.env' cargado exitosamente.")

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)


def analizar_resultado_moderacion(response):
    true_categories = []
    positive_scores = {}

    # Asumimos que solo hay un resultado en response.results
    result = response.results[0]

    # Obtener categorías que son True
    categories_dict = result.categories.dict()
    for category, value in categories_dict.items():
        if value:
            true_categories.append(category)

    # Obtener categorías con puntuaciones mayores que 0
    category_scores_dict = result.category_scores.dict()
    for category, score in category_scores_dict.items():
        if score > 0:
            positive_scores[category] = score

    return true_categories, positive_scores


def es_intento_danino(response, umbral):
    """
    Determina si el intento es dañino basándose en el resultado de la moderación.

    Parámetros:
    - response: objeto de respuesta de la API de moderación de OpenAI.
    - umbral: valor de umbral para considerar una categoría como positiva.

    Devuelve:
    - Un diccionario con el resultado y las categorías relevantes.
    """
    categorias_daninas = [
        "self_harm",
        "self_harm_intent",
        "self_harm_instructions",
        "self-harm",
        "self-harm/intent",
        "self-harm/instructions",
        "violence",
        "violence_graphic",
        "violence/graphic",
        "harassment",
        "harassment_threatening",
        "harassment/threatening",
        "hate",
        "hate_threatening",
        "hate/threatening",
        "illicit",
        "illicit_behavior",
        "illicit/behavior",
        "sexual_minors",
        "sexual/minors",
    ]

    result = response.results[0]
    category_scores = result.category_scores.dict()
    categorias_positivas = {}

    for categoria in categorias_daninas:
        # Verificar si la categoría está en los scores
        if categoria in category_scores:
            score = category_scores[categoria]
            if score >= umbral:
                categorias_positivas[categoria] = score

    if categorias_positivas:
        return {
            "es_danino": True,
            "categorias_detectadas": categorias_positivas
        }
    else:
        return {
            "es_danino": False,
            "categorias_detectadas": {}
        }


def analisis_moderador_generico(
    client, datos_paciente_json, sintomas, respuestas_adicionales_json
):
    # Construir el mensaje a partir de los datos de entrada
    message = (
        f"Datos del paciente:\n"
        f"- Nombre: {datos_paciente_json.get('nombre', 'Desconocido')}\n"
        f"- Edad: {datos_paciente_json.get('edad', 'No especificado')}\n"
        f"- Sexo: {datos_paciente_json.get('sexo', 'No especificado')}\n"
        f"- Peso: {datos_paciente_json.get('peso', 'No especificado')} kg\n\n"
    )

    message += "Síntomas: " + ", ".join(sintomas) + "\n\n"

    # Si hay respuestas adicionales, se procesan y se agregan al mensaje.
    if isinstance(respuestas_adicionales_json, list) and respuestas_adicionales_json:
        respuestas_str = "; ".join(
            [
                f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
                for r in respuestas_adicionales_json
                if isinstance(r, dict)
            ]
        )
        message += "Respuestas adicionales: " + respuestas_str

    # Imprimir el mensaje generado para verificar su contenido
    # print("Mensaje para moderación:")
    # print(message)

    # Llamada a la API de moderación de OpenAI usando el mensaje generado.
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=message,
    )

    # Procesar la respuesta (según la implementación de tu cliente)
    # print("Respuesta de moderación:")
    # print(response)

    # Modelo de moderaciones OpenaI (Prueba)
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=message,
    )

    # MUESTRA LAS CATEGORÍAS CON VALORES TRUE y FALSE#

    # for result in response.results:
    #    print("Categorías:")
    #    categories_dict = result.categories.dict()
    #    for category, value in categories_dict.items():
    #        print(f"  {category}: {value}")

    #    print("\nPuntuaciones de categorías:")
    #    category_scores_dict = result.category_scores.dict()
    #    for category, score in category_scores_dict.items():
    #        print(f"  {category}: {score}")

    #    print(f"\nMarcado (Flagged): {result.flagged}")

    #    for category, score in category_scores_dict.items():
    #        print(f"  {category}: {score}")

    #    print(f"\nMarcado (Flagged): {result.flagged}")

    # Suponiendo que ya tienes el objeto 'response' de la API de moderación
    true_categories, positive_scores = analizar_resultado_moderacion(response)

    # print("Categorías con valor True:")
    # for category in true_categories:
    #    print(f"- {category}")

    # print("\nCategorías con puntuaciones mayores que 0:")
    # for category, score in positive_scores.items():
    #    print(f"- {category}: {score}")

    # Supongamos que ya tienes el objeto 'response' de la API de moderación
    resultado = es_intento_danino(response, umbral=0.0000005)

    if resultado["es_danino"]:
        dano = 1
    #    print("El intento es dañino: ", dano)
    #    print("Categorías detectadas:")
    #    for categoria, puntaje in resultado['categorias_detectadas'].items():
    #        print(f"- {categoria}: {puntaje}")
    else:
        dano = 0
    #    print("El intento no es dañino: ", dano)

    return true_categories


def moderacion_pasada_web(
    client, datos_paciente_json, sintomas, respuestas_adicionales_json
):
    """
    Realiza la revisión de moderación utilizando la función analisis_moderador_generico.
    Devuelve una tupla (paso_moderacion, true_categories):
      - paso_moderacion: True si no se detectaron categorías problemáticas (moderación aprobada),
                         False en caso contrario.
      - true_categories: Lista de categorías problemáticas detectadas (vacía si no hay ninguna).
    """
    true_categories = analisis_moderador_generico(
        client, datos_paciente_json, sintomas, respuestas_adicionales_json
    )
    if true_categories:
        return False, true_categories
    else:
        return True, []
