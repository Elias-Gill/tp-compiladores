from dataclasses import dataclass
from typing import List

from tokenizer.sentimientos import (TIPO_DESCONOCIDO, TIPO_DESPEDIDA,
                                    TIPO_IDENTIFICACION, TIPO_PROHIBIDA,
                                    TIPO_SALUDO, TablaSentimientos)
from tokenizer.tokenizador import Token


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
    print(f"\nPalabra desconocida: '{valor}'")
    sugerencias = tabla_sentimientos.sugerir_similares(valor)

    if sugerencias:
        print("Sugerencias de palabras similares:")
        for i, sugerencia in enumerate(sugerencias, 1):
            print(f"{i}. {sugerencia}")
    else:
        print("No se encontraron sugerencias.")

    while True:
        print("\nOpciones:")
        print("  [a] Agregar al diccionario")
        if sugerencias:
            print("  [c] Corregir usando sugerencia")
        print("  [i] Ignorar")
        opcion = input("¿Qué desea hacer con esta palabra? ").strip().lower()

        if opcion == "a":
            while True:
                try:
                    puntaje = int(input(f"Ingrese un puntaje para '{valor}': "))
                    break
                except ValueError:
                    print("Entrada inválida. Ingrese un número entero.")
            tabla_sentimientos.agregar_palabra(valor, puntaje)
            return puntaje

        elif opcion == "c" and sugerencias:
            while True:
                seleccion = input("Seleccione el número de la sugerencia: ").strip()
                if seleccion.isdigit():
                    indice = int(seleccion) - 1
                    if 0 <= indice < len(sugerencias):
                        palabra_corregida = sugerencias[indice]
                        _, puntaje = tabla_sentimientos.buscar_palabra(
                            palabra_corregida
                        )
                        print(
                            f"✓ Corregido como '{palabra_corregida}' con puntaje {puntaje}"
                        )
                        return puntaje
                    else:
                        print("Número fuera de rango.")
                else:
                    print("Entrada inválida.")

        elif opcion == "i":
            return 0
        else:
            print("Opción no válida. Intente de nuevo.")


def analizar_sentimiento(
    tokens: List[Token], tabla_sentimientos: TablaSentimientos
) -> ResultadoSentimiento:
    puntaje_total = 0
    hay_saludo = False
    hay_despedida = False
    hay_identificacion = False
    hay_prohibidas = False
    desconocidas = []

    for token in tokens:
        tipo = token.type
        valor = token.valor
        puntuacion = token.puntuacion

        puntaje_total += puntuacion

        if tipo == TIPO_PROHIBIDA:
            hay_prohibidas = True
        elif tipo == TIPO_SALUDO:
            hay_saludo = True
        elif tipo == TIPO_DESPEDIDA:
            hay_despedida = True
        elif tipo == TIPO_IDENTIFICACION:
            hay_identificacion = True
        elif tipo == TIPO_DESCONOCIDO:
            puntaje_opcional = manejar_palabra_desconocida(valor, tabla_sentimientos)
            if puntaje_opcional is not None:
                puntaje_total += puntaje_opcional
            else:
                desconocidas.append(valor)

    return ResultadoSentimiento(
        puntaje_total=puntaje_total,
        hay_saludo=hay_saludo,
        hay_despedida=hay_despedida,
        hay_identificacion=hay_identificacion,
        hay_prohibidas=hay_prohibidas,
        desconocidas=desconocidas,
    )
