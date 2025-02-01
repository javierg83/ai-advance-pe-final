# Uso seguro de `API keys`

El problema de almacenar y utilizar las `API keys` se puede resolver al utilizar variables de entorno, tanto al momento de desarrollar, como de ejecutar.

Referencia: <https://medium.com/@alwinraju/%EF%B8%8F-storing-environment-variables-and-api-keys-in-python-475144b2f098>

## Cambios al código python para usar variables de ambiente y almacenar `API keys`

En vez de:

```python
import configparser
...

#PARAMETRIA
config = configparser.ConfigParser()
config.read('config.ini')

openai_api_key = config['openai']['api_key']
```

se cambia por:

```python
from dotenv import load_dotenv
...
# Load the environment variables from .env file
load_dotenv()

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

## Almacenamiento local de `API keys` en ambiente desarrollo

Debemos usar un archivo de nombre `.env`, donde se definen localmente los valores de las llaves. Este archivo no
 se lee en ningún momento por nuestro programa, si no que el entorno de desarrollo como Visual Studio 
Code, lee el contenido y las agrega como variables de entorno a la hora de ejecutar nuestro programa dentro de ese ambiente.

```powershell
from dotenv import load_dotenv
...
# Load the environment variables from .env file
load_dotenv()

# Configuración de las keys para APIs
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

A la hora de escribir o leer nuestros programas desde el repositorio Github, este archivo se excluye de manera explícita de la información guardada en en el repositorio, quedando solo en nuestro computador local. Esto se implementa con la existencia de un archivo llamado `.gitignore` en el mismo directorio donde esté nuestro archivo con llaves. Es en este donde vamos a agregar una línea con el nombre `.env`, y así se ignora efectivamente cuando se arman los commits.

**Por completar :  Forma de implementar cuando se hace deployment en la nube.** 
