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
