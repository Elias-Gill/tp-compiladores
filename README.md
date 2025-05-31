# Pre-procesado 

## Grabacion de audio

Los audios fueron grabados por los integrantes utilizando una conversacion guionada, usando en
lo posibles "jopara", pronunciacion natural y ruido de fondo para poder simular un ambiente mas
realista.

Las conversaciones de audio se encuentran dentro de la carpeta `audios`.

## Conversion de audio a texto

Para extraer el texto de las grabaciones de audio podemos utiliza cualquiera de las siguiente
paginas:

- https://transcri.io/es
- https://app.transcribetube.com/

Luego utilizamos chatgpt a fin de identificar entre agentes y clientes.
Esto lo hacemos con el siguiente prompt:

```text
Identifica y separa los diálogos entre el Agente y el Cliente en el siguiente texto:
<insertar el texto>
Dame el resultado en el formato 'Agente:' y 'Cliente:'
``` 

### Textos analizables (Test)

El resultado de este proceso son las conversaciones de audio trasncriptas a texto, las cuales
se guardan dentro de la carpeta `test/`.

````
prueba.txt
prueba-texto1-negativo.txt
prueba-texto2-positivo.txt
prueba-texto3-positivo.txt
prueba-texto4-neutral.txt
prueba-texto5-negativo.txt
````

Un ejemplo del formato de dichas conversaciones es el siguiente:

```txt
Agente: Buenos días, ¡Gracias por contactar con el servicio al cliente de ConexiónNet! Mi
nombre es Yamil. ¿En qué puedo ayudarle hoy?

Cliente: Mira, estoy harto de llamarles una y otra vez. Mi internet es un desastre, y nadie ha
hecho nada. Pago por 100 Mbps y estoy recibiendo una velocidad que es una broma. ¡Es
inaceptable!

Agente: Lamento mucho escuchar eso, señor. Entiendo que debe ser frustrante, pero estoy aquí
para ayudarle. ¿Podría proporcionarme sus datos completos y el número de cuenta para poder
revisar su situación?

...
```

# Tokenizacion

Para el proceso de tokenizacion se optaron por dos posibles soluciones, una basada en
diccionarios (hashmaps) y otra utilizando un AFD generado a partir de la tabla de simbolos.

Dado que tenemos tiempo de sobra, ambas opciones fueron implementadas a fin de ver los pros y
contras de ambas implementaciones.

Ambos tipos de tokenizador son intercambiables, dado que la unica condicion es que ambos
cuenten con la funcion "tokenizar" para que el programa funcione.
El tokenizador `por defecto` del programa es el de tipo AFD, pero puede ser modificado
utilizando la flag `--hashmap` para utilizar el tokenizador basado en diccionarios.

NOTA:
El tokenizador de tipo AFD vuelca el AFD construido dentro del archivo en `output/afd.json`.

Los tokens posibles son:
- `TOKEN_SALUDO`
- `TOKEN_DESPEDIDA`
- `TOKEN_IDENTIFICACION`
- `TOKEN_PROHIBIDA`
- `TOKEN_SENTIMIENTO`
- `TOKEN_DESCONOCIDO`
- `TOKEN_AGENTE`
- `TOKEN_CLIENTE`
- `TOKEN_SIGNO_PUNTUACION`

## Implementación con AFD

### Estructura del AFD

El autómata finito determinista (AFD) está implementado como un diccionario con la siguiente
estructura:

```python
{
    "initial": "start",  # Estado inicial
    "states": {
        "state_name": {
            "transitions": {},      # Transiciones desde este estado
            "is_final": bool,       # Si es estado final
            "token_type": str,      # Tipo de token si es final
            "puntuacion": int       # Puntuación asociada si es final
        },
        # ... más estados ...
    }
}
```

El AFD se construye dinámicamente durante la inicialización del tokenizador, cargando todas las
frases de los diferentes tipos (saludos, despedidas, etc.) desde la `TablaSentimientos`.

### Transiciones

Las transiciones se generan automáticamente para cada frase en los diccionarios de la
`TablaSentimientos`:

1. Para cada frase (ej.
   "hola"), se convierte en una secuencia de caracteres
2. Se crea un estado por cada carácter con el formato:
   `{estado_actual}_{caracter}_{tipo}`
3. Las transiciones se almacenan como diccionarios donde:
   - La clave es el carácter de entrada
   - El valor es una lista de estados destino

### Evaluación de Lexemas

El proceso de evaluación de lexemas ocurre en `_tokenizar_con_afd`:

1. Se mantiene un conjunto de estados activos
2. Para cada carácter de entrada:
   - Se calculan los nuevos estados alcanzables
   - Si se llega a un estado final, se registra como posible token válido
3. Se selecciona el token más largo encontrado (maximal munch)
4. Si no se encuentra ningún token reconocido por el AFD, marca como "DESCONOCIDO"

El proceso completo de tokenización:

1. Procesamiento por caracteres:
   - Signos de puntuación:
     tokens individuales
   - Identificadores de hablante:
     tokens especiales
   - Texto:
     procesado por el AFD
2. Para texto no reconocido:
   - Se marca como "DESCONOCIDO"

### Ventajas

1. **Eficiencia**:
   El AFD permite reconocer frases completas en tiempo lineal
2. **Precisión**:
   Prioriza frases completas sobre palabras sueltas
3. **Extensibilidad**:
   Fácil agregar nuevos tipos de **frases** mediante la tabla de sentimientos

### Desventajas

- Mayor uso de memoria (para almacenar el AFD).
- Mayor tiempo de inicializacion (construccion del AFD).
- Costoso realizar actualizaciones del AFD en tiempo de ejecucion.

## Implementación con Hashmap

### Estructura del Tokenizador

El tokenizador utiliza una estructura basada en:
- **Tabla de Hash (diccionario)**:
  Almacenada en `TablaSentimientos` que mapea frases/palabras a sus tipos y puntuaciones
  correspondientes
- **Expresiones regulares**:
  Para identificar patrones especiales como:
  - Hablantes (`agente:` o `cliente:`)
  - Palabras individuales y signos de puntuación
- **Clase `Token`**:
  Representa cada token con:
  - `type`:
    Tipo del token (constantes definidas)
  - `valor`:
    Texto original
  - `puntuacion`:
    Valor numérico asociado (para sentimientos)

### Proceso de Tokenización

1. **Preprocesamiento**:
   - Normaliza el texto a minúsculas
   - Añade espacios alrededor de `agente:` y `cliente:`

2. **Extracción de unidades**:
   - Divide el texto en palabras y signos de puntuación usando regex

3. **Búsqueda por longitud variable**:
   - Intenta hacer match primero con frases de 3 palabras
   - Si no encuentra, prueba con 2 palabras
   - Finalmente busca palabras individuales

4. **Asignación de tipos**:
   - Usa la función `asignar_tipo` para convertir los tipos de la tabla a constantes de token
   - Maneja casos especiales (signos de puntuación, hablantes) separadamente

5. **Generación de tokens**:
   - Crea objetos `Token` con la información recolectada

### Ventajas de esta Implementación

1. **Simplicidad**:
   - Más fácil de implementar y entender que un AFD
   - No requiere construcción de estados complejos

2. **Flexibilidad**:
   - Maneja frases de longitud variable naturalmente (1-3 palabras)
   - Permite añadir nuevos patrones modificando solo la tabla de hash

4. **Mantenibilidad**:
   - Fácil agregar nuevos patrones o modificar los existentes
   - Separación clara entre datos (tabla) y lógica (tokenizador)

## Ejemplo de Uso

```python
tabla = TablaSentimientos()  # Configurada con los patrones
tokenizer = HashTokenizer(tabla)
tokens = tokenizer.tokenizar("agente: Hola, ¿cómo estás?")
```
### Ejemplo de Flujo de Tokenización

Para la entrada "Hola agente:
¿Cómo estás?":

1. Preprocesamiento:
- Añade espacios alrededor de "agente:"
- Divide en:
  ["hola", "agente", ":", "¿", "cómo", "estás", "?"]

2. Procesamiento:
- "hola" → TIPO_SALUDO (si está en la tabla)
- "agente" + ":" → TOKEN_AGENTE
- ":" → TOKEN_SIGNO_PUNTUACION
- "¿" → TOKEN_SIGNO_PUNTUACION
- "cómo estás" → Frase de 2 palabras (si está en la tabla)
- "?" → TOKEN_SIGNO_PUNTUACION

Esta implementación es particularmente adecuada para escenarios donde:
- Las frases a reconocer son relativamente cortas
- Se prioriza la simplicidad sobre la optimización extrema
- El diccionario de palabras/frases cambia con frecuencia


## Comparación AFD vs Hashmap

| Característica          | HashTokenizer                 | AFDTokenizer                |
|-------------------------|-------------------------------|-----------------------------|
| Complejidad             | Baja                          | Alta                        |
| Tiempo de construcción  | Inmediato                     | Requiere construir el AFD   |
| Manejo de frases        | Búsqueda por longitud         | Reconocimiento exacto       |
| Eficiencia              | Bueno para textos cortos      | Mejor para textos largos    |
| Precisión               | Depende del orden de búsqueda | Exacto por construcción     |


# Análisis de Sentimiento

Utiliza una tabla de sentimientos que asocia palabras con puntajes emocionales, el programa
calcula un puntaje total que indica si el sentimiento general del texto es positivo, negativo o
neutral.
Esto se logra mediante la iteración a través de los lexemas aceptados y la acumulación de sus
puntajes.

### Salidas

El algoritmo realiza un reporte de la conversación dividido en tres partes:

```txt
├───output
│       [afd.json]     # no se genera con 'hashmap'
│       reporte.txt
│       tokens.txt
```

1. `reporte.txt`:
   Ofrece un análisis del texto procesado, incluyendo el sentimiento general (positivo,
   negativo o neutral), el puntaje total de las palabras, y listas de palabras positivas y
   negativas, así como resultados de la verificación del protocolo de atención.
2. `tokens.txt`:
   se presenta una tabla que muestra los lexemas identificados, sus correspondientes tokens y
   patrones asociados.
3. `afd.json`:
   detalla la estructura del Autómata Finito Determinista (AFD), incluyendo el estado inicial,
   los estados finales y las transiciones, que reflejan cómo se mueven entre estados en función
   de los lexemas detectados.

### Conclusiones

El Tokenizador AFD es una herramienta robusta y versátil para el procesamiento de texto y
análisis de sentimientos.
Su diseño basado en un AFD permite una categorización eficiente y un seguimiento del uso de
lexemas, mientras que su capacidad de análisis de sentimientos ofrece una visión profunda de la
percepción emocional de los textos procesados.
En un mundo donde la interacción humana y la comunicación son cada vez más mediadas por la
tecnología, herramientas como esta son esenciales para mejorar la comprensión y la respuesta a
las necesidades de los usuarios.
