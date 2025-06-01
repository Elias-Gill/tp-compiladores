import difflib
from pathlib import Path

TIPO_SENTIMIENTO = "sentimiento"
TIPO_SALUDO = "saludo"
TIPO_DESPEDIDA = "despedida"
TIPO_IDENTIFICACION = "identificacion"
TIPO_PROHIBIDA = "prohibida"
TIPO_DESCONOCIDO = "desconocido"


class TablaSentimientos:
    # Constantes de archivos
    BASE_DIR = Path("tokenizer/sentiment_symbols")
    ARCHIVO_PUNTAJES = BASE_DIR / "palabras_y_puntajes.txt"
    ARCHIVO_SALUDOS = BASE_DIR / "saludos.txt"
    ARCHIVO_DESPEDIDAS = BASE_DIR / "despedidas.txt"
    ARCHIVO_IDENTIFICACIONES = BASE_DIR / "identificaciones.txt"
    ARCHIVO_PROHIBIDAS = BASE_DIR / "palabras_prohibidas.txt"

    def __init__(self):
        # Diccionarios separados
        self.palabras = {}
        self.saludos = {}
        self.despedidas = {}
        self.identificaciones = {}
        self.palabras_prohibidas = {}

        self._cargar_datos()

    def agregar_palabra(self, palabra, puntaje, persistir=True):
        palabra = palabra.lower().strip()
        self.palabras[palabra] = int(puntaje)
        if persistir:
            self._guardar_palabra_en_archivo(palabra, puntaje, self.ARCHIVO_PUNTAJES)

    def eliminar_palabra(self, palabra, persistir=True):
        palabra = palabra.lower().strip()
        if palabra in self.palabras:
            del self.palabras[palabra]
            if persistir:
                self._eliminar_palabra_de_archivo(palabra, self.ARCHIVO_PUNTAJES)
            return True
        return False

    def buscar_palabra(self, palabra):
        palabra = palabra.lower().strip()
        if palabra in self.palabras:
            return (TIPO_SENTIMIENTO, self.palabras[palabra])
        if palabra in self.saludos:
            return (TIPO_SALUDO, self.saludos[palabra])
        if palabra in self.despedidas:
            return (TIPO_DESPEDIDA, self.despedidas[palabra])
        if palabra in self.identificaciones:
            return (TIPO_IDENTIFICACION, self.identificaciones[palabra])
        if palabra in self.palabras_prohibidas:
            return (TIPO_PROHIBIDA, self.palabras_prohibidas[palabra])
        return (TIPO_DESCONOCIDO, 0)

    def _cargar_archivo_comun(self, archivo: Path, destino: dict):
        if not archivo.exists():
            return
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    palabra, valor = linea.split(",", 1)
                    destino[palabra.lower()] = int(valor)
                except ValueError:
                    continue

    def _cargar_datos(self):
        self._cargar_archivo_comun(self.ARCHIVO_PUNTAJES, self.palabras)
        self._cargar_archivo_comun(self.ARCHIVO_SALUDOS, self.saludos)
        self._cargar_archivo_comun(self.ARCHIVO_DESPEDIDAS, self.despedidas)
        self._cargar_archivo_comun(self.ARCHIVO_IDENTIFICACIONES, self.identificaciones)
        self._cargar_archivo_comun(self.ARCHIVO_PROHIBIDAS, self.palabras_prohibidas)

    def _guardar_palabra_en_archivo(self, palabra, valor, archivo):
        try:
            with open(archivo, "a", encoding="utf-8") as f:
                f.write(f"{palabra},{valor}\n")
        except IOError as e:
            print(f"Error al guardar en archivo: {e}")

    def _eliminar_palabra_de_archivo(self, palabra, archivo):
        if not archivo.exists():
            return
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                lineas = [
                    linea
                    for linea in f
                    if not linea.lower().startswith(f"{palabra.lower()},")
                ]
            with open(archivo, "w", encoding="utf-8") as f:
                f.writelines(lineas)
        except IOError as e:
            print(f"Error al modificar archivo: {e}")

    def sugerir_similares(self, palabra: str, max_sugerencias=3):
        palabra = palabra.lower().strip()

        # Palabras conocidas del sistema
        todas = (
            set(self.palabras)
            | set(self.saludos)
            | set(self.despedidas)
            | set(self.identificaciones)
            | set(self.palabras_prohibidas)
        )

        sugerencias = difflib.get_close_matches(
            palabra, todas, n=max_sugerencias, cutoff=0.6
        )
        return sugerencias
