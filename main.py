#!/usr/bin/env python3
import sys
from pathlib import Path
from tokenizer.sentimientos import TablaSentimientos
from tokenizer.tokenizador import Tokenizador
from tokenizer.analisis import analizar_sentimiento  # Asegúrate de importar esta función

def procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
    """Procesa un archivo completo con el tokenizador y realiza análisis de sentimiento"""
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            texto = f.read()
        
        print(f"\nProcesando archivo: {archivo_entrada.name}")
        tokens = tokenizador.tokenizar(texto)
        
        # Generar archivo de salida
        archivo_salida = archivo_entrada.parent / f"{archivo_entrada.stem}_tokens.txt"
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for token in tokens:
                tipo = token.type
                valor = token.valor
                
                if tipo == "PALABRA":
                    puntaje = tabla_sentimientos.obtener_puntaje(valor)
                    f.write(f"{valor} (PALABRA: {puntaje})\n")
                else:
                    f.write(f"{valor} ({tipo})\n")
        
        print(f"✓ Tokenización completada. Resultados en: {archivo_salida}")
        
        # Análisis de sentimiento
        resultado = analizar_sentimiento(tokens, tabla_sentimientos)
        
        # Imprimir resultados del análisis de sentimiento
        print("\n--- Resultados del Análisis de Sentimiento ---")
        print(f"Puntaje total: {resultado['puntaje_total']}")
        print(f"¿Hay saludo? {'Sí' if resultado['hay_saludo'] else 'No'}")
        print(f"¿Hay despedida? {'Sí' if resultado['hay_despedida'] else 'No'}")
        print(f"¿Hay identificación? {'Sí' if resultado['hay_identificacion'] else 'No'}")
        print(f"¿Se usaron palabras prohibidas? {'Sí' if resultado['hay_prohibidas'] else 'No'}")
        
        if resultado["desconocidas"]:
            print("\nPalabras desconocidas encontradas:")
            for palabra in resultado["desconocidas"]:
                print(f"- {palabra}")
            
            print("\nSugerencias de palabras similares:")
            # TODO: probar
            # for palabra, sugeridas in resultado["sugerencias"].items():
            #     print(f"  {palabra} -> {', '.join(sugeridas)}")
        
        return True
    
    except FileNotFoundError:
        print(f"✗ Error: Archivo {archivo_entrada} no encontrado.")
        return False
    except Exception as e:
        print(f"✗ Error inesperado al procesar archivo: {e}")
        return False

def modo_interactivo(tabla_sentimientos, tokenizador):
    """Modo interactivo para tokenizar texto ingresado por el usuario y realizar análisis de sentimiento"""
    print("\n--- Modo Interactivo ---")
    print("Ingrese el texto a tokenizar (escriba 'salir' para terminar):")
    
    while True:
        texto = input("\nTexto: ").strip()
        
        if texto.lower() == 'salir':
            break
        
        if not texto:
            continue
        
        tokens = tokenizador.tokenizar(texto)
        
        print("\nResultados de tokenización:")
        for token in tokens:
            tipo = token.type
            valor = token.valor
            puntuacion = token.puntuacion
            
            print(f"- {valor} ({tipo}) {puntuacion}")
        
        # Análisis de sentimiento
        resultado = analizar_sentimiento(tokens, tabla_sentimientos)
        
        # Imprimir resultados del análisis de sentimiento
        print("\n--- Resultados del Análisis de Sentimiento ---")
        print(f"Puntaje total: {resultado['puntaje_total']}")
        print(f"¿Hay saludo? {'Sí' if resultado['hay_saludo'] else 'No'}")
        print(f"¿Hay despedida? {'Sí' if resultado['hay_despedida'] else 'No'}")
        print(f"¿Hay identificación? {'Sí' if resultado['hay_identificacion'] else 'No'}")
        print(f"¿Se usaron palabras prohibidas? {'Sí' if resultado['hay_prohibidas'] else 'No'}")
        
        if resultado["desconocidas"]:
            print("\nPalabras desconocidas encontradas:")
            for palabra in resultado["desconocidas"]:
                print(f"- {palabra}")
            
            # TODO:
            # print("\nSugerencias de palabras similares:")
            # for palabra, sugeridas in resultado["sugerencias"].items():
            #     print(f"  {palabra} -> {', '.join(sugeridas)}")

def main():
    # Inicializar componentes
    tabla_sentimientos = TablaSentimientos()
    tokenizador = Tokenizador(tabla_sentimientos)
    
    # Manejo de argumentos
    if len(sys.argv) > 1:
        # Modo archivo
        archivo_entrada = Path(sys.argv[1])
        if not archivo_entrada.exists():
            print(f"✗ Error: El archivo {archivo_entrada} no existe.", file=sys.stderr)
            sys.exit(1)
            
        if not procesar_archivo(archivo_entrada, tokenizador, tabla_sentimientos):
            sys.exit(1)
    else:
        # Modo interactivo
        modo_interactivo(tabla_sentimientos, tokenizador)


if __name__ == "__main__":
    main()
