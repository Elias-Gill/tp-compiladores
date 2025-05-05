import json
import os
import re


# Clase AFD para tokenización
class AFD:
    def __init__(self, estado_inicial, estados_finales):
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales
        self.transiciones = {estado_inicial: {}}
        self.lexema_ids = {}
        self.next_id = 1
        # self.contador_por_token = {estado: 0 for estado in estados_finales.values()}
        self.transiciones_usadas = {}

    def agregar_transicion(self, estado_origen, lexema, estado_destino):
        if estado_origen not in self.transiciones:
            self.transiciones[estado_origen] = {}
        if lexema in self.transiciones[estado_origen]:
            raise Exception("Transicion duplicada")
        self.transiciones[estado_origen][lexema] = estado_destino

        # No incrementar el contador aquí
        if lexema not in self.lexema_ids:
            self.lexema_ids[lexema] = self.next_id
            self.next_id += 1
        return self.lexema_ids[lexema]

    def evaluar_lexema(self, lexema):
        estado_actual = self.estado_inicial
        if lexema in self.transiciones[estado_actual]:
            estado_actual = self.transiciones[estado_actual][lexema]

            # Registrar la transición usada
            # if estado_actual not in self.transiciones_usadas:
            #    self.transiciones_usadas[estado_actual] = []
            # Solo agrega si no está ya en la lista
            # if lexema not in self.transiciones_usadas[estado_actual]:
            #    self.transiciones_usadas[estado_actual].append(lexema)
        else:
            return estado_actual, False

        return estado_actual, True

    def vaciar(self):
        self.transiciones = {self.estado_inicial: {}}
        self.lexema_ids.clear()  # Limpiar los IDs de los lexemas
        self.next_id = 1
        # self.contador_por_token = {estado: 0 for estado in self.estados_finales.values()}
        self.transiciones_usadas.clear()

    def guardar_en_json(self, filename):
        data = {
            "estado_inicial": self.estado_inicial,
            "estados_finales": self.estados_finales,
            "transiciones": {self.estado_inicial: {}},
        }
        for estado, transiciones in self.transiciones_usadas.items():
            for transicion in transiciones:
                data["transiciones"][self.estado_inicial][transicion] = estado

        with open(os.path.join("output", filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def generar_tabla_lexemas(self):
        tabla = []
        for estado, lexemas in self.transiciones_usadas.items():
            for lexema in lexemas:
                patrones = [
                    lexema
                    for lexema in self.transiciones[self.estado_inicial]
                    if self.transiciones[self.estado_inicial][lexema] == estado
                ]
                tabla.append({"Lexema": lexema, "Token": estado, "Patron": patrones})
        return tabla


class TokenizadorAFD:
    def __init__(self):
        self.afd = self.construir_afd()
        self.lista_salida = []
        self.posicion = 0

    def cargar_palabras_y_puntajes(self, archivo):
        palabras_positivas = []
        palabras_negativas = []
        with open(
            os.path.join("tokenizer", "sentiment_symbols", archivo), "r", encoding="utf-8"
        ) as f:
            for linea in f:
                palabra, puntaje = linea.strip().split(",")
                puntaje = int(puntaje)
                if puntaje > 0:
                    palabras_positivas.append(palabra)
                else:
                    palabras_negativas.append(palabra)
            f.close()

        return palabras_positivas, palabras_negativas

    def cargar_palabras(self, archivo):
        lexemas = []
        with open(
            os.path.join("tokenizer", "sentiment_symbols", archivo), "r", encoding="utf-8"
        ) as f:
            for linea in f:
                lexemas.append(linea.strip())  # Agrega cada línea como frase

        return lexemas

    def construir_afd(self):
        estado_inicial = "q0"
        estado_finales = {
            "SALUDO": "q_SALUDO",
            "IDENTIFICACION": "q_IDENTIFICACION",
            "DESPEDIDA": "q_DESPEDIDA",
            "ERROR_LX": "q_ERROR_LX",
            "POSITIVO": "q_POSITIVO",
            "NEGATIVO": "q_NEGATIVO",
            "PALABRA_PROHIBIDA": "q_PALABRA_PROHIBIDA",
        }
        # contador_por_token = {estado: 0 for estado in estado_finales.values()}

        afd = AFD(estado_inicial, estado_finales)

        saludos = self.cargar_palabras("saludos.txt")
        identificaciones = self.cargar_palabras("identificaciones.txt")
        despedidas = self.cargar_palabras("despedidas.txt")
        palabras_prohibidas = self.cargar_palabras("palabras_prohibidas.txt")
        palabras_positivas, palabras_negativas = self.cargar_palabras_y_puntajes(
            "palabras_y_puntajes.txt"
        )

        for saludo in saludos:
            afd.agregar_transicion(estado_inicial, saludo, "q_SALUDO")

        for identificacion in identificaciones:
            afd.agregar_transicion(estado_inicial, identificacion, "q_IDENTIFICACION")

        for despedida in despedidas:
            afd.agregar_transicion(estado_inicial, despedida, "q_DESPEDIDA")

        for palabra_positiva in palabras_positivas:
            afd.agregar_transicion(estado_inicial, palabra_positiva, "q_POSITIVO")

        for palabra_negativa in palabras_negativas:
            afd.agregar_transicion(estado_inicial, palabra_negativa, "q_NEGATIVO")

        for palabra_prohibida in palabras_prohibidas:
            afd.agregar_transicion(
                estado_inicial, palabra_prohibida, "q_PALABRA_PROHIBIDA"
            )

        return afd

    def tokenizador(self, texto):
        lexemas = re.findall(r"\b\w+:|\b\w+", texto.lower())

        for lexema in lexemas:
            estado, es_aceptado = self.afd.evaluar_lexema(lexema)

            if es_aceptado:
                print(f"Lexema aceptado: [{lexema}] se detecto como {estado}")
                self.posicion += 1

                # Guardar la transición usada
                if estado not in self.afd.transiciones_usadas:
                    self.afd.transiciones_usadas[estado] = []
                # Agregar lexema aunque sea repetido
                self.afd.transiciones_usadas[estado].append(lexema)

            else:
                print(f"Lexema no aceptado: [{lexema}]")
                self.agregar_error_lexico(lexema)
                self.posicion += 1

                # Guardar la transición para lexemas no aceptados como q_ERROR_LX
                error_estado = "q_ERROR_LX"
                if error_estado not in self.afd.transiciones_usadas:
                    self.afd.transiciones_usadas[error_estado] = []
                # Guardar el lexema no aceptado
                self.afd.transiciones_usadas[error_estado].append(lexema)

        # print(self.afd.transiciones_usadas)
        return lexemas

    def agregar_error_lexico(self, error_lx):
        self.afd.agregar_transicion("q0", error_lx, "q_ERROR_LX")
