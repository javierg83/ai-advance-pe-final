# Asistente Médico Virtual - Atención PrimarIA

![Atención PrimarIA](static/logo-medium.png)

Este repositorio contiene el código fuente para un **Asistente Médico basado en Inteligencia Artificial**. El sistema permite la interacción con un paciente, recogiendo sus datos personales, síntomas y realizando una recomendación médica a través de una IA, junto con la generación de una orden médica.

## Entrega Final Trabajo Curso Advanced Prompt Engineering

Este proyecto es parte del curso **Advanced Prompt Engineering, de la escuela de Ingeniería de la Universidad Adolfo Ibáñez** y tiene como objetivo demostrar la integración de modelos de lenguaje, uso de asistentes, moderación de contenido y generación de recomendaciones médicas en un entorno en producción.

### Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Modo de Ejecución](#modo-de-ejecución)
   1. [**Modo Web (Flask)**](#1-modo-web-flask)
   2. [**Modo Consola**](#2-modo-consola)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Licencia](#licencia)

## Instalación

 Parar requisitos previos e instrucciones para instalar el **Asistente Médico** en tu entorno local con Python, revisa el archivo de instalación [`INSTALL.md`](INSTALL.md).

## Uso

El flujo de trabajo general de Asistente es:

- El paciente entrega sus datos básicos para iniciar la sesión.
- El asistente le solicita información sobre los síntomas que lo traen a solicitar Atención primaria.
- Cuando los recibe, hace preguntas adicionales para precisar mejor.
- Realiza una recomendación médica basada en los datos recibidos.
- Se genera una orden médica, si el nivel de certeza es suficiente para tener un diagnóstico.

## Modo de Ejecución

El asistente médico puede ser ejecutado en dos modos, como Servidor Web, o en modo Consola de Texto, para utilizarlo localmente.

### 1. **Modo Web (Flask)**

Para ejecutar el asistente en modo web, donde el paciente puede interactuar a través de un navegador:

```powershell
python main.py --runserver --port 8000 --host localhost
```

Luego accede a `http://localhost:8000/` desde tu navegador para interactuar con la aplicación.

### 2. **Modo Consola**

Para ejecutar el asistente en modo consola, donde el usuario interactúa a través de la terminal, debes ejecutar el comando:

```powershell
python main.py
```

## Estructura del Proyecto

El proyecto está organizado en los siguientes directorios y archivos principales:

```bash
ai-advance-pe-final/
│
├── data/                        # Directorio para archivos de datos de entrada e intermedios
│   └── PreparacionBaseDatos.py  # Programa de transformación de datos y carga en Redis
├── docs/                        # Directorio para Documentación técnica más detallada
├── static/                      # Directorio de objetos estáticos para web
├── templates/                   # Directorio para Plantillas de páginas web
│
├── main.py                      # Archivo principal que ejecuta la aplicación
├── requirements.txt             # Lista de dependencias necesarias
├── .env                         # Variables de entorno (API Key, claves secretas, etc.)
├── asistenteMedico.PY           # Módulo para la lógica del asistente médico
├── consultaBaseConocimiento.py  # Módulo para la base de conocimiento
├── datosBasicosYSintomas.py     # Módulo para gestión de datos del paciente
├── generacionOrdenMedica.py     # Módulo para la generación de órdenes médicas
├── moderador.py                 # Módulo para moderación de consultas
└── supervisorMedico.py          # Módulo para validación de la recomendación médica
```

## Licencia

Este proyecto está bajo la **Apache License 2.0**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
