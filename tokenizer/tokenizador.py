import re

from tokenizer.sentimientos import TIPO_DESCONOCIDO, TablaSentimientos


class Token:
    def __init__(self, type: str, valor: str, puntuacion: int = 0):
        self.type = type
        self.valor = valor
        self.puntuacion = puntuacion

    def __repr__(self):
        return f"Token(type='{self.type}', valor='{self.valor}', puntuacion={self.puntuacion})"


class Tokenizador:
    def __init__(self, tabla_sentimientos: TablaSentimientos):
        self.tabla = tabla_sentimientos

    def tokenizar(self, texto: str) -> list[Token]:
        tokens = []
        palabras = re.findall(r"\w+|[^\w\s]", texto.lower(), re.UNICODE)
        i = 0

        while i < len(palabras):
            token = None

            # Intentar con 3 palabras
            if i + 2 < len(palabras):
                frase3 = f"{palabras[i]} {palabras[i+1]} {palabras[i+2]}"
                tipo, puntuacion = self.tabla.buscar_palabra(frase3)
                if tipo != TIPO_DESCONOCIDO:
                    token = Token(tipo, frase3, puntuacion)
                    i += 3

            # Intentar con 2 palabras
            if token is None and i + 1 < len(palabras):
                frase2 = f"{palabras[i]} {palabras[i+1]}"
                tipo, puntuacion = self.tabla.buscar_palabra(frase2)
                if tipo != TIPO_DESCONOCIDO:
                    token = Token(tipo, frase2, puntuacion)
                    i += 2

            # Intentar con 1 palabra
            if token is None:
                palabra = palabras[i]
                if re.match(r"\W", palabra):  # signo de puntuación
                    token = Token("SIGNO_PUNTUACION", palabra)
                else:
                    tipo, puntuacion = self.tabla.buscar_palabra(palabra)
                    token = Token(tipo, palabra, puntuacion)
                i += 1

            tokens.append(token)

        return tokens
