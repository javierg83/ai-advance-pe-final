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
import supervisorMedico
import generacionOrdenMedica

# Load the environment variables from .env file
load_dotenv()

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")


# Configuración de API Key de OpenAI
client = OpenAI(api_key=openai_api_key)


def main():
    print("################ INICIO PROGRAMA ################\n")

    usoModeradores = True
    usoRag = True
    usoAgente = True
    usoSupervisorMedico = True
    usoGeneracionOrdenMedica = True

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
        categorias_restringidas = moderador.analisis_moderador_generico(client, datos_paciente, sintomas, respuestas_adicionales)

        if categorias_restringidas:
            print("MODERADOR GENERICO NOK. LO SENTIMOS TU PREGUNTA NO CUMPLE CON LAS REGLAS ESTABLECIDAS")
        else:
            print("MODERADOR GENERICO OK")

        #moderador.moderador_intencion()

    # Paso 3: Se Utiliza llamada a RAG
    if(usoRag):

        base_conocimiento = consultaBaseConocimiento.busqueda_base_conocimiento(client, sintomas, respuestas_adicionales)

    if(usoAgente):
        # Paso 3: Se llamada a IA
        respuesta_asistente_medico = asistenteMedico.realizar_recomendacion_medica(client, datos_paciente, sintomas, respuestas_adicionales, base_conocimiento)

        print(respuesta_asistente_medico)


    if(usoSupervisorMedico):
        # Paso 3: Se llamada a IA
        supervisorMedico.revision_recomendacion_medica()

    if(usoGeneracionOrdenMedica):
        # Paso 3: Se llamada a IA
        generacionOrdenMedica.generar_orden_medica("javier", 31, 98, "15.737.576-8", "recomendacion para el paciente es bla bla")




if __name__ == "__main__":
    main()
