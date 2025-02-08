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


def evaluar_coherencia_medica(datos_paciente_json, sintomas, respuestas_adicionales_json):
    """
    Evalúa la coherencia médica de la información del paciente.
    Retorna un porcentaje de coherencia basado en la lógica de un experto médico.
    """
    mensaje_evaluacion = (
        f"Evaluar la coherencia médica de la siguiente información del paciente en atención primaria: \n"
        f"- Edad: {datos_paciente_json.get('edad', 'No especificado')} años\n"
        f"- Sexo: {datos_paciente_json.get('sexo', 'No especificado')}\n"
        f"- Peso: {datos_paciente_json.get('peso', 'No especificado')} kg\n"
        f"- Síntomas: {', '.join(sintomas)}\n"
    )
    
    if respuestas_adicionales_json:
        mensaje_evaluacion += "- Respuestas adicionales:\n"
        for r in respuestas_adicionales_json:
            mensaje_evaluacion += f"  - {r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}\n"
    
    mensaje_evaluacion += "\nDevuelve solo un número entre 0 y 100 indicando el porcentaje de coherencia médica."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un médico experto en atención primaria evaluando información médica."},
            {"role": "user", "content": mensaje_evaluacion}
        ]
    )
    
    try:
        coherencia = float(response.choices[0].message.content.strip())
    except ValueError:
        coherencia = 0  # En caso de error, asumimos que no es coherente
    
    print(f"Porcentaje de coherencia médica determinado: {coherencia}%")
    return coherencia

def analisis_moderador_generico(client, datos_paciente_json, sintomas, respuestas_adicionales_json):
    """
    Realiza la moderación genérica de OpenAI.
    """
    message = (
        f"Datos del paciente:\n"
        f"- Nombre: {datos_paciente_json.get('nombre', 'Desconocido')}\n"
        f"- Edad: {datos_paciente_json.get('edad', 'No especificado')}\n"
        f"- Sexo: {datos_paciente_json.get('sexo', 'No especificado')}\n"
        f"- Peso: {datos_paciente_json.get('peso', 'No especificado')} kg\n\n"
        f"Síntomas: {', '.join(sintomas)}\n\n"
    )
    
    if respuestas_adicionales_json:
        respuestas_str = "; ".join(
            [
                f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
                for r in respuestas_adicionales_json if isinstance(r, dict)
            ]
        )
        message += "Respuestas adicionales: " + respuestas_str
    
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=message,
    )
    
    result = response.results[0]
    true_categories = [category for category, value in result.categories.dict().items() if value]
    
    return true_categories

def moderacion_pasada_web(client, datos_paciente_json, sintomas, respuestas_adicionales_json):
    """
    Realiza la revisión de moderación combinando el moderador genérico y el de intenciones médicas.
    Devuelve una tupla (paso_moderacion, true_categories).
    """
    true_categories = analisis_moderador_generico(client, datos_paciente_json, sintomas, respuestas_adicionales_json)
    
    if true_categories:
        return False, true_categories
    
    coherencia = evaluar_coherencia_medica(datos_paciente_json, sintomas, respuestas_adicionales_json)
    if coherencia >= 70:
        return True, []  # Se considera coherente
    else:
        return False, ["Incoherencia Médica: Soy un especialista médico y no puedo orientarte sin información consistente."]

# Datos de prueba para validación
if __name__ == "__main__":
    datos_paciente_json = {"nombre": "Juan Perez", "edad": 35, "sexo": "Masculino", "peso": 70}
    sintomas = ["fiebre", "mocos", "dolor de cabeza"]
    respuestas_adicionales_json = [
        {"pregunta": "¿Has viajado recientemente?", "respuesta": "No"},
        {"pregunta": "¿Tienes enfermedades crónicas?", "respuesta": "No"}
    ]
    
    resultado, categorias = moderacion_pasada_web(client, datos_paciente_json, sintomas, respuestas_adicionales_json)
    print("Resultado de moderación:", "Aprobado" if resultado else "Rechazado")
    if categorias:
        print("Categorías detectadas:", categorias)