#!/usr/bin/env python

"""
Este módulo contiene funciones para la obtención de los datos personales del paciente y los síntomas relacionados con su enfermedad.

Funciones disponibles:
- obtener_datos_paciente: Solicita al cliente los datos personales.
- registrar_sintomas: Solicita al paciente que ingrese sus síntomas.
- realizar_preguntas_relevantes: Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini.
"""

import json
import re

# Constantes para validación de datos (EXPORTABLES A LA API)
CARACTERES_PARA_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
"""Caracteres permitidos para el nombre del paciente."""

CARACTERES_PARA_RUT = r"^[0-9]+-[0-9Kk]$"
"""Caracteres permitidos para el RUT del paciente."""

CARACTERES_PARA_SEXO = ["M", "F", "N"]
"""Caracteres permitidos para el sexo del paciente."""

EDAD_MINIMA = 0
"""Edad mínima permitida para el paciente."""

EDAD_MAXIMA = 125
"""Edad máxima permitida para el paciente."""

PESO_MINIMO = 0
"""Peso mínimo permitido para el paciente."""

PESO_MAXIMO = 250
"""Peso máximo permitido para el paciente."""


def obtener_datos_paciente():
    datos = {}
    intentos_maximos = 3

    # Validación con intentos limitados
    def solicitar_dato(pregunta, validacion_func, campo):
        intentos = 0
        ultima_respuesta = ""

        while intentos < intentos_maximos:
            respuesta = input(pregunta)
            ultima_respuesta = respuesta
            if validacion_func(respuesta):
                datos[campo] = respuesta if campo != "edad" else int(respuesta)
                return True
            print(f"⚠️ {campo.capitalize()} inválido. Inténtalo nuevamente.")
            intentos += 1

        # Si supera los intentos permitidos
        datos[campo] = ultima_respuesta
        return False

    print("\n🔹 **Registro de Datos Demográficos**")

    if not solicitar_dato("Ingresa tu nombre: ", validar_nombre, "nombre"):
        print("⛔ No es posible continuar sin un nombre válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu RUT (Ejemplo: 12345678-9): ", validar_rut, "rut"):
        print("⛔ No es posible continuar sin un RUT válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato(
        "Ingresa tu sexo (M: Masculino, F: Femenino, N: No informa): ",
        validar_sexo,
        "sexo",
    ):
        print("⛔ No es posible continuar sin un sexo válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu edad (0-120 años): ", validar_edad, "edad"):
        print("⛔ No es posible continuar sin una edad válida.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu peso (0-200 Kg): ", validar_peso, "peso"):
        print("⛔ No es posible continuar sin un peso valido")
        guardar_datos(datos, False)
        return

    # Si todos los datos son correctos
    guardar_datos(datos, True)
    print("✅ Datos guardados exitosamente en 'datos_demograficos.json'")

    return datos


def registrar_sintomas():
    """Solicita al paciente que ingrese sus síntomas."""
    print("\nIngrese los síntomas que está presentando (separados por coma):")
    sintomas = input("Síntomas: ")

    return [s.strip() for s in sintomas.split(",")]


def realizar_preguntas_relevantes(datos_basicos, sintomas, clientIA):
    """Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini."""
    print(
        "\nEl modelo está analizando los síntomas y generando preguntas adicionales..."
    )

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
                respuestas.append(
                    {"pregunta": pregunta.strip(), "respuesta": respuesta}
                )

        # Generar un JSON con las preguntas y respuestas en el formato solicitado
        preguntas_respuestas = respuestas

        # Guardar las preguntas y respuestas en un archivo JSON con codificación UTF-8
        with open("preguntas_respuestas.json", "w", encoding="utf-8") as f:
            json.dump(preguntas_respuestas, f, indent=4, ensure_ascii=False)
        print("1")

        return respuestas
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")
        return []


# Funciones de validación
def validar_nombre(nombre: str) -> bool:
    return bool(re.match(CARACTERES_PARA_NOMBRE, nombre.strip()))


def validar_rut(rut: str) -> bool:
    return bool(re.match(CARACTERES_PARA_RUT, rut.strip()))


def validar_sexo(caracter_sexo: str) -> bool:
    return caracter_sexo.strip().upper() in CARACTERES_PARA_SEXO


def validar_edad(edad: str) -> bool:
    # Se valida que la edad pueda comenzar en cero años (ej. un lactante), hasta 120 años
    return edad.isdigit() and EDAD_MINIMA <= int(edad.strip()) <= EDAD_MAXIMA


def validar_peso(peso: str) -> bool:
    # TODO: ¿El peso Podría ser 0 kg (ej. recién nacido)?
    return peso.isdigit() and PESO_MINIMO <= int(peso.strip()) <= PESO_MAXIMO


def guardar_datos(datos, almacenado_correctamente):
    datos["almacenado_correctamente"] = almacenado_correctamente
    with open("datos_demograficos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
