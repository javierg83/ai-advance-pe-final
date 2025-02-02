
import openai
import json
import numpy as np
from redis import Redis
from redis.commands.search.query import Query

# Configuración de OpenAI y Redis (OCULTAR ESTOS DATOS EN EL ENV)
redis_host = "redis-19179.c277.us-east-1-3.ec2.redns.redis-cloud.com"
redis_port = 19179
redis_db = 0
redis_password = "GlTO5JYBYVaT4bGgEKhpAkR2oyxxbyg4"
redis_username = "default"
redis_index = "V1"
gpt_key = ""

# Crear cliente de OpenAI con la nueva API
client = openai.OpenAI(api_key=gpt_key)

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

# Prompt del asistente
ai_prompt_system = """
Tu nombre es EnfBot, eres un experto en enfermedades y su solución.
Tu principal misión es responder y ayudar a los clientes en descubrir su enfermedad, entregarle una solución, medicamento y informarle si tendrá licencia médica.
Ubicación: Chile.
Siempre en español.
"""

VECTOR_FIELD_NAME = 'content_vector'

def find_vector_in_redis(query):
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

def generate_text(prompt):
    messages = [{"role": "system", "content": ai_prompt_system}]
    messages.append({'role': 'user', 'content': prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            max_tokens=300,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content

    except Exception as e:
        print("❌ Error al generar texto:", str(e))
        return "Error al generar respuesta."

# Mensaje de prueba
message = """
¿Qué enfermedad tengo y cuál es la solución si mis síntomas son dolor de garganta e inflamación de amígdalas? Quiero saber qué me recomiendas para recuperarme y cuánto me demoraré en estar sano.
"""

find_database_answer = find_vector_in_redis(message)

if find_database_answer:
    contents = [str(content["content"]) for content in find_database_answer]
    content_0 = contents[0]
else:
    content_0 = "No se encontraron coincidencias en la base de datos."

# Construcción del prompt final
prompt = f"Contexto: {content_0}, respeta el contexto siempre y responde la pregunta: {message}"
response = generate_text(prompt)

print("Response:", response)
