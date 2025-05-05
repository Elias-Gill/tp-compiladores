import os
from tokenizer.afd import TokenizadorAFD
from tokenizer.file_utils import agregar_palabra_sentimiento, eliminar_archivo, cargar_palabras_y_puntajes, eliminar_palabra_sentimiento
from tokenizer.menu import mostrar_menu
from tokenizer.analisis import analizar_sentimiento, verificar_protocolo

def reporte(tokenizador, tabla_sentimientos):
    tokenizador.afd.vaciar() 
    tokenizador = TokenizadorAFD()
    tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")
    eliminar_archivo("tabla_lexemas.txt")
    eliminar_archivo("afd.json")
    eliminar_archivo("reporte.txt")
    nombre = input("Ingresa el nombre del archivo de entrada (con extensión .txt): ")
    archivo = f"test/{nombre}"

    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as archivo_texto:
            texto = archivo_texto.read().replace('\n', ' ')

            # Tokenizar el texto
            lexemas = tokenizador.tokenizador(texto)
            # Generar la tabla de lexemas
            tabla_lexemas = tokenizador.afd.generar_tabla_lexemas()
            # Guardar la tabla en un archivo de texto
            with open(os.path.join("output","tabla_lexemas.txt"), "w", encoding="utf-8") as archivo_salida:
                archivo_salida.write(f"{'Lexema':<20} {'Token':<15} {'Patron'}\n")
                archivo_salida.write("=" * 50 + "\n")
                for entrada in tabla_lexemas:
                    archivo_salida.write(f"{entrada['Lexema']:<20} {entrada['Token']:<15} {entrada['Patron']}\n")

            print("-"*64)
            # Análisis de Sentimiento
            resultado_sentimiento = analizar_sentimiento(lexemas, tabla_sentimientos, tokenizador)
            print("Detección de sentimientos: ")
            print(f"Sentimiento general: {resultado_sentimiento['sentimiento']}")
            print(f"Puntaje total: {resultado_sentimiento['puntaje_total']}")
            print(f"Palabras positivas: {resultado_sentimiento['palabras_positivas']}")
            print(f"Palabras negativas: {resultado_sentimiento['palabras_negativas']}")

            # Verificación del Protocolo
            resultado_protocolo = verificar_protocolo(lexemas,tokenizador)
            print(f"Verificación del protocolo de Atención (Agente): ")
            print(f" - Saludo: {'OK' if resultado_protocolo['saludo'] else 'No detectado'}")
            print(f" - Identificación: {'OK' if resultado_protocolo['identificacion'] else 'No detectado'}")
            print(f" - Despedida: {'OK' if resultado_protocolo['despedida'] else 'No detectado'}")
            print(f" - Palabras rudas: {'Detectadas' if resultado_protocolo['palabras_prohibidas'] else 'Ninguna detectada'}")
            print("-"*64)

            # Guardar resultados en archivo de texto
            output_filename = "reporte.txt"
            with open(os.path.join("output",output_filename), "w", encoding="utf-8") as archivo_salida:
                archivo_salida.write(f"Sentimiento general: {resultado_sentimiento['sentimiento']}\n")
                archivo_salida.write(f"Puntaje total: {resultado_sentimiento['puntaje_total']}\n")
                archivo_salida.write(f"Palabras positivas: {resultado_sentimiento['palabras_positivas']}\n")
                archivo_salida.write(f"Palabras negativas: {resultado_sentimiento['palabras_negativas']}\n")
                archivo_salida.write(f"Verificación del protocolo de Atención (Agente):\n")
                archivo_salida.write(f" - Saludo: {'OK' if resultado_protocolo['saludo'] else 'No detectado'}\n")
                archivo_salida.write(f" - Identificación: {'OK' if resultado_protocolo['identificacion'] else 'No detectado'}\n")
                archivo_salida.write(f" - Despedida: {'OK' if resultado_protocolo['despedida'] else 'No detectado'}\n")
                archivo_salida.write(f" - Palabras rudas: {'Detectadas' if resultado_protocolo['palabras_prohibidas'] else 'Ninguna detectada'}\n")

            print(f"[*] Archivo de salida guardado en: {output_filename}")

            # Guardar el AFD en un archivo JSON solo con transiciones usadas
            afd_json = "afd.json"
            tokenizador.afd.guardar_en_json(afd_json)
            print(f"[*] AFD guardado en: {afd_json}")
            print("[*] Tabla de lexemas guardada en: tabla_lexemas.txt")
    else:
        print(f"El archivo {archivo} no existe.")


def main():
    tokenizador = TokenizadorAFD()
    tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

    while True:
        opcion = mostrar_menu()

        if opcion == '1':
            reporte(tokenizador, tabla_sentimientos)

        elif opcion == '2':
            tokenizador.afd.vaciar() 
            agregar_palabra_sentimiento(tabla_sentimientos, tokenizador.afd)
            tokenizador = TokenizadorAFD()
            tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

        elif opcion == '3':
            tokenizador.afd.vaciar() 
            eliminar_palabra_sentimiento(tabla_sentimientos)
            tokenizador = TokenizadorAFD()
            tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

        elif opcion == '4':
            print("Saliendo del programa.")
            break

        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
