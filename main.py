import sys
from pathlib import Path

from tokenizer.analisis import ResultadoSentimiento, analizar_sentimiento
from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import Tokenizador


def imprimir_tokens(tokens, tabla_sentimientos=None, archivo=None):
    for token in tokens:
        tipo = token.type
        valor = token.valor

        if tipo == "PALABRA" and tabla_sentimientos:
            puntaje = tabla_sentimientos.obtener_puntaje(valor)
            linea = f"{valor} (PALABRA: {puntaje})"
        else:
            linea = f"{valor} ({tipo})"

        if archivo:
            archivo.write(linea + "\n")
        else:
            puntuacion = getattr(token, "puntuacion", None)
            extra = f" {puntuacion}" if puntuacion is not None else ""
            print(f"- {valor} ({tipo}){extra}")


def imprimir_resultados_analisis(resultado: ResultadoSentimiento):
    print("\n--- Resultados del Análisis de Sentimiento ---")
    print(f"Puntaje total: {resultado.puntaje_total}")
    print(f"¿Hay saludo? {'Sí' if resultado.hay_saludo else 'No'}")
    print(f"¿Hay despedida? {'Sí' if resultado.hay_despedida else 'No'}")
    print(f"¿Hay identificación? {'Sí' if resultado.hay_identificacion else 'No'}")
    print(
        f"¿Se usaron palabras prohibidas? {'Sí' if resultado.hay_prohibidas else 'No'}"
    )


def procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
    """Procesa un archivo con el tokenizador y realiza análisis de sentimiento"""
    try:
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            texto = f.read()

        print(f"\nProcesando archivo: {archivo_entrada.name}")
        tokens = tokenizador.tokenizar(texto)

        archivo_salida = archivo_entrada.parent / f"{archivo_entrada.stem}_tokens.txt"
        with open(archivo_salida, "w", encoding="utf-8") as f:
            imprimir_tokens(tokens, tabla_sentimientos, archivo=f)

        print(f"✓ Tokenización completada. Resultados en: {archivo_salida}")

        resultado = analizar_sentimiento(tokens, tabla_sentimientos)
        imprimir_resultados_analisis(resultado)
        return True

    except FileNotFoundError:
        print(f"✗ Error: Archivo {archivo_entrada} no encontrado.")
        return False
    except Exception as e:
        print(f"✗ Error inesperado al procesar archivo: {e}")
        return False


def modo_interactivo(tabla_sentimientos, tokenizador):
    """Modo interactivo para tokenizar texto ingresado por el usuario"""
    print("\n--- Modo Interactivo ---")
    print("Ingrese el texto a tokenizar (escriba 'salir' para terminar):")

    while True:
        texto = input("\nTexto: ").strip()

        if texto.lower() == "salir":
            break
        if not texto:
            continue

        tokens = tokenizador.tokenizar(texto)
        print("\nResultados de tokenización:")
        imprimir_tokens(tokens)

        resultado = analizar_sentimiento(tokens, tabla_sentimientos)
        imprimir_resultados_analisis(resultado)


def main():
    tabla_sentimientos = TablaSentimientos()
    tokenizador = Tokenizador(tabla_sentimientos)

    if len(sys.argv) > 1:
        archivo_entrada = Path(sys.argv[1])
        if not archivo_entrada.exists():
            print(f"✗ Error: El archivo {archivo_entrada} no existe.", file=sys.stderr)
            sys.exit(1)

        if not procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
            sys.exit(1)
    else:
        modo_interactivo(tabla_sentimientos, tokenizador)


if __name__ == "__main__":
    main()
