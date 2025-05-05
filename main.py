import os
import whisper

from tokenizer.afd import TokenizadorAFD
from tokenizer.analisis import analizar_sentimiento, verificar_protocolo
from tokenizer.file_utils import (
    agregar_palabra_sentimiento,
    cargar_palabras_y_puntajes,
    eliminar_archivo,
    eliminar_palabra_sentimiento,
)


def mostrar_menu():
    print()
    print("-------------------------------------------------------")
    print("                   --- Menú ---                        ")
    print("-------------------------------------------------------")
    print("  1. Analizar texto                                    ")
    print("  2. Añadir nueva palabra a la tabla de sentimientos   ")
    print("  3. Eliminar palabra de la tabla de sentimientos      ")
    print("  4. Convertir audio                                   ")
    print("  5. Salir                                             ")
    print("-------------------------------------------------------")
    seleccion = input("Seleccione una opción: ")
    print()

    return seleccion


def reporte(tokenizador, tabla_sentimientos):
    tokenizador.afd.vaciar()
    tokenizador = TokenizadorAFD()

    tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

    # Preparar los archivos de output
    eliminar_archivo("tabla_lexemas.txt")
    eliminar_archivo("afd.json")
    eliminar_archivo("reporte.txt")

    archivo = input("Ingresa la direccion del archivo de entrada: ")

    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as archivo_texto:
            texto = archivo_texto.read().replace("\n", " ")

            # Tokenizar el texto y generar la tabla de lexemas
            lexemas = tokenizador.tokenizador(texto)
            tabla_lexemas = tokenizador.afd.generar_tabla_lexemas()

            # Guardar la tabla de lexemas
            with open(
                os.path.join("output", "tabla_lexemas.txt"), "w", encoding="utf-8"
            ) as archivo_salida:
                archivo_salida.write(f"{'Lexema':<20} {'Token':<15} {'Patron'}\n")
                archivo_salida.write("=" * 50 + "\n")
                for entrada in tabla_lexemas:
                    archivo_salida.write(
                        f"{entrada['Lexema']:<20} {entrada['Token']:<15} {entrada['Patron']}\n"
                    )

            print("-" * 64)
            # Análisis de Sentimiento
            resultado_sentimiento = analizar_sentimiento(
                lexemas, tabla_sentimientos, tokenizador
            )
            print("Detección de sentimientos: ")
            print(f"Sentimiento general: {resultado_sentimiento['sentimiento']}")
            print(f"Puntaje total: {resultado_sentimiento['puntaje_total']}")
            print(f"Palabras positivas: {resultado_sentimiento['palabras_positivas']}")
            print(f"Palabras negativas: {resultado_sentimiento['palabras_negativas']}")

            # Verificación del Protocolo
            resultado_protocolo = verificar_protocolo(lexemas, tokenizador)
            print(f"Verificación del protocolo de Atención (Agente): ")
            print(
                f" - Saludo: {'OK' if resultado_protocolo['saludo'] else 'No detectado'}"
            )
            print(
                f" - Identificación: {'OK' if resultado_protocolo['identificacion'] else 'No detectado'}"
            )
            print(
                f" - Despedida: {'OK' if resultado_protocolo['despedida'] else 'No detectado'}"
            )
            print(
                f" - Palabras rudas: {'Detectadas' if resultado_protocolo['palabras_prohibidas'] else 'Ninguna detectada'}"
            )
            print("-" * 64)

            # Guardar resultados en archivo de texto
            output_filename = "reporte.txt"
            with open(
                os.path.join("output", output_filename), "w", encoding="utf-8"
            ) as archivo_salida:
                archivo_salida.write(
                    f"Sentimiento general: {resultado_sentimiento['sentimiento']}\n"
                )
                archivo_salida.write(
                    f"Puntaje total: {resultado_sentimiento['puntaje_total']}\n"
                )
                archivo_salida.write(
                    f"Palabras positivas: {resultado_sentimiento['palabras_positivas']}\n"
                )
                archivo_salida.write(
                    f"Palabras negativas: {resultado_sentimiento['palabras_negativas']}\n"
                )
                archivo_salida.write(
                    f"Verificación del protocolo de Atención (Agente):\n"
                )
                archivo_salida.write(
                    f" - Saludo: {'OK' if resultado_protocolo['saludo'] else 'No detectado'}\n"
                )
                archivo_salida.write(
                    f" - Identificación: {'OK' if resultado_protocolo['identificacion'] else 'No detectado'}\n"
                )
                archivo_salida.write(
                    f" - Despedida: {'OK' if resultado_protocolo['despedida'] else 'No detectado'}\n"
                )
                archivo_salida.write(
                    f" - Palabras rudas: {'Detectadas' if resultado_protocolo['palabras_prohibidas'] else 'Ninguna detectada'}\n"
                )

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

        if opcion == "1":
            reporte(tokenizador, tabla_sentimientos)

        elif opcion == "2":
            tokenizador.afd.vaciar()
            agregar_palabra_sentimiento(tabla_sentimientos, tokenizador.afd)
            tokenizador = TokenizadorAFD()
            tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

        elif opcion == "3":
            tokenizador.afd.vaciar()
            eliminar_palabra_sentimiento(tabla_sentimientos)
            tokenizador = TokenizadorAFD()
            tabla_sentimientos = cargar_palabras_y_puntajes("palabras_y_puntajes.txt")

        elif opcion == "4":
            model = whisper.load_model("medium")
            f = input("Ingrese la direccion del archivo a convertir: ")
            resultado = model.transcribe(f)
            print(resultado["text"])

        elif opcion == "5":
            print("Saliendo del programa.")
            break

        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
