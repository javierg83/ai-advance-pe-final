#!/usr/bin/env python

"""
Paso 1: Este módulo contiene las funciones y componentes necesarios para convertir la información de un archivo .csv a diferentes claves .txt
"""
import os
import pandas as pd 

# Directorios con rutas corregidas
output_dir = r'C:\Users\Escritorio\enfermedades_texto'
input_file = r'C:\Users\Escritorio\enfermedades_texto\claves.csv'

# Crear la carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

# Leer el archivo CSV
df = pd.read_csv(input_file)

# Función para generar el texto
def create_enfermedad_details_text(row):
    return (f"Enfermedad: {row['nombre']}\n"
            f"Sintoma Principal: {row['sintoma_1']}\n"
            f"Sintoma Secundario: {row['sintoma_2']}\n"
            f"Sintoma Normal: {row['sintoma_3']}\n"
            f"Sintoma Medio: {row['sintoma_4']}\n"
            f"Sintoma Bajo: {row['sintoma_5']}\n"
            f"Sintoma sin importancia: {row['sintoma_6']}\n"
            f"Solucion: {row['solucion']}\n"
            f"Medicamento: {row['medicamento']}\n"
            f"Licencia Medica: {row['licencia_medica']}\n")

# Iterar sobre el DataFrame y guardar cada enfermedad como un archivo .txt
for _, row in df.iterrows():
    enfermedad_name = row['nombre'].replace("/", "-")  # Asegurar nombres de archivo válidos
    file_name = f"{enfermedad_name}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Escribir los detalles en un archivo .txt
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(create_enfermedad_details_text(row))

print(f"Archivos guardados en: {output_dir}")


"""
Paso 2: Este módulo contiene las funciones y componentes necesarios para importar las claves .txt a Redis
"""
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.document_loaders import TextLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import numpy as np
import openai
from redis.commands.search.query import Query
import redis
import os

input_dir = os.path.normpath('C:/Users/Escritorio/enfermedades_texto')

# Load the environment variables from .env file
load_dotenv()

# Configuración de OpenAI y Redis
redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_db = os.environ.get("REDIS_DB")
redis_password = os.environ.get("REDIS_PASSWORD")
redis_username = os.environ.get("REDIS_USERNAME")
redis_index = os.environ.get("REDIS_INDEX")
gpt_key="sk-proj-" (FALTA PASAR A DOTENV)

#Crear embeddings usando la API de OpenAI
embeddings = OpenAIEmbeddings(openai_api_key=gpt_key)

#Iterar sobre cada archivo en el directorio y cargarlo a REDIS 
for filename in sorted(os.listdir(input_dir)):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)

        #Cargar el documento desde el archivo de texto 
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        #Dividir el documento en fragmentos de tamaño adecuado para embeddings 
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        #Cargar los documentos divididos a REDIS con embeddings
        vectorstore = Redis.from_documents(
            docs,
            embeddings,
            redis_url=f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}",
            index_name=redis_index
        )

        print(f"Documentos del archivo '{filename}'cargado exitosamente en REDIS.")

print("Todos los archivos han sido procesados y cargados en REDIS.")


"""
Paso 3: Este módulo contiene las funciones y componentes necesarios para conexión con Redis y obtener información de la base de conocimiento.
"""
import os

import numpy as np
from dotenv import load_dotenv
from redis import Redis
from redis.commands.search.query import Query

# Load the environment variables from .env file
load_dotenv()

# Configuración de OpenAI y Redis
redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_db = os.environ.get("REDIS_DB")
redis_password = os.environ.get("REDIS_PASSWORD")
redis_username = os.environ.get("REDIS_USERNAME")
redis_index = os.environ.get("REDIS_INDEX")

VECTOR_FIELD_NAME = "content_vector"
"""Nombre del campo de vectores en Redis."""

# Conexión única a Redis
redis_url = (
    f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
)
redis_client = Redis.from_url(redis_url)

# Verificación de conexión a Redis
try:
    redis_client.ping()
    print("✅ Conexión a Redis exitosa.")
except Exception as e:
    print("❌ Error en la conexión a Redis:", str(e))
    exit()


def find_vector_in_redis(query, client):
    try:
        top_k = 1

        # Crear el embedding con la API actualizada
        response = client.embeddings.create(
            input=[query],  # OpenAI espera una lista
            model="text-embedding-ada-002"
        )

        # Obtener el embedding vectorizado
        embedding_vector = response.data[0].embedding
        embedded_query = np.array(embedding_vector, dtype=np.float32).tobytes()

        # Construcción de la consulta KNN en Redis
        q = (
            Query(f"*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]")
            .sort_by("vector_score")
            .paging(0, top_k)
            .return_fields("filename", "text_chunk", "text_chunk_index", "content")
            .dialect(2)
        )
        params_dict = {"vec_param": embedded_query}

        # Ejecutar la consulta en Redis
        results = redis_client.ft(redis_index).search(q, query_params=params_dict)

        return results.docs if results.total > 0 else []

    except Exception as e:
        print("❌ Error al buscar en Redis:", str(e))
        return []


def busqueda_base_conocimiento(client, sintomas, respuestas_adicionales):
    message = preparar_mensaje_vectorial(sintomas, respuestas_adicionales)

    find_database_answer = find_vector_in_redis(message, client)

    if find_database_answer:
        contents = [str(content["content"]) for content in find_database_answer]
        content_0 = contents[0]
    else:
        content_0 = "No se encontraron coincidencias en la base de datos."

    print("content_0=" + content_0)
    return content_0


def preparar_mensaje_vectorial(sintomas, respuestas_adicionales):
    message = "Síntomas: " + ", ".join(sintomas) + "\n\n"

    # Si hay respuestas adicionales, se procesan y se agregan al mensaje.
    if isinstance(respuestas_adicionales, list) and respuestas_adicionales:
        respuestas_str = "; ".join(
            [
                f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
                for r in respuestas_adicionales
                if isinstance(r, dict)
            ]
        )
        message += "Respuestas adicionales: " + respuestas_str

    return message
