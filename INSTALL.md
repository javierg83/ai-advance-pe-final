# Guía de Instalación

## Requisitos Previos

- Python 3.10.11
- Gestor de paquetes `pip`
- Windows 10 o superior

## Pasos de Instalación

1. Clonar el repositorio y navegar al directorio del proyecto:

    ```powershell
    git clone 'https://github.com/javierg83/ai-advance-pe-final.git'
    cd 'ai-advance-pe-final'
    ```

2. Crear y activar un entorno virtual:

    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. Instalar paquetes requeridos desde `requirements.txt`:

    ```powershell
    pip install -r requirements.txt
    ```

## Ejecutar la Aplicación

Para iniciar la aplicación:

```powershell
uvicorn main:app --host=0.0.0.0 --port=8000
```

### Notas

- El puerto puede configurarse usando la variable de entorno PORT.
- Asegúrese de tener todas las variables de entorno configuradas antes de ejecutar.
- Para desarrollo local, puede usar `uvicorn main:app --reload`.
