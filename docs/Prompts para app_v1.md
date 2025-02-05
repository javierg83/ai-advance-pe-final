# Prompts para app

## Prompt 1 - o3-mini-high

Ayúdame a crear una app utilizando FastAPI y uvicorn, donde mi clase principal SesionRecomendaciones, tiene los atributos:
- nombre: str
- edad: int
- sexo: str
- peso: int
- id_instancia: int
- memoria
- anexos: List[str]

Considerar que los atributos 'nombre, edad, sexo, peso' deben tener asociados una función de validación  siguiendo el patrón 'validación_<campo>' (ej. para 'nombre' es 'validación_nombre'), definidas en otra parte del código y que sólo deben invocarse en la creación del objeto. El resto de los atributos se deben asignar cero, none y lista vacía respectivamente.

Se requiere implementar los siguientes mensajes como métodos de la clase principal con los siguientes atributos de entrada y salida:

Mensaje Init
- nombre
- edad
- sexo
- peso
Respuesta mensaje:
- Resultado: éxito o error
- Detalle: en caso de error se escribe la lista de problemas detectados. Si todo fue exitoso viene el texto de bienvenida y la solicitud de síntomas.
- Id de sesión: solo en el caso de éxito si no irá vacío.

Mensaje Ask
- Id de sesión
- respuesta de usuario: en el primer mensaje de este tipo iría la lista de síntomas. Posteriormente vendrían las respuestas del usuario a las preguntas de clarificación de nuestros agentes.
Respuesta mensaje:
- Resultado: str con éxito o error
- Detalle: str. En caso de error se escribe la lista de problemas detectados: esto podría ocurrir como resultado de alguno de los moderadores. En caso de éxito, podrían ser nuevas preguntas de clarificación o el resultado de la consulta.
- tipo de respuesta: valor string desde lista de literales ["inicial", "sintomas", "clarificación", "resultado"].
- documento anexo: este campo contendría el archivo cifrado en texto plano.

---

## Prompt 2 - o3-mini-high - ajuste de métodos

Ayúdame a crear una app utilizando FastAPI y uvicorn, donde mi clase principal SesionRecomendaciones, tiene los atributos:
- nombre: str
- edad: int
- sexo: str
- peso: int
- id_instancia: int
- memoria
- anexos: List[str]

Considerar que los atributos 'nombre, edad, sexo, peso' deben tener asociados una función de validación  siguiendo el patrón 'validación_<campo>' (ej. para 'nombre' es 'validación_nombre'), definidas en otra parte del código y que sólo deben invocarse en la creación del objeto. El resto de los atributos se deben asignar cero, none y lista vacía respectivamente.

Se requiere implementar los siguientes mensajes endpoint, llamando a la clase principal con los siguientes atributos de entrada y salida:

Mensaje Init
- nombre
- edad
- sexo
- peso
Procesamiento del mensaje:
- Debe instanciar una nueva clase SesiónRecomendaciones, con los valores entregados.
- Si hay errores, Debe recopilarlos.
- Si no hay errores, debe asignar un número de sesión elegido al azar. Ese número de sesión debe ser guardado En  las variables globales sesiones_activas: Set[int], detalle_sesiones: Dict[], guardando el id sesión y la fecha y hora de la creación en formato ISO.
Respuesta mensaje:
- Resultado: éxito o error
- Detalle: en caso de error se escribe la lista de problemas detectados. Si todo fue exitoso viene el texto de bienvenida y la solicitud de síntomas.
- Id de sesión: solo en el caso de éxito si no irá vacío.

Mensaje Ask
- Id de sesión
- respuesta de usuario: en el primer mensaje de este tipo iría la lista de síntomas. Posteriormente vendrían las respuestas del usuario a las preguntas de clarificación de nuestros agentes.
Respuesta mensaje:
- Resultado: str con éxito o error
- Detalle: str. En caso de error se escribe la lista de problemas detectados: esto podría ocurrir como resultado de alguno de los moderadores. En caso de éxito, podrían ser nuevas preguntas de clarificación o el resultado de la consulta.
- tipo de respuesta: valor string desde lista de literales ["inicial", "sintomas", "clarificación", "resultado"].
- documento anexo: este campo contendría el archivo cifrado en texto plano.

---
