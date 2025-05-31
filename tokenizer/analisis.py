from dataclasses import dataclass, field
from typing import List

from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import (TOKEN_DESCONOCIDO, TOKEN_DESPEDIDA,
                                   TOKEN_IDENTIFICACION, TOKEN_PROHIBIDA,
                                   TOKEN_SALUDO, Token)


@dataclass
class ResultadoParticipante:
    puntaje_total: int = 0
    hay_saludo: bool = False
    hay_despedida: bool = False
    hay_identificacion: bool = False
    hay_prohibidas: bool = False
    desconocidas: List[str] = field(default_factory=list)


@dataclass
class ResultadoConversacion:
    cliente: ResultadoParticipante
    agente: ResultadoParticipante
    puntaje_total: int = 0
    desconocidas_compartidas: List[str] = field(default_factory=list)


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
) -> ResultadoConversacion:
    """Analiza los tokens diferenciando entre cliente y agente."""
    resultado = ResultadoConversacion(
        cliente=ResultadoParticipante(), agente=ResultadoParticipante()
    )
    palabras_desconocidas = []
    hablante_actual = "agente"  # 'cliente' o 'agente'

    # Primera pasada: procesar tokens conocidos
    for token in tokens:
        # Determinar hablante actual
        if token.type == "TOKEN_CLIENTE":
            hablante_actual = "cliente"
            continue
        elif token.type == "TOKEN_AGENTE":
            hablante_actual = "agente"
            continue

        # Si no hay hablante definido, saltar este token
        if not hablante_actual:
            continue

        # Obtener referencia al participante actual
        participante = getattr(resultado, hablante_actual)

        # Procesar token según tipo
        if token.type == TOKEN_PROHIBIDA:
            participante.hay_prohibidas = True
        elif token.type == TOKEN_SALUDO:
            participante.hay_saludo = True
        elif token.type == TOKEN_DESPEDIDA:
            participante.hay_despedida = True
        elif token.type == TOKEN_IDENTIFICACION:
            participante.hay_identificacion = True
        elif token.type == TOKEN_DESCONOCIDO:
            palabras_desconocidas.append((hablante_actual, token.valor))

        # Sumar puntuación siempre
        participante.puntaje_total += token.puntuacion
        resultado.puntaje_total += token.puntuacion

    # Segunda pasada: manejar palabras desconocidas
    if palabras_desconocidas:
        print("\nPalabras desconocidas encontradas:")
        for i, (_, palabra) in enumerate(palabras_desconocidas, 1):
            print(f"{i}. {palabra}")

        opcion = input("\n¿Desea corregir estas palabras? (s/n): ").strip().lower()

        if opcion == "s":
            for hablante, palabra in palabras_desconocidas:
                participante = getattr(resultado, hablante)
                if puntaje := manejar_palabra_desconocida(palabra, tabla_sentimientos):
                    participante.puntaje_total += puntaje
                    resultado.puntaje_total += puntaje
                else:
                    participante.desconocidas.append(palabra)
        else:
            for hablante, palabra in palabras_desconocidas:
                getattr(resultado, hablante).desconocidas.append(palabra)

    return resultado
