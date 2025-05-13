from dataclasses import dataclass
from typing import Dict, List

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
    sugerencias: Dict[str, List[str]]


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
            desconocidas.append(valor)

    sugerencias = {
        palabra: tabla_sentimientos.sugerir_similares(palabra)
        for palabra in desconocidas
    }

    return ResultadoSentimiento(
        puntaje_total=puntaje_total,
        hay_saludo=hay_saludo,
        hay_despedida=hay_despedida,
        hay_identificacion=hay_identificacion,
        hay_prohibidas=hay_prohibidas,
        desconocidas=desconocidas,
        sugerencias=sugerencias,
    )
