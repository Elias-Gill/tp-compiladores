from tokenizer.sentimientos import (TIPO_DESCONOCIDO, TIPO_DESPEDIDA,
                                    TIPO_IDENTIFICACION, TIPO_PROHIBIDA,
                                    TIPO_SALUDO, TIPO_SENTIMIENTO)
from tokenizer.tokenizador import Token


def analizar_sentimiento(tokens: list[Token], tabla_sentimientos):
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
            desconocidas.append(valor)

    # TODO: hacer algo con palabras desconocidas
    # sugerencias = {}
    # for palabra in desconocidas:
    #     sugerencias[palabra] = tabla_sentimientos.sugerir_similares(palabra)

    return {
        "puntaje_total": puntaje_total,
        "hay_saludo": hay_saludo,
        "hay_despedida": hay_despedida,
        "hay_identificacion": hay_identificacion,
        "hay_prohibidas": hay_prohibidas,
        "desconocidas": desconocidas,
        # "sugerencias": sugerencias,
    }
