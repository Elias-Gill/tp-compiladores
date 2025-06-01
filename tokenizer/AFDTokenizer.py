import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tokenizer.TablaSentimientos import (TIPO_DESPEDIDA, TIPO_IDENTIFICACION,
                                         TIPO_PROHIBIDA, TIPO_SALUDO,
                                         TIPO_SENTIMIENTO, TablaSentimientos)
from tokenizer.tokens import (TOKEN_AGENTE, TOKEN_CLIENTE,
                              TOKEN_SIGNO_PUNTUACION, Token, asignar_tipo)


class AFDTokenizer:
    def __init__(self, tabla_sentimientos: TablaSentimientos):
        self.tabla = tabla_sentimientos
        self._build_afd_completo()
        self._persistir_afd()

    def _persistir_afd(self):
        """Guarda el AFD en un archivo JSON en la carpeta output"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        afd_file = output_dir / "afd.json"
        with open(afd_file, "w", encoding="utf-8") as f:
            json.dump(self.afd, f, indent=2, ensure_ascii=False)

    def _build_afd_completo(self):
        self.afd = {
            "initial": "start",
            "states": {
                "start": {"transitions": {}, "is_final": False, "token_type": None}
            },
        }

        self._cargar_frases_al_afd(self.tabla.palabras, TIPO_SENTIMIENTO)
        self._cargar_frases_al_afd(self.tabla.saludos, TIPO_SALUDO)
        self._cargar_frases_al_afd(self.tabla.despedidas, TIPO_DESPEDIDA)
        self._cargar_frases_al_afd(self.tabla.identificaciones, TIPO_IDENTIFICACION)
        self._cargar_frases_al_afd(self.tabla.palabras_prohibidas, TIPO_PROHIBIDA)

    def _cargar_frases_al_afd(self, frases_dict: Dict[str, int], tipo: str):
        for frase in frases_dict.keys():
            chars = list(frase.lower())
            current_state = "start"

            for i, char in enumerate(chars):
                next_state = f"{current_state}_{char}_{tipo}"

                is_final = i == len(chars) - 1
                token_type = tipo if is_final else None
                puntuacion = frases_dict[frase] if is_final else 0

                if next_state not in self.afd["states"]:
                    self.afd["states"][next_state] = {
                        "transitions": {},
                        "is_final": is_final,
                        "token_type": token_type,
                        "puntuacion": puntuacion,
                    }

                if char not in self.afd["states"][current_state]["transitions"]:
                    self.afd["states"][current_state]["transitions"][char] = []
                self.afd["states"][current_state]["transitions"][char].append(
                    next_state
                )

                current_state = next_state

    def tokenizar(self, texto: str) -> List[Token]:
        tokens = []
        i = 0
        n = len(texto)

        texto = self._preprocesar_hablantes(texto)

        while i < n:
            if texto[i].isspace():
                i += 1
                continue

            if self._es_signo_puntuacion(texto[i]):
                tokens.append(Token(TOKEN_SIGNO_PUNTUACION, texto[i]))
                i += 1
                continue

            hablante_token = self._procesar_hablante(texto, i)
            if hablante_token:
                tokens.append(hablante_token)
                i += len(hablante_token.valor)
                continue

            token, delta = self._tokenizar_con_afd(texto, i)
            tokens.append(token)
            i += delta

        return tokens

    def _procesar_hablante(self, texto: str, start: int) -> Optional[Token]:
        if texto[start:].lower().startswith("agente:"):
            return Token(TOKEN_AGENTE, "agente:")
        elif texto[start:].lower().startswith("cliente:"):
            return Token(TOKEN_CLIENTE, "cliente:")
        return None

    def _preprocesar_hablantes(self, texto: str) -> str:
        import re

        return re.sub(
            r"\b(agente|cliente):",
            lambda m: f" {m.group(0)} ",
            texto,
            flags=re.IGNORECASE,
        )

    def _es_signo_puntuacion(self, char: str) -> bool:
        return not (char.isalnum() or char.isspace() or char in "'-_áéíóúüñ")

    def _tokenizar_con_afd(self, texto: str, start: int) -> Tuple[Token, int]:
        best_token = None
        best_length = 0
        current_states = [("start", "", 0)]

        i = start
        while i < len(texto) and current_states:
            char = texto[i].lower()
            new_states = []

            for state, acc, total_length in current_states:
                if char in self.afd["states"][state]["transitions"]:
                    for next_state in self.afd["states"][state]["transitions"][char]:
                        new_acc = acc + texto[i]
                        new_length = total_length + 1

                        if self.afd["states"][next_state]["is_final"]:
                            token_type = self.afd["states"][next_state]["token_type"]
                            puntuacion = self.afd["states"][next_state]["puntuacion"]

                            if new_length > best_length:
                                best_token = Token(
                                    asignar_tipo(token_type), new_acc, puntuacion
                                )
                                best_length = new_length

                        new_states.append((next_state, new_acc, new_length))

            current_states = new_states
            i += 1

        if best_token:
            return best_token, best_length

        return self._tokenizar_palabra_simple(texto, start)

    def _tokenizar_palabra_simple(self, texto: str, start: int) -> Tuple[Token, int]:
        i = start
        n = len(texto)

        while i < n and (texto[i].isalnum() or texto[i] in "'-_áéíóúüñ"):
            i += 1

        if i == start:
            return Token("DESCONOCIDO", texto[start]), 1

        palabra = texto[start:i].lower()
        tipo, puntuacion = self.tabla.buscar_palabra(palabra)
        return Token(asignar_tipo(tipo), palabra, puntuacion), i - start
