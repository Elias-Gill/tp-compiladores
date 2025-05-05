class NodoSentimiento:
    def __init__(self, palabra, puntaje):
        self.palabra = palabra
        self.puntaje = puntaje
        self.siguiente = None

class TablaSentimientos:
    def __init__(self):
        self.cabeza = None

    def agregar_palabra(self, palabra, puntaje):
        nuevo_nodo = NodoSentimiento(palabra, puntaje)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def obtener_puntaje(self, palabra):
        actual = self.cabeza
        while actual:
            if actual.palabra == palabra:
                return actual.puntaje
            actual = actual.siguiente
        return 0  # Retornar 0 si la palabra no se encuentra

    def eliminar_palabra(self, palabra):
        actual = self.cabeza
        anterior = None
        while actual:
            if actual.palabra == palabra:
                if anterior is None:  # Eliminar la cabeza
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                return  # Palabra eliminada
            anterior = actual
            actual = actual.siguiente
        print(f"La palabra '{palabra}' no se encontró en la tabla de sentimientos.")
