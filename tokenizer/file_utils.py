import os

from tokenizer.sentimientos import TablaSentimientos


def eliminar_archivo(nombre_archivo):
    try:
        os.remove(os.path.join("output", nombre_archivo))
    except FileNotFoundError:
        pass
    except Exception as e:
        pass


def cargar_palabras_y_puntajes(archivo):
    tabla_sentimientos = TablaSentimientos()
    with open(
        os.path.join("tokenizer", "sentiment_symbols", archivo), "r", encoding="utf-8"
    ) as f:
        for linea in f:
            palabra, puntaje = linea.strip().split(",")
            tabla_sentimientos.agregar_palabra(palabra, int(puntaje))
        f.close()
    return tabla_sentimientos


def agregar_palabra_sentimiento(tabla_sentimientos, afd):
    palabra = input("Ingrese la nueva palabra: ").strip()
    puntaje = int(input("Ingrese el puntaje de la palabra (positivo o negativo): "))
    eliminar_archivo("tabla_lexemas.txt")
    eliminar_archivo("afd.json")

    # Agregar a la tabla de sentimientos
    tabla_sentimientos.agregar_palabra(palabra, puntaje)

    # Agregar al AFD
    afd.agregar_transicion(
        afd.estado_inicial, palabra, f"q_{puntaje > 0 and 'POSITIVO' or 'NEGATIVO'}"
    )

    # Guardar en el archivo para persistencia
    with open(
        os.path.join("tokenizer", "sentiment_symbols", "palabras_y_puntajes.txt"),
        "a",
        encoding="utf-8",
    ) as f:
        f.write(f"{palabra},{puntaje}\n")

    print(f"Palabra '{palabra}' con puntaje {puntaje} añadida con éxito.")


def eliminar_palabra_sentimiento(tabla_sentimientos):
    palabra = input("Ingrese la palabra a eliminar: ").strip()
    tabla_sentimientos.eliminar_palabra(palabra)
    eliminar_archivo("tabla_lexemas.txt")
    eliminar_archivo("afd.json")

    # Leer el archivo y eliminar la palabra
    with open(
        os.path.join("tokenizer", "sentiment_symbols", "palabras_y_puntajes.txt"),
        "r",
        encoding="utf-8",
    ) as f:
        lineas = f.readlines()

    with open(
        os.path.join("tokenizer", "sentiment_symbols", "palabras_y_puntajes.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        for linea in lineas:
            if not linea.startswith(f"{palabra},"):
                f.write(linea)

    print(f"Palabra '{palabra}' eliminada con éxito.")
