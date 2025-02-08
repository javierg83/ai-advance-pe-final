#!/usr/bin/env python

"""Archivo principal que soporta ejecución por consola y vía web (Flask)."""

import argparse
import logging
import os
import json
from datetime import timedelta

import openai
from dotenv import find_dotenv, load_dotenv

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
from rich import print, traceback

# Importar módulos del proyecto
import asistenteMedico
import consultaBaseConocimiento
import datosBasicosYSintomas
import generacionOrdenMedica
import moderador
import supervisorMedico

# Activa traceback para mejorar la depuración de excepciones
traceback.install()

# Constantes
DURACION_SESION = 7
"""Duración máxima de la sesión en minutos"""

PUERTO_DEFAULT = 8000
"""Puerto por defecto para el servidor web de Flask"""

HOST_DEFAULT = "localhost"
"""Host por defecto para el servidor web de Flask"""

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
if load_dotenv(find_dotenv(usecwd=True)):
    logging.debug("Archivo '.env' cargado exitosamente.")

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    logging.debug("OPENAI_API_KEY cargada correctamente.")
else:
    logging.error("OPENAI_API_KEY NO está definida. Revisa el entorno y/o el archivo '.env'.")
    exit(1)

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

    # Paso 7: Llamadas adicionales (Supervisor Médico)
    nivel_de_certeza = 0  # Valor por defecto
    if usoSupervisorMedico:
        respuesta_supervisor_json = supervisorMedico.revision_recomendacion_medica(
            openai_client,
            datos_paciente,
            sintomas,
            respuestas_adicionales,
            base_conocimiento,
            respuesta_asistente_medico
        )
        
        # Si la respuesta incluye delimitadores Markdown, eliminarlos.
        if respuesta_supervisor_json.startswith("```"):
            primer_salto = respuesta_supervisor_json.find("\n")
            ultimos_backticks = respuesta_supervisor_json.rfind("```")
            if primer_salto != -1 and ultimos_backticks != -1:
                respuesta_supervisor_json = respuesta_supervisor_json[primer_salto:ultimos_backticks].strip()

        # Parsear la respuesta JSON para obtener el nivel de certeza
        try:
            if isinstance(respuesta_supervisor_json, str):
                data = json.loads(respuesta_supervisor_json)
            else:
                data = respuesta_supervisor_json
            nivel_de_certeza = data.get("nivel_de_certeza", 0)
        except json.JSONDecodeError as e:
            print("Error al parsear la respuesta JSON:", e)
            nivel_de_certeza = 0

        print("El nivel de certeza es:", nivel_de_certeza)
        print("respuesta_supervisor=" + respuesta_supervisor_json)

    # Generar la orden médica solo si se cumple la condición adicional
    if usoGeneracionOrdenMedica and nivel_de_certeza > 70:
        generacionOrdenMedica.generar_orden_medica(
            openai_client,
            datos_paciente,
            sintomas,
            respuestas_adicionales,
            base_conocimiento,
            respuesta_asistente_medico,
        )
    else:
        print("Estimado paciente, con la información entregada no podemos generar una recomendación médica, por lo que debe asistir a un centro asistencial de forma presencial.")


# ----------------------------
# Configuración de Flask (Modo Web)
# ----------------------------
app = Flask(__name__)
# Clave secreta en entorno, para firmar cookies de sesión
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
# Configuramos la duración máxima de la sesión
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=DURACION_SESION)


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
        # Marcar la sesión como modificada y no permanente
        session.modified = True
        session.permanent = False

        return redirect(url_for("sintomas"))

    # GET
    session.clear()  # Limpiar la sesión, si existe
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
    app.logger.debug(f"Sintomas en sesión: {sintomas}")

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
    if (
        "datos" not in session
        or "sintomas" not in session
        or "respuestas" not in session
    ):
        app.logger.debug("Falta información en la sesión. Redirigiendo a registro.")
        return redirect(url_for("registro"))

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

    # Variables iniciales
    base_conocimiento = ""
    respuesta_asistente_medico = ""
    supervisor_response = ""
    nivel_de_certeza = 0
    orden_filepath = ""

    if not moderacion_ok:
        # Si la moderación falla, se puede notificar al usuario y detener el flujo
        app.logger.debug(
            "La consulta no cumple con las normas de moderación. Categorías detectadas: " +
            ", ".join(categorias)
        )
        respuesta_asistente_medico = "Consulta rechazada por moderación."
    else:
        # Paso 2: Búsqueda en base de conocimiento
        base_conocimiento = consultaBaseConocimiento.busqueda_base_conocimiento(
            openai_client, sintomas, respuestas
        )
        # Paso 3: Recomendación médica web
        app.logger.debug("Asistente Medico Iniciando")
        respuesta_asistente_medico = asistenteMedico.realizar_recomendacion_medica_web(
            openai_client, datos, sintomas, respuestas, base_conocimiento
        )
        # Paso 4: Llamada al Supervisor Médico para validar la recomendación
        app.logger.debug("Analisis de Supervisor Medico")
        supervisor_response = supervisorMedico.revision_recomendacion_medica(
            openai_client,
            datos,
            sintomas,
            respuestas,
            base_conocimiento,
            respuesta_asistente_medico
        )
        # Eliminar delimitadores Markdown, si existen
        
        if supervisor_response.startswith("```"):
            primer_salto = supervisor_response.find("\n")
            ultimos_backticks = supervisor_response.rfind("```")
            if primer_salto != -1 and ultimos_backticks != -1:
                supervisor_response = supervisor_response[primer_salto:ultimos_backticks].strip()

        # Parsear la respuesta JSON para extraer el nivel de certeza
        try:
            if isinstance(supervisor_response, str):
                data = json.loads(supervisor_response)
            else:
                data = supervisor_response
            nivel_de_certeza = data.get("nivel_de_certeza", 0)
        except json.JSONDecodeError as e:
            app.logger.error("Error al parsear la respuesta JSON: " + str(e))
            nivel_de_certeza = 0

        app.logger.debug("Supervisor Medico - El nivel de certeza es: " + str(nivel_de_certeza))
        
        # Paso 5: Generación de la orden médica solo si el nivel de certeza es mayor a 80
        if nivel_de_certeza >= 70:
            app.logger.debug("Generación Orden Medica - Iniciando:")
            orden_filepath = generacionOrdenMedica.generar_orden_medica_web(
                openai_client,
                datos,
                sintomas,
                respuestas,
                base_conocimiento,
                respuesta_asistente_medico,
            )
        else:
            # Se puede notificar al paciente que, con la información entregada, no se genera orden médica.
            respuesta_asistente_medico += (
                "\nEstimado paciente, con la información entregada no podemos generar una recomendación médica, "
                "por lo que debe asistir a un centro asistencial de forma presencial."
            )
            app.logger.debug("respuesta_asistente_medico="+respuesta_asistente_medico)

    session["orden_filepath"] = orden_filepath

    return render_template(
        "resultado.html",
        datos=datos,
        síntomas=sintomas,
        respuestas=respuestas,
        respuesta_asistente_medico=respuesta_asistente_medico,
        orden_filepath=orden_filepath,
        nivel_de_certeza=nivel_de_certeza,
        supervisor_response=supervisor_response
    )


@app.route("/download")
def download():
    orden_filepath = session.get("orden_filepath")
    if orden_filepath and os.path.exists(orden_filepath):
        directory, filename = os.path.split(orden_filepath)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return "No hay archivo disponible para descargar.", 404


def Lee_Parametros() -> tuple[bool, int, str]:
    parser = argparse.ArgumentParser(
        description="App Asistente Médico",
        add_help=True,
    )
    parser.add_argument(
        "--runserver",
        action="store_true",
        default=False,
        help="Ejecutar el servidor web de Flask; sino, se ejecuta en modo consola.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PUERTO_DEFAULT,
        required=False,
        help=f"Puerto para el servidor web de Flask, default: {PUERTO_DEFAULT}.",
    )
    parser.add_argument(
        "--host",
        default=HOST_DEFAULT,
        required=False,
        help=f"Host para el servidor web de Flask, default: {HOST_DEFAULT}.",
    )
    args = parser.parse_args()

    return args.runserver, args.port, args.host


# ----------------------------
# Selección del Modo de Ejecución
# ----------------------------
if __name__ == "__main__":
    run_server, port, host = Lee_Parametros()
    if run_server:
        app.run(host=host, port=port, debug=True, load_dotenv=True)
    else:
        main()

# Ejecutar en modo consola:
# python main.py

# Ejecutar como servidor web:
# python main.py --server --port 8000 --host localhost
# http://localhost:8000/
