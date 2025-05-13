import re

from tokenizer.sentimientos import TIPO_DESCONOCIDO, TablaSentimientos

# Tipos de token
TOKEN_SALUDO = "TOKEN_SALUDO"
TOKEN_DESPEDIDA = "TOKEN_DESPEDIDA"
TOKEN_IDENTIFICACION = "TOKEN_IDENTIFICACION"
TOKEN_PROHIBIDA = "TOKEN_PROHIBIDA"
TOKEN_SENTIMIENTO = "TOKEN_SENTIMIENTO"
TOKEN_DESCONOCIDO = "TOKEN_DESCONOCIDO"
TOKEN_AGENTE = "TOKEN_AGENTE"
TOKEN_CLIENTE = "TOKEN_CLIENTE"
TOKEN_SIGNO_PUNTUACION = "TOKEN_SIGNO_PUNTUACION"


def asignar_tipo(tipo_tabla: str) -> str:
    """Mapea tipos de la tabla a constantes de token."""
    return {
        "saludo": TOKEN_SALUDO,
        "despedida": TOKEN_DESPEDIDA,
        "identificacion": TOKEN_IDENTIFICACION,
        "prohibida": TOKEN_PROHIBIDA,
        "sentimiento": TOKEN_SENTIMIENTO,
    }.get(tipo_tabla, TOKEN_DESCONOCIDO)


class Token:
    __slots__ = ["type", "valor", "puntuacion"]  # Mejor rendimiento

    def __init__(self, type: str, valor: str, puntuacion: int = 0):
        self.type = type
        self.valor = valor
        self.puntuacion = puntuacion

    def __repr__(self):
        return f"Token(type='{self.type}', valor='{self.valor}', puntuacion={self.puntuacion})"


class Tokenizador:
    def __init__(self, tabla_sentimientos: TablaSentimientos):
        self.tabla = tabla_sentimientos
        self._hablante_re = re.compile(r"\b(agente|cliente):", re.IGNORECASE)
        self._palabras_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)

    def tokenizar(self, texto: str) -> list[Token]:
        tokens = []
        texto = self._hablante_re.sub(lambda m: f" {m.group(0)} ", texto)
        palabras = self._palabras_re.findall(texto.lower())
        i = 0

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
