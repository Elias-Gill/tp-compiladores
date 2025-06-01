"""
Dentro de este archivo se encuentra todo el codigo para realizar los reportes y manejar el cli.
En su mayoria es codigo irrelevante para el objetivo principal, que es el analisis de
sentimiento y especialmente el proceso de tokenizacion.
"""

import sys
from pathlib import Path

from tokenizer.AFDTokenizador import AFDTokenizer
from tokenizer.analisis import ResultadoConversacion, analizar_sentimiento
from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import HashTokenizer

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


def aplicar_color(texto, color, usar_color):
    return f"{color}{texto}{RESET}" if usar_color else texto


def imprimir_tokens(tokens, tabla_sentimientos=None, archivo=None, color=True):
    """Imprime los tokens en formato de tabla con opción de colores.

    Args:
        tokens: Lista de tokens a imprimir
        tabla_sentimientos: Opcional, para mostrar puntuaciones
        archivo: Opcional, archivo de salida (sin colores)
        color: Si es True, usa colores ANSI (solo en consola)
    """
    usar_color = color and archivo is None

    # Anchos de columnas
    max_valor = max(len(token.valor) for token in tokens) if tokens else 10
    max_tipo = max(len(token.type) for token in tokens) if tokens else 10
    max_punt = 7  # "Puntaje"

    # Encabezado
    encabezado = (
        f"{aplicar_color('Valor', BOLD, usar_color):<{max_valor}}  "
        f"{aplicar_color('Tipo', BOLD, usar_color):<{max_tipo}}  "
        f"{aplicar_color('Puntaje', BOLD, usar_color) if tabla_sentimientos else ''}"
    )

    linea_sep = "-" * (
        max_valor + max_tipo + (max_punt if tabla_sentimientos else 0) + 4
    )

    out = archivo.write if archivo else print
    out(encabezado)
    out(linea_sep)

    # Cuerpo
    for token in tokens:
        valor = token.valor
        tipo = token.type
        puntuacion = getattr(token, "puntuacion", "")
        punt_str = f"{puntuacion:>{max_punt}}" if tabla_sentimientos else ""

        if archivo:
            out(f"{valor:<{max_valor}}  {tipo:<{max_tipo}}  {punt_str}")
        else:
            out(
                f"{aplicar_color(valor, MAGENTA, usar_color):<{max_valor}}  "
                f"{aplicar_color(tipo, CYAN, usar_color):<{max_tipo}}  "
                f"{aplicar_color(punt_str, YELLOW, usar_color)}"
            )


def si_no(cond, invertido=False, usar_colores=True):
    if not usar_colores:
        return "Sí" if cond else "No"
    color = GREEN if cond != invertido else RED
    return f"{color}Sí{RESET}" if cond else f"{color}No{RESET}"


def generar_seccion(nombre, datos, usar_colores=True):
    bold = BOLD if usar_colores else ""
    reset = RESET if usar_colores else ""
    header = f"\n{bold + CYAN if usar_colores else ''}=== {nombre.upper()} ==={reset}"
    return "\n".join(
        [
            header,
            f"{bold}Puntaje:{reset} {datos.puntaje_total}",
            f"{bold}Saludo:{reset} {si_no(datos.hay_saludo, usar_colores=usar_colores)}",
            f"{bold}Despedida:{reset} {si_no(datos.hay_despedida, usar_colores=usar_colores)}",
            f"{bold}Identificación:{reset} {si_no(datos.hay_identificacion, usar_colores=usar_colores)}",
            f"{bold}Palabras prohibidas:{reset} {si_no(datos.hay_prohibidas, invertido=True, usar_colores=usar_colores)}",
        ]
    )


def obtener_sentimiento(puntaje, usar_colores=True):
    if usar_colores:
        if puntaje > 0:
            return f"{GREEN}POSITIVO{RESET}"
        elif puntaje < 0:
            return f"{RED}NEGATIVO{RESET}"
        return f"{YELLOW}NEUTRAL{RESET}"
    return "POSITIVO" if puntaje > 0 else "NEGATIVO" if puntaje < 0 else "NEUTRAL"


def imprimir_resultados_analisis(resultado: ResultadoConversacion):
    OUTPUT_PATH.mkdir(exist_ok=True)
    # Archivo sin colores
    with open(OUTPUT_PATH / "reporte.txt", "w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                [
                    "=== RESUMEN GENERAL ===",
                    f"Puntaje total: {resultado.puntaje_total}",
                    f"Sentimiento: {obtener_sentimiento(resultado.puntaje_total, usar_colores=False)}",
                    generar_seccion("Cliente", resultado.cliente, usar_colores=False),
                    generar_seccion("Agente", resultado.agente, usar_colores=False),
                    (
                        "\nNota: Se ignoraron las palabras desconocidas"
                        if resultado.cliente.desconocidas
                        or resultado.agente.desconocidas
                        else ""
                    ),
                ]
            )
        )

    # Consola con colores
    print(f"\n{BOLD}{MAGENTA}=== RESUMEN GENERAL ===")
    print(f"{BOLD}{BLUE}Puntaje total:{RESET} {resultado.puntaje_total}")
    print(
        f"{BOLD}{BLUE}Sentimiento:{RESET} {obtener_sentimiento(resultado.puntaje_total)}"
    )
    print(generar_seccion("Cliente", resultado.cliente))
    print(generar_seccion("Agente", resultado.agente))
    if resultado.cliente.desconocidas or resultado.agente.desconocidas:
        print(f"\n{YELLOW}Nota: Se ignoraron las palabras desconocidas{RESET}")


def procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
    try:
        try:
            texto = Path(archivo_entrada).read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"{RED}✗ Error: {archivo_entrada} no encontrado.{RESET}",
                file=sys.stderr,
            )
            return False
        except PermissionError:
            print(
                f"{RED}✗ Error: Sin permisos para leer {archivo_entrada}.{RESET}",
                file=sys.stderr,
            )
            return False

        print(f"\n{BOLD}{BLUE}Procesando:{RESET} {archivo_entrada}")

        tokens = tokenizador.tokenizar(texto)

        try:
            OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"{RED}✗ Error al crear {OUTPUT_PATH}: {e}{RESET}", file=sys.stderr)
            return False

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

        try:
            resultado = analizar_sentimiento(tokens, tabla_sentimientos)
            imprimir_resultados_analisis(resultado)
        except Exception as e:
            print(
                f"{YELLOW}⚠ Advertencia: Error en análisis de sentimientos: {e}{RESET}",
                file=sys.stderr,
            )
            return True  # éxito parcial

        return True
    except Exception as e:
        print(f"{RED}✗ Error inesperado: {e}{RESET}", file=sys.stderr)
        return False


def modo_interactivo(tabla_sentimientos, tokenizador):
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
    usar_hashmap = "--hashmap" in sys.argv
    if usar_hashmap:
        tokenizador = HashTokenizer(tabla_sentimientos)
        sys.argv.remove("--hashmap")
    else:
        tokenizador = AFDTokenizer(tabla_sentimientos)

    if len(sys.argv) > 1:
        archivo = Path(sys.argv[1])
        if not archivo.exists():
            print(
                f"{RED}✗ Error: El archivo {archivo} no existe.{RESET}", file=sys.stderr
            )
            sys.exit(1)
        sys.exit(0 if procesar_archivo(archivo, tokenizador, tabla_sentimientos) else 1)
    else:
        modo_interactivo(tabla_sentimientos, tokenizador)


if __name__ == "__main__":
    main()
