#!/usr/bin/env python

"""Archivo principal que soporta ejecución por consola y vía web (Flask)."""

import os
import sys
import logging

import openai
from dotenv import load_dotenv

# Importar Flask y dependencias
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

# Importar módulos del proyecto
import asistenteMedico
import consultaBaseConocimiento
import datosBasicosYSintomas
import generacionOrdenMedica
import moderador
import supervisorMedico


# ----------------------------
# Configuración de Logging
# ----------------------------
logging.basicConfig(
    level=logging.ERROR,  # Se muestran mensajes DEBUG y superiores
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ----------------------------
# Cargar variables de entorno y configurar OpenAI
# ----------------------------
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    logging.debug("OPENAI_API_KEY cargada correctamente.")
else:
    logging.error("OPENAI_API_KEY NO está definida. Revisa el archivo .env")

# Configurar la API key para la librería de OpenAI
openai.api_key = openai_api_key

# Definir el objeto openai_client (para evitar posibles conflictos de nombres)
openai_client = openai


# ----------------------------
# Flujo CLI (Modo Consola)
# ----------------------------
def main():
    print("################ INICIO PROGRAMA (CLI) ################\n")
    usoModeradores = True
    usoRag = True
    usoAgente = True
    usoSupervisorMedico = True
    usoGeneracionOrdenMedica = True
    base_conocimiento = ""

    # Paso 1: Recopilar datos personales del paciente (modo consola)
    datos_paciente = datosBasicosYSintomas.obtener_datos_paciente()

    # Paso 2: Registrar los síntomas (modo consola)
    sintomas = datosBasicosYSintomas.registrar_sintomas()

    # Paso 3: Realizar preguntas relevantes basadas en los síntomas
    respuestas_adicionales = datosBasicosYSintomas.realizar_preguntas_relevantes(
        datos_paciente, sintomas, openai_client
    )

    # Paso 4: Uso de moderadores
    if usoModeradores:
        categorias_restringidas = moderador.analisis_moderador_generico(
            openai_client, datos_paciente, sintomas, respuestas_adicionales
        )
        if categorias_restringidas:
            print(
                "MODERADOR GENÉRICO NOK. LO SENTIMOS: TU PREGUNTA NO CUMPLE CON LAS REGLAS ESTABLECIDAS."
            )
        else:
            print("MODERADOR GENERICO OK")

    # Paso 5: Llamada a RAG (búsqueda en base de conocimiento)
    if usoRag:
        base_conocimiento = consultaBaseConocimiento.busqueda_base_conocimiento(
            openai_client, sintomas, respuestas_adicionales
        )

    # Paso 6: Recomendación médica vía IA
    if usoAgente:
        respuesta_asistente_medico = asistenteMedico.realizar_recomendacion_medica(
            openai_client,
            datos_paciente,
            sintomas,
            respuestas_adicionales,
            base_conocimiento,
        )
        # print("\n--- Recomendación Médica ---")
        # print(respuesta_asistente_medico)

    # Paso 7: Llamadas adicionales
    if usoSupervisorMedico:
        supervisorMedico.revision_recomendacion_medica()
    if usoGeneracionOrdenMedica:
        generacionOrdenMedica.generar_orden_medica(
            openai_client,
            datos_paciente,
            sintomas,
            respuestas_adicionales,
            base_conocimiento,
            respuesta_asistente_medico,
        )


# ----------------------------
# Configuración de Flask (Modo Web)
# ----------------------------
app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Reemplaza con una clave segura para producción

@app.route("/", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        rut = request.form.get("rut")
        sexo = request.form.get("sexo")
        edad = request.form.get("edad")
        peso = request.form.get("peso")

        app.logger.debug(
            f"Datos recibidos: nombre={nombre}, rut={rut}, sexo={sexo}, edad={edad}, peso={peso}"
        )

        errores = datosBasicosYSintomas.validar_datos_paciente_web(
            nombre, rut, sexo, edad, peso
        )
        app.logger.debug(f"Errores de validación: {errores}")
        if errores:
            return render_template("registro.html", errores=errores, datos=request.form)

        session["datos"] = {
            "nombre": nombre,
            "rut": rut,
            "sexo": sexo,
            "edad": edad,
            "peso": peso,
        }
        return redirect(url_for("sintomas"))

    # GET
    return render_template("registro.html")


@app.route("/sintomas", methods=["GET", "POST"])
def sintomas():
    if "datos" not in session:
        return redirect(url_for("registro"))

    if request.method == "POST":
        sintomas_str = request.form.get("sintomas")
        sintomas_lista = datosBasicosYSintomas.parse_sintomas_web(sintomas_str)
        session["sintomas"] = sintomas_lista
        return redirect(url_for("preguntas"))

    # GET
    return render_template("sintomas.html")


@app.route("/preguntas", methods=["GET", "POST"])
def preguntas():
    if "datos" not in session or "sintomas" not in session:
        app.logger.debug("Falta información en la sesión. Redirigiendo a registro.")
        return redirect(url_for("registro"))

    datos = session.get("datos")
    sintomas = session.get("sintomas")

    app.logger.debug(f"Datos en sesión: {datos}")
    app.logger.debug(f"Síntomas en sesión: {sintomas}")

    # Forzar la generación de nuevas preguntas para depuración:
    if "preguntas" in session:
        del session["preguntas"]

    if "preguntas" not in session:
        app.logger.debug(
            "No se encontraron preguntas en sesión. Generando nuevas preguntas..."
        )
        preguntas_generadas = datosBasicosYSintomas.realizar_preguntas_relevantes_web(
            datos, sintomas, openai_client
        )
        session["preguntas"] = preguntas_generadas
        app.logger.debug(f"Preguntas generadas: {preguntas_generadas}")
    else:
        preguntas_generadas = session.get("preguntas")

    if request.method == "POST":
        respuestas = []
        for i, pregunta in enumerate(preguntas_generadas):
            respuesta = request.form.get(f"pregunta_{i}")
            respuestas.append({"pregunta": pregunta, "respuesta": respuesta})
        session["respuestas"] = respuestas

        return redirect(url_for("resultado"))

    # GET
    return render_template("preguntas.html", preguntas=preguntas_generadas)


@app.route("/resultado")
def resultado():
    # Recuperar datos de la sesión
    datos = session.get("datos")
    sintomas = session.get("sintomas")
    respuestas = session.get("respuestas")

    # Paso 1: Moderación (ejemplo con moderador_pasada_web)
    moderacion_ok, categorias = moderador.moderacion_pasada_web(
        openai_client,
        datos,
        sintomas,
        respuestas
    )

    if not moderacion_ok:
        conclusion = (
            "La consulta no cumple con las normas de moderación. Categorías detectadas: "
            + ", ".join(categorias)
        )
        base_conocimiento = ""

    else:
        # Paso 2: Búsqueda en Redis
        base_conocimiento = consultaBaseConocimiento.busqueda_base_conocimiento(
            openai_client, sintomas, respuestas
        )

        # Paso 3: Recomendación médica web
        respuesta_asistente_medico = asistenteMedico.realizar_recomendacion_medica_web(
            openai_client, datos, sintomas, respuestas, base_conocimiento
        )

        # Paso 4: Generar la orden médica y guardar la ruta en la sesión
        orden_filepath = generacionOrdenMedica.generar_orden_medica_web(
            openai_client,
            datos,
            sintomas,
            respuestas,
            base_conocimiento,
            respuesta_asistente_medico,
        )

    session["orden_filepath"] = orden_filepath

    return render_template(
        "resultado.html",
        datos=datos,
        sintomas=sintomas,
        respuestas=respuestas,
        respuesta_asistente_medico=respuesta_asistente_medico,
        orden_filepath=orden_filepath,
    )


@app.route("/download")
def download():
    orden_filepath = session.get("orden_filepath")
    if orden_filepath and os.path.exists(orden_filepath):
        directory, filename = os.path.split(orden_filepath)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return "No hay archivo disponible para descargar.", 404


# ----------------------------
# Selección del Modo de Ejecución
# ----------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        app.run(debug=False)
    else:
        main()

# Ejecutar en modo consola:
# python main.py

# Ejecutar como servidor web:
# python main.py runserver
# http://localhost:8000/
