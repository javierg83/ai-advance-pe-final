#!/usr/bin/env python

"""
Este módulo contiene las funciones y componenetes necesarios para conexion con Redis y obener informacion de la base de conocimiento.

"""

import numpy as np
from redis import Redis
from redis.commands.search.query import Query

VECTOR_FIELD_NAME = 'content_vector'


def conexion():

    # Configuración de OpenAI y Redis 
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    redis_db = os.environ.get("REDIS_DB")
    redis_password = os.environ.get("REDIS_PASSWORD")
    redis_username = os.environ.get("REDIS_USERNAME")
    redis_index = os.environ.get("REDIS_INDEX")
    gpt_key = os.environ.get("OPENAI_API_KEY")
    
    # Conexión única a Redis
    redis_url = f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
    redis_client = Redis.from_url(redis_url)
    
    # Verificación de conexión a Redis
    try:
        redis_client.ping()
        print("✅ Conexión a Redis exitosa.")
    except Exception as e:
        print("❌ Error en la conexión a Redis:", str(e))
        exit()

    return redis_client, redis_index


def find_vector_in_redis(query, client, redis_client, redis_index):

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
        q = Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]').sort_by('vector_score').paging(0, top_k).return_fields('filename', 'text_chunk', 'text_chunk_index', 'content').dialect(2)
        params_dict = {"vec_param": embedded_query}

        # Ejecutar la consulta en Redis
        results = redis_client.ft(redis_index).search(q, query_params=params_dict)

        return results.docs if results.total > 0 else []

    except Exception as e:
        print("❌ Error al buscar en Redis:", str(e))
        return []

def busqueda_base_conocimiento(client, sintomas, respuestas_adicionales):

    redis_client, redis_index = conexion()

    message = preparar_mensaje_vectorial(sintomas, respuestas_adicionales)

    find_database_answer = find_vector_in_redis(message, client, redis_client, redis_index)

    if find_database_answer:
        contents = [str(content["content"]) for content in find_database_answer]
        content_0 = contents[0]
    else:
        content_0 = "No se encontraron coincidencias en la base de datos."

    print("content_0="+content_0)
    return content_0
    

def preparar_mensaje_vectorial(sintomas, respuestas_adicionales):

    message = "Síntomas: " + ", ".join(sintomas) + "\n\n"

    # Si hay respuestas adicionales, se procesan y se agregan al mensaje.
    if isinstance(respuestas_adicionales, list) and respuestas_adicionales:
        respuestas_str = "; ".join(
            [f"{r.get('pregunta', 'Sin pregunta')}: {r.get('respuesta', 'Sin respuesta')}"
            for r in respuestas_adicionales if isinstance(r, dict)]
        )
        message += "Respuestas adicionales: " + respuestas_str

    return message
