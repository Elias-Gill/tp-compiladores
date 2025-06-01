from dataclasses import dataclass, field
from typing import List

from tokenizer.TablaSentimientos import TablaSentimientos
from tokenizer.tokens import (TOKEN_DESCONOCIDO, TOKEN_DESPEDIDA,
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
    """Muestra un menú ordenado para manejar una palabra desconocida."""

    print(f"\nPalabra desconocida: '{valor}'")

    while True:
        print("Opciones:")
        print("  [a] Agregar palabra manualmente")
        print("  [c] Corregir usando una sugerencia")
        print("  [i] Ignorar palabra")
        opcion = input("Seleccione una opción: ").strip().lower()

        if opcion == "a":
            try:
                puntaje = int(input(f"Ingrese puntaje para '{valor}': "))
                tabla_sentimientos.agregar_palabra(valor, puntaje)
                print(f"✓ Palabra '{valor}' agregada con puntaje {puntaje}")
                return puntaje
            except ValueError:
                print("✗ Entrada inválida. Ingrese un número entero.")

        elif opcion == "c":
            sugerencias = tabla_sentimientos.sugerir_similares(valor)
            if not sugerencias:
                print("✗ No se encontraron sugerencias.")
                continue

            print("\nSugerencias:")
            for i, s in enumerate(sugerencias, 1):
                puntaje = tabla_sentimientos.buscar_palabra(s)[1]
                print(f"  {i}. {s} (puntaje: {puntaje})")

            seleccion = input("Seleccione el número de la sugerencia: ").strip()
            if seleccion.isdigit():
                idx = int(seleccion) - 1
                if 0 <= idx < len(sugerencias):
                    corregida = sugerencias[idx]
                    _, puntaje = tabla_sentimientos.buscar_palabra(corregida)
                    print(f"✓ Usando '{corregida}' con puntaje {puntaje}")
                    return puntaje
                else:
                    print("✗ Número fuera de rango.")
            else:
                print("✗ Entrada inválida.")

        elif opcion == "i":
            print("✓ Palabra ignorada.")
            return 0

        else:
            print("✗ Opción no válida.")


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
