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

def imprimir_tokens(tokens, tabla_sentimientos=None, archivo=None):
    """Imprime los tokens con formato colorido usando ANSI"""
    for token in tokens:
        tipo = token.type
        valor = token.valor
        puntuacion = getattr(token, "puntuacion", None)

        if archivo:
            archivo.write(f"{valor} ({tipo})" + (f" {puntuacion}" if puntuacion else "") + "\n")
        else:
            tipo_str = f"{CYAN}{tipo}{RESET}"
            valor_str = f"{MAGENTA}{valor}{RESET}"
            punt_str = f" {YELLOW}{puntuacion}{RESET}" if puntuacion else ""
            print(f"- {valor_str} ({tipo_str}){punt_str}")

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
        ("¿Palabras prohibidas?", si_no(resultado.hay_prohibidas))
    ]
    
    for label, value in items:
        print(f"{BOLD}{BLUE}{label}:{RESET} {value}")

def procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
    """Procesa archivo con manejo de errores"""
    try:
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            texto = f.read()

        print(f"\n{BOLD}{BLUE}Procesando:{RESET} {archivo_entrada.name}")
        tokens = tokenizador.tokenizar(texto)

        archivo_salida = archivo_entrada.parent / f"{archivo_entrada.stem}_tokens.txt"
        with open(archivo_salida, "w", encoding="utf-8") as f:
            imprimir_tokens(tokens, tabla_sentimientos, f)

        print(f"{GREEN}✓ Tokenización completada. Resultados en: {archivo_salida}{RESET}")
        imprimir_resultados_analisis(analizar_sentimiento(tokens, tabla_sentimientos))
        return True

    except FileNotFoundError:
        print(f"{RED}✗ Error: Archivo {archivo_entrada} no encontrado.{RESET}", file=sys.stderr)
        return False
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
            print(f"{RED}✗ Error: El archivo {archivo_entrada} no existe.{RESET}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0 if procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos) else 1)
    else:
        modo_interactivo(tabla_sentimientos, tokenizador)

if __name__ == "__main__":
    main()
