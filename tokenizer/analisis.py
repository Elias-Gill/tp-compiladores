from dataclasses import dataclass
from typing import List

from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import (TOKEN_DESCONOCIDO, TOKEN_DESPEDIDA,
                                   TOKEN_IDENTIFICACION, TOKEN_PROHIBIDA,
                                   TOKEN_SALUDO, Token)


@dataclass
class ResultadoSentimiento:
    puntaje_total: int
    hay_saludo: bool
    hay_despedida: bool
    hay_identificacion: bool
    hay_prohibidas: bool
    desconocidas: List[str]


def manejar_palabra_desconocida(
    valor: str, tabla_sentimientos: TablaSentimientos
) -> int:
    """Maneja palabras desconocidas mostrando sugerencias y opciones al usuario."""
    print(f"\nPalabra desconocida: '{valor}'")
    sugerencias = tabla_sentimientos.sugerir_similares(valor)

    if sugerencias:
        print("Sugerencias de palabras similares:")
        for i, sugerencia in enumerate(sugerencias, 1):
            print(f"{i}. {sugerencia}")

    opciones = "\nOpciones:\n  [a] Agregar al diccionario\n"
    if sugerencias:
        opciones += "  [c] Corregir usando sugerencia\n"
    opciones += "  [i] Ignorar"

    while True:
        opcion = (
            input(f"{opciones}\n¿Qué desea hacer con esta palabra? ").strip().lower()
        )

        if opcion == "a":
            while True:
                try:
                    puntaje = int(input(f"Ingrese un puntaje para '{valor}': "))
                    tabla_sentimientos.agregar_palabra(valor, puntaje)
                    return puntaje
                except ValueError:
                    print("Entrada inválida. Ingrese un número entero.")

        elif opcion == "c" and sugerencias:
            while True:
                seleccion = input("Seleccione el número de la sugerencia: ").strip()
                if seleccion.isdigit() and 0 <= (indice := int(seleccion) - 1) < len(
                    sugerencias
                ):
                    palabra_corregida = sugerencias[indice]
                    _, puntaje = tabla_sentimientos.buscar_palabra(palabra_corregida)
                    print(
                        f"✓ Corregido como '{palabra_corregida}' con puntaje {puntaje}"
                    )
                    return puntaje
                print(
                    "Número fuera de rango."
                    if seleccion.isdigit()
                    else "Entrada inválida."
                )

        elif opcion == "i":
            return 0
        print(
            "Opción no válida. Intente de nuevo."
            if opcion not in ["a", "c", "i"]
            else ""
        )


def analizar_sentimiento(
    tokens: List[Token], tabla_sentimientos: TablaSentimientos
) -> ResultadoSentimiento:
    """Analiza los tokens y calcula el sentimiento general."""
    resultado = ResultadoSentimiento(
        puntaje_total=0,
        hay_saludo=False,
        hay_despedida=False,
        hay_identificacion=False,
        hay_prohibidas=False,
        desconocidas=[],
    )

    # Primera pasada: recolectar palabras desconocidas y procesar las conocidas
    palabras_desconocidas = []

    for token in tokens:
        resultado.puntaje_total += token.puntuacion

        if token.type == TOKEN_PROHIBIDA:
            resultado.hay_prohibidas = True
        elif token.type == TOKEN_SALUDO:
            resultado.hay_saludo = True
        elif token.type == TOKEN_DESPEDIDA:
            resultado.hay_despedida = True
        elif token.type == TOKEN_IDENTIFICACION:
            resultado.hay_identificacion = True
        elif token.type == TOKEN_DESCONOCIDO:
            palabras_desconocidas.append(token.valor)

    # Segunda pasada: manejar palabras desconocidas si el usuario quiere corregirlas
    if palabras_desconocidas:
        print("\nPalabras desconocidas encontradas:")
        for i, palabra in enumerate(palabras_desconocidas, 1):
            print(f"{i}. {palabra}")

        opcion = input("\n¿Desea corregir estas palabras? (s/n): ").strip().lower()

        if opcion == "s":
            for palabra in palabras_desconocidas:
                if puntaje := manejar_palabra_desconocida(palabra, tabla_sentimientos):
                    resultado.puntaje_total += puntaje
                else:
                    resultado.desconocidas.append(palabra)
        else:
            resultado.desconocidas.extend(palabras_desconocidas)

    return resultado
