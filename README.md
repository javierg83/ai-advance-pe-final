
Entrega Final Trabajo Curso Advanced Prompt Engineering

# Asistente Médico - Proyecto de Título

Este repositorio contiene el código fuente para un **Asistente Médico basado en Inteligencia Artificial**. El sistema permite la interacción con un paciente, recogiendo sus datos personales, síntomas y realizando una recomendación médica a través de una IA, junto con la generación de una orden médica.

Este proyecto es parte del curso **Advanced Prompt Engineering** y tiene como objetivo demostrar la integración de modelos de lenguaje, moderación de contenido y generación de recomendaciones médicas en un entorno de producción.

### Tabla de Contenidos
1. [Instalación](#instalación)
2. [Uso](#uso)
3. [Despliegue](#despliegue)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Requisitos](#requisitos)
6. [Licencia](#licencia)
7. [Detalle de Flujo Técnico](#detalle-de-flujo-técnico)

## Instalación

Para instalar el **Asistente Médico** en tu entorno local con Python, sigue los pasos a continuación.

### Requisitos previos
- **Python 3.10.11** 
- **Gestor de paquetes pip**
- **Windows 10 o superior**

### Pasos de instalación:
1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/usuario/asistenteMedico.git
   cd asistenteMedico
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

Este proyecto está bajo la **Apache License 2.0**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Detalle de Flujo Técnico

**Inicio del Sistema**
1. El sistema se puede ejecutar en dos modos:
   - **Modo CLI (Consola)**: Llamando directamente al script principal.
   - **Modo Web (Flask)**: Ejecutando el servidor Flask y accediendo a la interfaz web.

2. Se carga el archivo de configuración y las variables de entorno desde `.env` usando `dotenv`.
3. Se configura el logging para registrar eventos del sistema.

**Configuración de la API de OpenAI**
1. Se obtiene la clave de API desde las variables de entorno.
2. Se inicializa el cliente de OpenAI con la clave de autenticación.

**Modo CLI: Flujo de Consulta**
1. Se llama a `datosBasicosYSintomas.obtener_datos_paciente()` para solicitar datos del usuario.
2. Se registran los síntomas con `datosBasicosYSintomas.registrar_sintomas()`.
3. Se generan preguntas adicionales usando `datosBasicosYSintomas.realizar_preguntas_relevantes()`.
4. Se ejecuta la validación de moderación con `moderador.analisis_moderador_generico()`.
5. Si la consulta es válida, se realiza una búsqueda en la base de conocimiento con `consultaBaseConocimiento.busqueda_base_conocimiento()`.
6. Se genera una recomendación médica con `asistenteMedico.realizar_recomendacion_medica()`.
7. Se ejecuta la revisión médica con `supervisorMedico.revision_recomendacion_medica()`.
8. Si aplica, se genera una orden médica con `generacionOrdenMedica.generar_orden_medica()`.
9. Se muestra la recomendación y la posible orden médica en la consola.

**Modo Web: Flujo de Consulta**
1. Se inicia la aplicación Flask con `app = Flask(__name__)`.
2. Se define `app.secret_key` para gestionar sesiones de usuario.

**Rutas y Controladores**
- **/** (Registro del Paciente)
   - Se muestra `registro.html` para recopilar datos del usuario.
   - Se validan los datos con `datosBasicosYSintomas.validar_datos_paciente_web()`.
   - Si la validación es exitosa, los datos se almacenan en la sesión.
- **/sintomas** (Registro de Síntomas)
   - Se muestra `sintomas.html` donde el usuario ingresa sus síntomas.
   - Los síntomas se procesan con `datosBasicosYSintomas.parse_sintomas_web()` y se guardan en la sesión.
- **/preguntas** (Generación de Preguntas)
   - Se obtienen datos y síntomas de la sesión.
   - Se generan preguntas con `datosBasicosYSintomas.realizar_preguntas_relevantes_web()`.
   - Se muestra `preguntas.html` con la lista de preguntas generadas.
- **/resultado** (Recomendación Médica)
   - Se validan los datos con `moderador.moderacion_pasada_web()`.
   - Si la moderación es exitosa, se busca información en `consultaBaseConocimiento.busqueda_base_conocimiento()`.
   - Se genera una recomendación con `asistenteMedico.realizar_recomendacion_medica_web()`.
   - Se revisa la recomendación con `supervisorMedico.revision_recomendacion_medica_web()`.
   - Si aplica, se genera una orden médica con `generacionOrdenMedica.generar_orden_medica_web()`.
   - Se muestra `resultado.html` con la recomendación médica y la opción de descarga de la orden.
- **/download** (Descarga de Orden Médica)
   - Se recupera el archivo generado y se envía al usuario mediante `send_from_directory()`.

**Base de Conocimiento y OpenAI**
1. Se realiza una búsqueda en la base de conocimiento utilizando `consultaBaseConocimiento.busqueda_base_conocimiento()`.
2. Se utilizan modelos de OpenAI para generar preguntas relevantes y recomendaciones médicas.

**Manejo de Sesión y Datos Temporales**
1. En la versión web, se utilizan sesiones Flask (`session`) para almacenar datos temporales del usuario.
2. En la versión CLI, los datos se manejan en memoria durante la ejecución del programa.

**Manejo de Errores y Logging**
1. Se implementa `logging.error()` para capturar errores críticos.
2. Se utilizan validaciones en cada paso del proceso para evitar datos inválidos.

**Seguridad y Cumplimiento**
1. Se implementa la validación de datos del paciente.
2. Se garantiza la seguridad de la clave de API de OpenAI.
3. Se restringe el acceso a archivos médicos generados.

**Finalización del Flujo**
1. En CLI, el programa finaliza después de mostrar la recomendación médica.
2. En Web, el usuario puede volver al inicio o descargar la orden médica generada.
