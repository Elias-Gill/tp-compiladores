import sys
from pathlib import Path

from tokenizer.analisis import ResultadoSentimiento, analizar_sentimiento
from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import Tokenizador

# Códigos ANSI para colores
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

OUTPUT_PATH = Path("output")


def imprimir_tokens(tokens, tabla_sentimientos=None, archivo=None, color=True):
    """Imprime los tokens en formato de tabla con opción de colores.

    Args:
        tokens: Lista de tokens a imprimir
        tabla_sentimientos: Opcional, para mostrar puntuaciones
        archivo: Opcional, archivo de salida (sin colores)
        color: Si es True, usa colores ANSI (solo en consola)
    """
    # Configurar formatos según el modo
    if archivo or not color:
        RESET = BOLD = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = ""
    else:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"

    # Determinar el ancho de columnas
    max_valor = max(len(token.valor) for token in tokens) if tokens else 10
    max_tipo = max(len(token.type) for token in tokens) if tokens else 10
    max_punt = 7  # Para "Puntaje"

    # Encabezado de la tabla
    encabezado = (
        f"{BOLD}{'Valor':<{max_valor}}  {'Tipo':<{max_tipo}}  "
        f"{'Puntaje' if tabla_sentimientos else '':<{max_punt}}{RESET}"
    )

    # Imprimir en archivo o consola
    if archivo:
        archivo.write(encabezado + "\n")
        archivo.write("-" * (max_valor + max_tipo + max_punt + 4) + "\n")
    else:
        print(encabezado)
        print("-" * (max_valor + max_tipo + max_punt + 4))

    # Imprimir cada token
    for token in tokens:
        valor = token.valor
        tipo = token.type
        puntuacion = getattr(token, "puntuacion", None)

        # Formatear puntuación si existe tabla de sentimientos
        punt_str = ""
        if tabla_sentimientos and puntuacion is not None:
            punt_str = f"{puntuacion:>{max_punt}}"

        # Construir línea
        linea = (
            f"{MAGENTA}{valor:<{max_valor}}{RESET}  "
            f"{CYAN}{tipo:<{max_tipo}}{RESET}  "
            f"{YELLOW if color else ''}{punt_str}{RESET}"
        ).strip()

        if archivo:
            archivo.write(f"{valor:<{max_valor}}  {tipo:<{max_tipo}}  {punt_str}\n")
        else:
            print(linea)


def imprimir_resultados_analisis(resultado: ResultadoSentimiento):
    """Muestra resultados con colores ANSI"""
    print(f"\n{BOLD}{CYAN}=== Resultados del Análisis de Sentimiento ==={RESET}")

    # Determinar color del sentimiento
    if resultado.puntaje_total > 0:
        sen = f"{GREEN}POSITIVO"
    elif resultado.puntaje_total == 0:
        sen = f"{YELLOW}NEUTRAL"
    else:
        sen = f"{RED}NEGATIVO"

    # Función helper para Sí/No coloreado
    def si_no(cond):
        return f"{GREEN}Sí{RESET}" if cond else f"{RED}No{RESET}"

    # Imprimir resultados
    items = [
        ("Sentimiento final", sen),
        ("Puntaje total", str(resultado.puntaje_total)),
        ("¿Hay saludo?", si_no(resultado.hay_saludo)),
        ("¿Hay despedida?", si_no(resultado.hay_despedida)),
        ("¿Hay identificación?", si_no(resultado.hay_identificacion)),
        ("¿Palabras prohibidas?", si_no(resultado.hay_prohibidas)),
    ]

    for label, value in items:
        print(f"{BOLD}{BLUE}{label}:{RESET} {value}")


def procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
    try:
        # 1. Lectura del archivo de entrada
        try:
            with open(archivo_entrada, "r", encoding="utf-8") as f:
                texto = f.read()
        except FileNotFoundError:
            print(
                f"{RED}✗ Error: Archivo de entrada {archivo_entrada} no encontrado.{RESET}",
                file=sys.stderr,
            )
            return False
        except PermissionError:
            print(
                f"{RED}✗ Error: Sin permisos para leer {archivo_entrada}{RESET}",
                file=sys.stderr,
            )
            return False

        print(f"\n{BOLD}{BLUE}Procesando:{RESET} {archivo_entrada.name}")

        # 2. Tokenización
        tokens = tokenizador.tokenizar(texto)

        # 3. Preparar directorio de salida
        try:
            OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(
                f"{RED}✗ Error al crear directorio de salida {OUTPUT_PATH}: {e}{RESET}",
                file=sys.stderr,
            )
            return False

        # 4. Escritura de resultados
        archivo_salida = OUTPUT_PATH / "tokens.txt"
        try:
            with open(archivo_salida, "w", encoding="utf-8") as f:
                imprimir_tokens(tokens, tabla_sentimientos, f, color=False)
        except OSError as e:
            print(
                f"{RED}✗ Error al escribir {archivo_salida}: {e}{RESET}",
                file=sys.stderr,
            )
            return False

        print(
            f"{GREEN}✓ Tokenización completada. Resultados en: {archivo_salida}{RESET}"
        )

        # 5. Análisis de sentimientos
        try:
            resultado = analizar_sentimiento(tokens, tabla_sentimientos)
            imprimir_resultados_analisis(resultado)
        except Exception as e:
            print(
                f"{YELLOW}⚠ Advertencia: Error en análisis de sentimientos: {e}{RESET}",
                file=sys.stderr,
            )
            # Consideramos esto como éxito parcial
            return True

        return True

    except Exception as e:
        print(f"{RED}✗ Error inesperado: {e}{RESET}", file=sys.stderr)
        return False


def modo_interactivo(tabla_sentimientos, tokenizador):
    """Modo interactivo con colores ANSI"""
    print(f"\n{BOLD}{CYAN}=== Modo Interactivo ==={RESET}")
    print(f"Ingrese texto a analizar (escriba {YELLOW}salir{RESET} para terminar):")

    while True:
        texto = input(f"\n{BOLD}{BLUE}Texto:{RESET} ").strip()
        if texto.lower() == "salir":
            break
        if not texto:
            continue

        tokens = tokenizador.tokenizar(texto)
        print(f"\n{BOLD}{BLUE}Tokens encontrados:{RESET}")
        imprimir_tokens(tokens)
        imprimir_resultados_analisis(analizar_sentimiento(tokens, tabla_sentimientos))


def main():
    tabla_sentimientos = TablaSentimientos()
    tokenizador = Tokenizador(tabla_sentimientos)

    if len(sys.argv) > 1:
        archivo_entrada = Path(sys.argv[1])
        if not archivo_entrada.exists():
            print(
                f"{RED}✗ Error: El archivo {archivo_entrada} no existe.{RESET}",
                file=sys.stderr,
            )
            sys.exit(1)
        sys.exit(
            0
            if procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos)
            else 1
        )
    else:
        modo_interactivo(tabla_sentimientos, tokenizador)


if __name__ == "__main__":
    main()
