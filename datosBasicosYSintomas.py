#!/usr/bin/env python

"""
Este módulo contiene funciones para la obtención de los datos personales del paciente y los síntomas relacionados con su enfermedad.

Funciones disponibles:
- obtener_datos_paciente: Solicita al cliente los datos personales.
- registrar_sintomas: Solicita al paciente que ingrese sus síntomas.
- realizar_preguntas_relevantes: Genera preguntas relevantes basándose en los síntomas utilizando GPT-4o-mini.
"""


def obtener_datos_paciente():
    """Recopila los datos personales del paciente."""
    print("Por favor, ingrese sus datos personales:")
    nombre = input("Nombre: ")
    rut = input("RUT: ")
    sexo = input("Sexo (M/F): ")
    peso = input("Peso (kg): ")
    edad = input("Edad: ")

    return {
        "nombre": nombre,
        "rut": rut,
        "sexo": sexo,
        "peso": peso,
        "edad": edad
    }


def registrar_sintomas():
    """Solicita al paciente que ingrese sus síntomas."""
    print("\nIngrese los síntomas que está presentando (separados por coma):")
    sintomas = input("Síntomas: ")

    return [s.strip() for s in sintomas.split(",")]


def realizar_preguntas_relevantes(datos_basicos, sintomas, clientIA):
    """Genera preguntas relevantes basándose en los síntomas utilizando GPT-4o-mini."""
    print("\nEl modelo está analizando los síntomas y generando preguntas adicionales...")

    prompt = (
        f"Síntomas iniciales reportados: {', '.join(sintomas)}\n"
        "Con base en estos síntomas, genere hasta 5 preguntas relevantes para obtener más detalles "
        "que complementen el diagnóstico. Las preguntas deben ser claras y específicas."
    )

    try:
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente médico que ayuda a recopilar información relevante de pacientes.",
            },
            {"role": "user", "content": prompt},
        ]

        response = clientIA.chat.completions.create(
            model="gpt-4o-mini",  # Ajustado al modelo compatible
            messages=messages,
            temperature=0,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )
        preguntas = response.choices[0].message.content.split("\n")
        respuestas = {}
        for pregunta in preguntas:
            if pregunta.strip():
                respuesta = input(f"{pregunta.strip()} ")
                respuestas[pregunta.strip()] = respuesta

        return respuestas
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")

        return {}
