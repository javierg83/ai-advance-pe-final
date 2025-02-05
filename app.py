#!/usr/bin/env python

""" Aplicación de FastAPI para un asistente médico. """

import os
import random
from datetime import datetime
from typing import Dict, Union

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from rich import inspect, print, traceback

from datosBasicosYSintomas import EDAD_MAXIMA, EDAD_MINIMA, PESO_MAXIMO, PESO_MINIMO

# activa traceback para mejorar la depuración de excepciones
traceback.install()

print("[bold green]Iniciando App...[/bold green]")

# Load the environment variables from .env file
load_dotenv()

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Inicializamos la aplicación de FastAPI.
app = FastAPI()

# Inicializamos el modelo de chat de LangChain usando la API de OpenAI.
chat_model = ChatOpenAI(temperature=0, api_key=openai_api_key)

# Diccionario global para almacenar las sesiones activas.
# Cada sesión contendrá su propia memoria y otros metadatos.
sessions: Dict[int, Dict] = {}


# Modelos de entrada/salida de FastAPI.
class InitRequest(BaseModel):
    nombre: str
    edad: int
    sexo: str
    peso: int


class InitResponse(BaseModel):
    # Resultado de la operación: "EXITO" o "ERROR"
    resultado: str
    detalle: Union[str, list]
    id_sesion: Union[int, None] = None


class AskRequest(BaseModel):
    id_sesion: int
    respuesta_usuario: str


class AskResponse(BaseModel):
    # Resultado de la operación: "EXITO" o "ERROR"
    resultado: str
    detalle: str
    # Tipo de respuesta: "inicial", "clarificación", "resultado"
    tipo_respuesta: str
    documento_anexo: str


# Prompt para validar datos personales en /init.
init_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"Eres un asistente experto en validación de datos. Valida que el nombre no esté vacío, que la edad esté entre {EDAD_MINIMA} y {EDAD_MAXIMA}, que el sexo sea 'masculino', 'femenino' u 'otro', y que el peso sea un número entre {PESO_MINIMO} y {PESO_MAXIMO}.",
        ),
        (
            "human",
            "Datos: Nombre: {nombre}, Edad: {edad}, Sexo: {sexo}, Peso: {peso}. Responde 'EXITO' si todos los datos son correctos o devuelve una descripción de los errores.",
        ),
    ]
)

# Prompt para procesar los mensajes de interacción en /ask.
ask_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un asistente que ayuda a interpretar síntomas y a formular preguntas de clarificación. Basándote en el contexto, responde de forma clara.",
        ),
        ("human", "{input}"),
    ]
)


def generar_id_sesion() -> int:
    nuevo_id = random.randint(1000, 9999)
    while nuevo_id in sessions:
        nuevo_id = random.randint(1000, 9999)
    return nuevo_id


@app.post("/init", response_model=InitResponse)
async def mensaje_init(init_req: InitRequest):
    # Formateamos el prompt con los datos recibidos.
    prompt = init_prompt.format_prompt(
        nombre=init_req.nombre,
        edad=init_req.edad,
        sexo=init_req.sexo,
        peso=init_req.peso,
    )
    # Convertimos el prompt a mensajes.
    mensajes = prompt.to_messages()
    # Invocamos el modelo.
    response = chat_model.invoke(mensajes)

    # Si la respuesta no es exactamente "éxito", se asume que hay errores.
    if response.content.strip().upper() != "EXITO":
        errores = response.content.strip().splitlines()
        return InitResponse(resultado="ERROR", detalle=errores, id_sesion=None)

    # Si la validación es correcta, se genera un id de sesión.
    id_sesion = generar_id_sesion()
    # Se crea la memoria para la sesión.
    memory = ConversationBufferMemory(return_messages=True)
    
    # Se guarda la sesión con su memoria y fecha de creación.
    sessions[id_sesion] = {
        "memory": memory,
        "created_at": datetime.now().isoformat(),
        "nombre": init_req.nombre,
    }

    mensaje_bienvenida = (
        f"Bienvenido {init_req.nombre}. Por favor, ingrese sus síntomas."
    )
    # Se registra un mensaje inicial en la memoria.
    memory.save_context(
        {"input": f"#Mis Datos Personales:\n- Nombre: {init_req.nombre}\n- Edad: {init_req.edad}\n- Sexo: {init_req.sexo}\n- Peso: {init_req.peso}"},
        {"output": mensaje_bienvenida}
    )
    # debug
    inspect(sessions, docs=False)

    return InitResponse(
        resultado="EXITO",
        detalle=mensaje_bienvenida,
        id_sesion=id_sesion
    )


@app.post("/ask", response_model=AskResponse)
async def mensaje_ask(ask_req: AskRequest):
    if ask_req.id_sesion not in sessions:
        return AskResponse(
            resultado="ERROR",
            detalle="Sesión no encontrada o expirada.",
            tipo_respuesta="",
            documento_anexo="",
        )

    session = sessions[ask_req.id_sesion]
    memory = session["memory"]

    # Se asume que la respuesta del usuario es siempre un string.
    input_usuario = ask_req.respuesta_usuario
    tipo_resp = "clarificación"

    # Se carga el historial de conversación.
    history = memory.load_memory_variables({})
    # Se formatea el prompt para la consulta.
    prompt_msg = ask_prompt.format_prompt(input=input_usuario)
    # Se convierten a mensajes.
    mensajes = prompt_msg.to_messages()
    # Inyectamos el historial, si existe.
    if "chat_history" in history:
        mensajes.append(HumanMessage(content=history["chat_history"]))

    # Invocamos el modelo.
    response = chat_model.invoke(mensajes)
    # Se guarda la respuesta en la memoria.
    memory.save_context({"input": input_usuario}, {"output": response.content})
    # Simulación de documento anexo.
    doc_anexo = "ENCRYPTED_DATA"
    # debug
    inspect(sessions, docs=False)

    return AskResponse(
        resultado="EXITO",
        detalle=response.content,
        tipo_respuesta=tipo_resp,
        documento_anexo=doc_anexo,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# uvicorn app:app --reload
# http://127.0.0.1:8000/docs
