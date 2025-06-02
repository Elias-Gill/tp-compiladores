import re

from tokenizer.TablaSentimientos import TIPO_DESCONOCIDO, TablaSentimientos
from tokenizer.tokens import (TOKEN_AGENTE, TOKEN_CLIENTE,
                              TOKEN_SIGNO_PUNTUACION, Token, asignar_tipo)


class HashTokenizer:
    def __init__(self, tabla_sentimientos: TablaSentimientos):
        self.tabla = tabla_sentimientos
        self._hablante_re = re.compile(r"\b(agente|cliente):", re.IGNORECASE)
        self._palabras_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)

    def tokenizar(self, texto: str) -> list[Token]:
        # extraer los hablantes del texto
        texto = self._hablante_re.sub(lambda m: f" {m.group(0)} ", texto)
        palabras = self._palabras_re.findall(texto.lower())
        i = 0

        # tokenizar
        tokens = []
        while i < len(palabras):
            # Manejo de agente/cliente
            if i + 1 < len(palabras) and palabras[i + 1] == ":":
                if palabras[i] == "agente":
                    tokens.append(Token(TOKEN_AGENTE, "agente:"))
                    i += 2
                    continue
                if palabras[i] == "cliente":
                    tokens.append(Token(TOKEN_CLIENTE, "cliente:"))
                    i += 2
                    continue

            # Búsqueda de frases (3, 2, 1 palabras)
            for length in (3, 2, 1):
                if i + length > len(palabras):
                    continue

                frase = " ".join(palabras[i : i + length])
                tipo, puntuacion = self.tabla.buscar_palabra(frase)

                if tipo != TIPO_DESCONOCIDO:
                    tokens.append(Token(asignar_tipo(tipo), frase, puntuacion))
                    i += length
                    break
            else:  # Si no se encontró ninguna frase válida
                palabra = palabras[i]
                if re.match(r"\W", palabra):
                    tokens.append(Token(TOKEN_SIGNO_PUNTUACION, palabra))
                else:
                    tipo, puntuacion = self.tabla.buscar_palabra(palabra)
                    tokens.append(Token(asignar_tipo(tipo), palabra, puntuacion))
                i += 1

        return tokens
