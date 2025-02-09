Entrega Final Trabajo Curso Advanced Prompt Engineering

# Asistente Médico - Proyecto de Título

Este repositorio contiene el código fuente para un Asistente Médico basado en Inteligencia Artificial. El sistema permite la interacción con un paciente, recogiendo sus datos personales, síntomas y realizando una recomendación médica a través de una IA, junto con la generación de una orden médica.

### Tabla de Contenidos
1. Instalación(#instalación)
2. Uso(#uso)
3. Despliegue(#despliegue)
4. Estructura del Proyecto(#estructura-del-proyecto)
5. Requisitos(#requisitos)
6. Licencia(#licencia)

## Instalación

Para instalar el Asistente Médico en tu entorno local en Python, sigue los siguientes pasos:

### Requisitos previos
- **Python 3.7+**
- **pip** (gestor de paquetes de Python)

### Pasos de instalación:
1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/usuario/asistente-medico.git
   cd asistente-medico
   ```

2. **Crea un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   venv/bin/activate
   ```

3. **Instala las dependencias necesarias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   Se configuran desde un archivo `.env` con las siguientes claves:
   ```
   OPENAI_API_KEY=tu_clave_api_de_openai
   REDIS=configuraciones_base_de_datos
   FLASK_SECRET_KEY=una_clave_secreta
   ```

## Uso

El asistente médico puede ser ejecutado en dos modos:

### 1. **Modo Consola**
   Para ejecutar el asistente en modo consola, donde el usuario interactúa a través de la terminal:

   ```bash
   python main.py
   ```

   El flujo de trabajo de este modo es el siguiente:
   - El asistente recopila los datos del paciente.
   - El asistente registra los síntomas y hace preguntas relevantes.
   - Realiza una recomendación médica basada en los datos recibidos.
   - Se genera una orden médica si el nivel de certeza es mayor a un umbral.

### 2. **Modo Web (Flask)**
   Para ejecutar el asistente en modo web, donde el paciente puede interactuar a través de un navegador:

   ```bash
   python main.py --runserver --port 8000 --host localhost
   ```

   Luego accede a `http://localhost:8000/` desde tu navegador para interactuar con la aplicación.

   En este modo, los pasos son similares a los del modo consola, pero el flujo se maneja a través de una interfaz web interactiva.

## Despliegue

### Despliegue en un servidor:
1. **Configura el entorno de producción:**
   Asegúrate de tener un servidor adecuado, en este caso **Heroku**.

2. **Instala las dependencias:**
   Sigue los mismos pasos de instalación de la sección anterior.

3. **Configura el servidor:**
   Asegúrate de tener las variables de entorno correctamente configuradas en tu servidor.

4. **Ejecuta el servidor:**
   Para desplegar en producción, utilizaremos Flask
   ```

   Esto ejecutará la aplicación en un entorno adecuado para producción.

## Estructura del Proyecto

El proyecto está organizado en los siguientes directorios y archivos:

```
asistente-medico/
│
├── main.py                # Archivo principal que ejecuta la aplicación
├── requirements.txt       # Lista de dependencias necesarias
├── .env                   # Variables de entorno (API Key, claves secretas, etc.)
├── /asistenteMedico       # Módulo para la lógica del asistente médico
├── /consultaBaseConocimiento  # Módulo para la base de conocimiento
├── /datosBasicosYSintomas # Módulo para gestión de datos del paciente
├── /generacionOrdenMedica # Módulo para la generación de órdenes médicas
├── /moderador             # Módulo para moderación de consultas
└── /supervisorMedico      # Módulo para validación de la recomendación médica
```

## Requisitos

- **Flask**: Framework web utilizado para la interfaz web.
- **OpenAI**: Se utiliza la API de OpenAI para generar recomendaciones médicas.
- **dotenv**: Para cargar variables de entorno desde un archivo `.env`.
- **Rich**: Utilizado para mejorar la presentación de los logs y trazas de error.

Para instalar las dependencias, ejecuta:

```bash
pip install -r requirements.txt
```

## Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
