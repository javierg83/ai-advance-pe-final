 # Este modulo se ocupa de la preparación e importación de datos en un archivo .csv hasta cargarlos en una base de datos en Redis a utilizar como contexto para las consultas del usuario 

import os
import pandas as pd 
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


# Directorios con rutas corregidas
output_dir = r'C:\Users\laram\OneDrive\Escritorio\repositorio\ai-advance-pe-final-1\data'
input_file = r'C:\Users\laram\OneDrive\Escritorio\repositorio\ai-advance-pe-final-1\data\claves.csv'

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


""


input_dir = os.path.normpath('C:\Users\laram\OneDrive\Escritorio\repositorio\ai-advance-pe-final-1\data')

redis_host="redis-19179.c277.us-east-1-3.ec2.redns.redis-cloud.com"
redis_port="19179"
redis_db=0
redis_password="GlTO5JYBYVaT4bGgEKhpAkR2oyxxbyg4"
redis_username="default"
redis_index = "V1"
gpt_key = os.environ.get("OPENAI_API_KEY")

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