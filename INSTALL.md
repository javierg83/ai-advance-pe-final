# Guía de Instalación

## Requisitos Previos

- Python 3.10
- Gestor de paquetes `pip`
- Windows 10 o superior

## Pasos de Instalación

1. Clonar el repositorio y navegar al directorio del proyecto

    ```powershell
    git clone 'https://github.com/javierg83/ai-advance-pe-final.git'
    cd 'ai-advance-pe-final'
    ```

2. Crear y activar un entorno virtual

    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. Instalar paquetes requeridos desde `requirements.txt`

    ```powershell
    pip install -r requirements.txt
    ```

4. Configurar las variables de entorno

   Se configuran creando un archivo `.env` en el mismo directorio del proyecto, con el siguiente patrón:

    ```bash
    # reemplaza con tu clave_api_de_openai
    OPENAI_API_KEY="XXXXXXXXXXXXXXXXXXXXXXXX"

    # reemplaza con tus datos y claves de Redis
    REDIS_HOST="XXXXXXXXXXXXXXXX"
    REDIS_PORT="000"
    REDIS_DB=000
    REDIS_PASSWORD="XXXXXXXXXXXXXXXX"
    REDIS_USERNAME="XXXX"
    REDIS_INDEX="XXXX"

    # genera una clave muy secreta para el servidor web
    FLASK_SECRET_KEY="XXXXXXXXXXXXXXXX"
    ```

    Para mayor conveniencia, existe un template de este archivo llamado [`env-emplate.txt`](env-emplate.txt), al cual le puedes cambiar el nombre a `.env`, y completar con tus claves propias.
