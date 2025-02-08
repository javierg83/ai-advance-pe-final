#!/usr/bin/env python

"""Este modulo se ocupa de la preparación e importación de datos en un archivo .csv, hasta cargarlos en una base de datos en Redis, que se utiliza como contexto para las consultas del usuario."""

import os
from dotenv import find_dotenv, load_dotenv

import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.redis import Redis
from langchain_openai.embeddings import OpenAIEmbeddings
from rich import (
    print,  # sobreescribe la función print, para utilizar formato con colores
    traceback
)

# activa traceback para mejorar la depuración de excepciones
traceback.install()

# Directorios con rutas corregidas a estilo python
output_dir = ".//data"
input_file = ".//data//claves.csv"


def create_enfermedad_details_text(row) -> str:
    """Generar el texto a almacenar en el archivo .txt para cada enfermedad."""
    return (
        f"Enfermedad: {row['nombre']}\n"
        + f"Sintoma Principal: {row['sintoma_1']}\n"
        + f"Sintoma Secundario: {row['sintoma_2']}\n"
        + f"Sintoma Normal: {row['sintoma_3']}\n"
        + f"Sintoma Medio: {row['sintoma_4']}\n"
        + f"Sintoma Bajo: {row['sintoma_5']}\n"
        + f"Sintoma sin importancia: {row['sintoma_6']}\n"
        + f"Solucion: {row['solucion']}\n"
        + f"Medicamento: {row['medicamento']}\n"
        + f"Licencia Medica: {row['licencia_medica']}\n"
    )


def main():
    global output_dir, input_file
    # Buscar el archivo .env en los lugares posibles
    if load_dotenv(find_dotenv(usecwd=True)):
        print("[bold]Archivo '.env' cargado exitosamente.[/bold]")

    # Crear la carpeta si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Obtener la ruta absoluta del archivo de entrada
    input_file = os.path.abspath(input_file)
    # Leer el archivo CSV
    df = pd.read_csv(input_file)
    print(f"[bold]Archivo de entrada '{input_file}' cargado exitosamente.[/bold]")

    # Iterar sobre el DataFrame y guardar cada enfermedad como un archivo .txt
    for idx, row in df.iterrows():
        enfermedad_name = row["nombre"].replace(
            "/", "-"
        )  # Asegurar nombres de archivo válidos
        file_name = f"{enfermedad_name}.txt"
        file_path = os.path.join(output_dir, file_name)

        # Escribir los detalles en un archivo .txt
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(create_enfermedad_details_text(row))

    print(
        f"[bold]Datos Procesados: {idx + 1} archivos generados en: '{os.path.normpath(os.path.abspath(output_dir))}'.[/bold]"
    )

    input_dir = os.path.dirname(input_file)

    # Lectura de claves desde el entorno
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    redis_db = os.environ.get("REDIS_DB")
    redis_password = os.environ.get("REDIS_PASSWORD")
    redis_username = os.environ.get("REDIS_USERNAME")
    redis_index = os.environ.get("REDIS_INDEX")
    gpt_key = os.environ.get("OPENAI_API_KEY")

    # Crear embeddings usando la API de OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=gpt_key)

    # Iterar sobre cada archivo en el directorio y cargarlo a REDIS
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            file_path = os.path.normpath(os.path.join(input_dir, filename))

            # Cargar el documento desde el archivo de texto
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()

            # Dividir el documento en fragmentos de tamaño adecuado para embeddings
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(documents)
            number_chunks = len(docs)

            # Cargar los documentos divididos a REDIS con embeddings
            vectorstore = Redis.from_documents(
                docs,
                embeddings,
                redis_url=f"redis://{redis_username}:{redis_password}@{redis_host}:{redis_port}/{redis_db}",
                index_name=redis_index,
            )

            print(
                f"[bold]Documentos del archivo '{filename}' fueron cargados exitosamente en REDIS, en",
                f"{ {number_chunks} + 'chunks' if number_chunks > 1 else 'un solo chunk' }.[/bold]"
            )

    print(
        "[bold green]Todos los archivos han sido procesados y cargados en REDIS.[/bold green]"
    )


if __name__ == "__main__":
    main()
