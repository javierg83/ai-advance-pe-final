#!/usr/bin/env python
"""
Este módulo contiene funciones para la obtención de los datos personales del paciente,
registro de síntomas y generación de preguntas relevantes utilizando GPT-4o-mini.

Funciones para consola:
  - obtener_datos_paciente()
  - registrar_sintomas()
  - realizar_preguntas_relevantes()

Funciones para entornos web (con sufijo _web):
  - validar_datos_paciente_web()
  - parse_sintomas_web()
  - realizar_preguntas_relevantes_web()
"""

import json
import re
import logging

# ----------------------------
# Constantes para validación
# ----------------------------
CARACTERES_PARA_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
CARACTERES_PARA_RUT = r"^[0-9]+-[0-9Kk]$"
CARACTERES_PARA_SEXO = ["M", "F", "N"]
EDAD_MINIMA = 0
EDAD_MAXIMA = 125
PESO_MINIMO = 0
PESO_MAXIMO = 250

# ----------------------------
# Funciones para Consola
# ----------------------------
def obtener_datos_paciente():
    datos = {}
    intentos_maximos = 3

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
    if not solicitar_dato("Ingresa tu sexo (M, F, N): ", validar_sexo, "sexo"):
        print("⛔ No es posible continuar sin un sexo válido.")
        guardar_datos(datos, False)
        return
    if not solicitar_dato("Ingresa tu edad (0-125 años): ", validar_edad, "edad"):
        print("⛔ No es posible continuar sin una edad válida.")
        guardar_datos(datos, False)
        return
    if not solicitar_dato("Ingresa tu peso (0-250 Kg): ", validar_peso, "peso"):
        print("⛔ No es posible continuar sin un peso válido")
        guardar_datos(datos, False)
        return

    guardar_datos(datos, True)
    print("✅ Datos guardados exitosamente en 'datos_demograficos.json'")
    return datos

def registrar_sintomas():
    """Solicita al paciente que ingrese sus síntomas vía consola."""
    print("\nIngrese los síntomas que está presentando (separados por coma):")
    sintomas = input("Síntomas: ")
    return [s.strip() for s in sintomas.split(",")]

def realizar_preguntas_relevantes(datos_basicos, sintomas, clientIA):
    """Genera preguntas relevantes vía consola solicitando respuestas al usuario."""
    print("\nEl modelo está analizando los síntomas y generando preguntas adicionales...")
    prompt = (
        f"Paciente de {datos_basicos['edad']} años, sexo {datos_basicos['sexo']} y peso {datos_basicos['peso']} kg.\n"
        f"Síntomas reportados: {', '.join(sintomas)}\n"
        "Con base en estos síntomas y características del paciente, genere hasta 5 preguntas relevantes "
        "para obtener más detalles que complementen el diagnóstico. Las preguntas deben ser claras y específicas."
        "SALIDA: las 5 preguntas generadas sin otros textos complementarios."
    )

    try:
        messages = [
            {"role": "system", "content": "Eres un asistente médico que ayuda a recopilar información relevante de pacientes."},
            {"role": "user", "content": prompt},
        ]
    
        response = clientIA.chat.completions.create(
        #response = clientIA.chat.ChatCompletion.create(
            model="gpt-4o-mini",
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
                respuestas.append({"pregunta": pregunta.strip(), "respuesta": respuesta})
        with open("preguntas_respuestas.json", "w", encoding="utf-8") as f:
            json.dump(respuestas, f, indent=4, ensure_ascii=False)
        print("Preguntas y respuestas guardadas en 'preguntas_respuestas.json'")
        return respuestas
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")
        return []

# ----------------------------
# Funciones para Entornos Web (Sufijo _web)
# ----------------------------
def validar_datos_paciente_web(nombre, rut, sexo, edad, peso):
    """
    Valida los datos del paciente recibidos desde un formulario web.
    Retorna un diccionario de errores (vacío si no hay errores).
    """
    errores = {}
    if not validar_nombre(nombre):
        errores["nombre"] = "Nombre inválido. Sólo se permiten letras y espacios."
    if not validar_rut(rut):
        errores["rut"] = "RUT inválido. Debe tener el formato 12345678-9."
    if not validar_sexo(sexo):
        errores["sexo"] = "Sexo inválido. Use M, F o N."
    if not validar_edad(str(edad)):
        errores["edad"] = f"Edad inválida. Debe estar entre {EDAD_MINIMA} y {EDAD_MAXIMA}."
    if not validar_peso(str(peso)):
        errores["peso"] = f"Peso inválido. Debe estar entre {PESO_MINIMO} y {PESO_MAXIMO} Kg."
    return errores

def parse_sintomas_web(sintomas_str):
    """
    Procesa un string con síntomas separados por coma y retorna una lista.
    Ejemplo: "fiebre, tos, dolor" -> ['fiebre', 'tos', 'dolor']
    """
    return [s.strip() for s in sintomas_str.split(",") if s.strip()]

def realizar_preguntas_relevantes_web(datos_basicos, sintomas, clientIA):
    """
    Genera preguntas relevantes utilizando GPT-4o-mini y retorna una lista de preguntas
    para ser presentadas en la web (sin solicitar respuestas por consola).
    Se deja una traza del prompt enviado y la respuesta recibida.
    """
    prompt = (
        f"Paciente de {datos_basicos['edad']} años, sexo {datos_basicos['sexo']} y peso {datos_basicos['peso']} kg.\n"
        f"Síntomas reportados: {', '.join(sintomas)}\n"
        "Con base en estos síntomas y características del paciente, genere hasta 5 preguntas relevantes "
        "para obtener más detalles que complementen el diagnóstico. Las preguntas deben ser claras y específicas."
        "SALIDA: las 5 preguntas generadas sin otros textos complementarios."
    )
    try:
        # Usar el logger de Flask si está en contexto, sino el global
        from flask import current_app
        logger = current_app.logger if current_app else logging.getLogger(__name__)
        
        logger.debug("------------------------------------------------")
        logger.debug("Enviando el siguiente prompt a OpenAI:")
        logger.debug(prompt)
        logger.debug("------------------------------------------------")
        
        messages = [
            {"role": "system", "content": "Eres un asistente médico que ayuda a recopilar información relevante de pacientes."},
            {"role": "user", "content": prompt},
        ]
        response = clientIA.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )
        content = response.choices[0].message.content
        logger.debug("------------------------------------------------")
        logger.debug("Respuesta recibida de OpenAI:")
        logger.debug(content)
        logger.debug("------------------------------------------------")
        
        preguntas = [line.strip() for line in content.split("\n") if line.strip()]
        return preguntas
    except Exception as e:
        from flask import current_app
        if current_app:
            current_app.logger.error(f"Error al generar preguntas (web): {str(e)}")
        else:
            logging.error(f"Error al generar preguntas (web): {str(e)}")
        return []

# ----------------------------
# Funciones de Validación (Originales)
# ----------------------------
def validar_nombre(nombre: str) -> bool:
    return bool(re.match(CARACTERES_PARA_NOMBRE, nombre.strip()))

def validar_rut(rut: str) -> bool:
    return bool(re.match(CARACTERES_PARA_RUT, rut.strip()))

def validar_sexo(caracter_sexo: str) -> bool:
    return caracter_sexo.strip().upper() in CARACTERES_PARA_SEXO

def validar_edad(edad: str) -> bool:
    return edad.isdigit() and EDAD_MINIMA <= int(edad.strip()) <= EDAD_MAXIMA

def validar_peso(peso: str) -> bool:
    return peso.isdigit() and PESO_MINIMO <= int(peso.strip()) <= PESO_MAXIMO

def guardar_datos(datos, almacenado_correctamente):
    datos["almacenado_correctamente"] = almacenado_correctamente
    with open("datos_demograficos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
