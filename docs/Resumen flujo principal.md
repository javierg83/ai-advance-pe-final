# Detalle de Flujo Técnico

## Resumen funcional

### Inicio del Sistema

1. El sistema se puede ejecutar en dos modos:
   - **Modo CLI (Consola)**: Llamando directamente al script principal.
   - **Modo Web (Flask)**: Ejecutando el servidor Flask y accediendo a la interfaz web.

2. Se carga el archivo de configuración y las variables de entorno desde `.env` usando `dotenv`.
3. Se configura el logging para registrar eventos del sistema.

### Configuración de la API de OpenAI

1. Se obtiene la clave de API desde las variables de entorno.
2. Se inicializa el cliente de OpenAI con la clave de autenticación.

### Modo CLI: Flujo de Consulta

1. Se llama a `datosBasicosYSintomas.obtener_datos_paciente()` para solicitar datos del usuario.
2. Se registran los síntomas con `datosBasicosYSintomas.registrar_sintomas()`.
3. Se generan preguntas adicionales usando `datosBasicosYSintomas.realizar_preguntas_relevantes()`.
4. Se ejecuta la validación de moderación con `moderador.analisis_moderador_generico()`.
5. Si la consulta es válida, se realiza una búsqueda en la base de conocimiento con `consultaBaseConocimiento.busqueda_base_conocimiento()`.
6. Se genera una recomendación médica con `asistenteMedico.realizar_recomendacion_medica()`.
7. Se ejecuta la revisión médica con `supervisorMedico.revision_recomendacion_medica()`.
8. Si aplica, se genera una orden médica con `generacionOrdenMedica.generar_orden_medica()`.
9. Se muestra la recomendación y la posible orden médica en la consola.

### Modo Web: Flujo de Consulta

1. Se inicia la aplicación Flask con `app = Flask(__name__)`.
2. Se define `app.secret_key` para gestionar sesiones de usuario.

#### Rutas y Controladores

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

### Base de Conocimiento y OpenAI

1. Se realiza una búsqueda en la base de conocimiento utilizando `consultaBaseConocimiento.busqueda_base_conocimiento()`.
2. Se utilizan modelos de OpenAI para generar preguntas relevantes y recomendaciones médicas.

### Finalización del Flujo

1. En CLI, el programa finaliza después de mostrar la recomendación médica.
2. En Web, el usuario puede volver al inicio o descargar la orden médica generada.

## Otros requerimientos no funcionales

### Manejo de Sesión y Datos Temporales

1. En la versión web, se utilizan sesiones Flask (`session`) para almacenar datos temporales del usuario.
2. En la versión CLI, los datos se manejan en memoria durante la ejecución del programa.

### Manejo de Errores y Logging

1. Se implementa `logging.error()` para capturar errores críticos.
2. Se utilizan validaciones en cada paso del proceso para evitar datos inválidos.

### Seguridad y Cumplimiento

1. Se implementa la validación de datos del paciente.
2. Se garantiza la seguridad de la clave de API de OpenAI.
3. Se restringe el acceso a archivos médicos generados.
