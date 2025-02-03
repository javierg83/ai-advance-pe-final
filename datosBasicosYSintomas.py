#!/usr/bin/env python

import json

"""
Este módulo contiene funciones para la obtención de los datos personales del paciente y los síntomas relacionados con su enfermedad.

Funciones disponibles:
- obtener_datos_paciente: Solicita al cliente los datos personales.
- registrar_sintomas: Solicita al paciente que ingrese sus síntomas.
- realizar_preguntas_relevantes: Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini.
"""

def obtener_datos_paciente():
    """Recopila los datos personales del paciente."""
    print("Por favor, ingrese sus datos personales:")
    nombre = input("Nombre: ")
    rut = input("RUT: ")
    sexo = input("Sexo (M/F): ")
    peso = input("Peso (kg): ")
    edad = input("Edad: ")

    # Generar un JSON con los datos básicos del paciente
    datos_basicos = {
        "nombre": nombre,
        "rut": rut,
        "sexo": sexo,
        "peso": peso,
        "edad": edad
    }

    # Guardar los datos básicos en un archivo JSON
    with open('datos_basicos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_basicos, f, indent=4, ensure_ascii=False)

    return datos_basicos


def registrar_sintomas():
    """Solicita al paciente que ingrese sus síntomas."""
    print("\nIngrese los síntomas que está presentando (separados por coma):")
    sintomas = input("Síntomas: ")

    return [s.strip() for s in sintomas.split(",")]


def realizar_preguntas_relevantes(datos_basicos, sintomas, clientIA):
    """Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini."""
    print("\nEl modelo está analizando los síntomas y generando preguntas adicionales...")

    # Ajustar el prompt para incluir sexo, peso y edad del paciente
    prompt = (
        f"Paciente de {datos_basicos['edad']} años, sexo {datos_basicos['sexo']} y peso {datos_basicos['peso']} kg.\n"
        f"Síntomas reportados: {', '.join(sintomas)}\n"
        "Con base en estos síntomas y características del paciente, genere hasta 5 preguntas relevantes "
        "para obtener más detalles que complementen el diagnóstico. Las preguntas deben ser claras y específicas."
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
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )
        
        preguntas = response.choices[0].message.content.split("\n")
        respuestas = []
        for pregunta in preguntas:
            if pregunta.strip():
                respuesta = input(f"{pregunta.strip()} ")
                respuestas.append({
                    "pregunta": pregunta.strip(),
                    "respuesta": respuesta
                })

        # Generar un JSON con las preguntas y respuestas en el formato solicitado
        preguntas_respuestas = respuestas

        # Guardar las preguntas y respuestas en un archivo JSON con codificación UTF-8
        with open('preguntas_respuestas.json', 'w', encoding='utf-8') as f:
            json.dump(preguntas_respuestas, f, indent=4, ensure_ascii=False)
        print("1")

        return respuestas
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")
        return []
