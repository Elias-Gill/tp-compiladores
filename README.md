# Tokenización 

## Función

### Textos analizables (Test)

````
prueba.txt
prueba-texto1-negativo.txt
prueba-texto2-positivo.txt
prueba-texto3-positivo.txt
prueba-texto4-neutral.txt
prueba-texto5-negativo.txt
````

### Convertir audio en texto

- Página 1:
  https://transcri.io/es
- Página 2:
  https://app.transcribetube.com/auth/login

Luego usar chatgpt con el promt: 

```text
Identifica y separa los diálogos entre el Agente y el Cliente en el siguiente texto:
<insertar el texto>
Dame el resultado en el formato 'Agente:' y 'Cliente:'
``` 

### Estructura del AFD

La clase `AFD` representa un autómata que gestiona estados, transiciones y lexemas.
Cada vez que se evalua un lexema, el AFD determina si puede pasar de un estado a otro basado en
las transiciones definidas.

El AFD se construye inicialmente con un estado inicial y varios estados finales, que
representan categorías de lexemas:
saludos, identificaciones, despedidas, errores léxicos, y palabras con carga emocional positiva
o negativa.
A través de un conjunto de transiciones, el AFD puede aceptar diferentes lexemas, y cada vez
que se procesa un lexema, se registra su frecuencia de aparición.

### Transiciones

Las trancisiones se configuran utilizando el método `agregar_transicion`, donde se especifica
un estado de origen, un lexema y un estado de destino.

### Evaluación de Lexemas

El método `evaluar_lexema` toma un lexema, verifica si existe una transición válida desde el
estado actual (inicialmente, estado_inicial), y actualiza el estado.
Si el lexema lleva a un estado final, se considera aceptado.

### Tokenización

La clase `TokenizadorAFD` utiliza el AFD para tokenizar un texto.
Al recibir un texto, lo divide en lexemas y evalúa cada uno, almacenando el resultado en una
lista. 

La función tokenizador utiliza expresiones regulares para dividir el texto de entrada en
lexemas.
Este proceso es fundamental, ya que asegura que se reconozcan correctamente palabras completas,
ignorando signos de puntuación y espacios.
Una vez tokenizados, cada lexema se evalúa contra el AFD para determinar su categoría.
En caso de que un lexema no sea aceptado, se registra como un error léxico, lo que permite un
análisis adicional sobre los términos que no encajan en las categorías predefinidas.

### Análisis de Sentimiento

Utiliza una tabla de sentimientos que asocia palabras con puntajes emocionales, el programa
calcula un puntaje total que indica si el sentimiento general del texto es positivo, negativo o
neutral.
Esto se logra mediante la iteración a través de los lexemas aceptados y la acumulación de sus
puntajes.

### Salidas

El algoritmo realiza un reporte de la conversación dividido en tres partes:

```txt
├───output
│       afd.json
│       reporte.txt
│       tabla_lexemas.txt
```

1. `reporte.txt`:
   Ofrece un análisis del texto procesado, incluyendo el sentimiento general (positivo,
   negativo o neutral), el puntaje total de las palabras, y listas de palabras positivas y
   negativas, así como resultados de la verificación del protocolo de atención.
2. `tabla_lexemas.txt`:
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

## Diferencias entres AFD y usar hasmap

Por ejemplo la frase: "En qué puedo ayudarle" es facilmente reconocible por el AFD, pero para
la implementacion con hashmap se requeriria ampliar el buffer, esto es facilmente solventable
tambien haciendo que el tamano del buffer varie automaticamente para hacer que el buffer sea
del tamano de la frase mas larga, esto en el proceso de instanciamiento.

```txt
         Frase                   TOKEN
AFD:     En qué puedo ayudarle   TOKEN_SALUDO   

HASH:    en                      TOKEN_DESCONOCIO
         qué                     TOKEN_DESCONOCIO
         puedo                   TOKEN_DESCONOCIO
         ayudarle                TOKEN_SENTIMIENTO
```
