from collections import defaultdict

from tokenizer.sentimientos import TablaSentimientos


class AFDTokenizador:
    def __init__(self, tabla_sentimientos: TablaSentimientos):
        self.tabla = tabla_sentimientos
        self.estado_inicial = 0
        self.estado_counter = 1  # Comienza desde 1 porque 0 es el inicial
        self.estados_finales = {}  # {estado: (tipo, valor, *args)}
        self.transiciones = defaultdict(dict)  # {estado: {caracter: nuevo_estado}}
        self.estado_desconocido = -1
        self._construir_afd()

    def _nuevo_estado(self):
        estado = self.estado_counter
        self.estado_counter += 1
        return estado

    def _construir_afd(self):
        for palabra in self.tabla.palabras:
            self._agregar_palabra_afd(palabra, "PALABRA")

        for categoria, frases in [
            ("SALUDO", self.tabla.saludos),
            ("DESPEDIDA", self.tabla.despedidas),
            ("IDENTIFICACION", self.tabla.identificaciones),
        ]:
            for frase in frases:
                self._agregar_frase_afd(frase, categoria)

        for palabra in self.tabla.palabras_prohibidas:
            self._agregar_palabra_afd(palabra, "PROHIBIDA")

    def _agregar_palabra_afd(self, palabra, tipo):
        estado_actual = self.estado_inicial
        for i, char in enumerate(palabra.lower()):
            if char not in self.transiciones[estado_actual]:
                nuevo_estado = self._nuevo_estado()
                self.transiciones[estado_actual][char] = nuevo_estado
                estado_actual = nuevo_estado
            else:
                estado_actual = self.transiciones[estado_actual][char]
        extra = (self.tabla.palabras[palabra],) if tipo == "PALABRA" else ()
        self.estados_finales[estado_actual] = (tipo, palabra, *extra)

    def _agregar_frase_afd(self, frase, tipo):
        estado_actual = self.estado_inicial
        for i, char in enumerate(frase.lower()):
            char_key = " " if char == " " else char
            if char_key not in self.transiciones[estado_actual]:
                nuevo_estado = self._nuevo_estado()
                self.transiciones[estado_actual][char_key] = nuevo_estado
                estado_actual = nuevo_estado
            else:
                estado_actual = self.transiciones[estado_actual][char_key]
        self.estados_finales[estado_actual] = (tipo, frase)

    def tokenizar(self, texto, manejar_desconocidos=None):
        tokens = []
        i = 0
        n = len(texto)
        signos_puntuacion = {
            ",",
            ".",
            ";",
            ":",
            "!",
            "?",
            "¿",
            "¡",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
        }
        espacios = {" ", "\t", "\n", "\r"}

        while i < n:
            estado = self.estado_inicial
            buffer = []
            ultimo_estado_final = None
            buffer_final = []
            pos_final = i

            j = i
            while j < n:
                char = texto[j].lower()
                char_key = " " if char in espacios else char

                if char in signos_puntuacion and not buffer:
                    tokens.append(("SIGNO_PUNTUACION", char))
                    j += 1
                    break

                if char_key in self.transiciones[estado]:
                    estado = self.transiciones[estado][char_key]
                    buffer.append(texto[j])
                    if estado in self.estados_finales:
                        ultimo_estado_final = estado
                        buffer_final = buffer.copy()
                        pos_final = j + 1
                    j += 1
                else:
                    j += 1  # seguimos intentando, no cortamos aún
                    break  # rompe el while, luego se usa lo último válido

            if ultimo_estado_final is not None:
                self._procesar_buffer(
                    tokens, buffer_final, ultimo_estado_final, manejar_desconocidos
                )
                i = pos_final
            else:
                if texto[i] not in espacios:
                    buffer = []
                    while (
                        i < n
                        and texto[i] not in signos_puntuacion
                        and texto[i] not in espacios
                    ):
                        buffer.append(texto[i])
                        i += 1
                    self._procesar_buffer(
                        tokens, buffer, self.estado_desconocido, manejar_desconocidos
                    )
                else:
                    i += 1  # Saltar espacio

        return tokens

    def _procesar_buffer(self, tokens, buffer, estado, manejar_desconocidos=None):
        if not buffer:
            return
        token_texto = "".join(buffer)
        if estado in self.estados_finales:
            tipo, valor, *extra = self.estados_finales[estado]
            if tipo in {"SALUDO", "DESPEDIDA", "IDENTIFICACION"}:
                token_texto = " ".join(token_texto.split())
            tokens.append((tipo, token_texto, *extra))
        else:
            if manejar_desconocidos:
                resultado = manejar_desconocidos(token_texto, self.tabla, self)
                if resultado:
                    accion, datos = resultado
                    if accion == "agregada":
                        tokens.append(("PALABRA", datos["palabra"], datos["puntaje"]))
                    elif accion == "reemplazada":
                        tokens.append(("PALABRA", datos["reemplazo"], datos["puntaje"]))
            else:
                tokens.append(("DESCONOCIDO", token_texto))

    def reset(self):
        self.estado_actual = self.estado_inicial
