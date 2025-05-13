def manejar_palabra_desconocida(palabra, tabla_sentimientos):
    """
    Muestra un menú interactivo para manejar palabras no encontradas en la tabla de símbolos.

    Args:
        palabra (str): Palabra no reconocida
        tabla_sentimientos (TablaSentimientos): Instancia de la tabla de símbolos
        tokenizador: Instancia del tokenizador para posibles actualizaciones

    Returns:
        tuple: (acción_tomada, datos_relevantes)
               acciones: 'agregada', 'reemplazada', 'ignorada'
    """
    print(f"\nPalabra no reconocida: '{palabra}'")
    print("¿Qué deseas hacer?")
    print("1. Agregar palabra a la tabla de símbolos")
    print("2. Ver sugerencias de palabras similares")
    print("3. Ignorar y continuar")
    print("4. Cancelar procesamiento")

    while True:
        try:
            opcion = int(input("Seleccione una opción (1-4): "))

            if opcion == 1:
                # Opción para agregar nueva palabra
                puntaje = int(
                        input(
                            f"Ingrese puntaje de sentimiento para '{palabra}' (ej. 2 para positivo, -1 para negativo): "
                            )
                        )

                # TODO: Implementar función para agregar palabra a la tabla
                # tabla_sentimientos.agregar_palabra(palabra, puntaje)

                # TODO: Si el tokenizador usa AFD, reconstruirlo
                # if isinstance(tokenizador, AFDTokenizador):
                #     tokenizador.actualizar_afd()

                print(f"Palabra '{palabra}' agregada con puntaje {puntaje}.")
                return ("agregada", {"palabra": palabra, "puntaje": puntaje})

            elif opcion == 2:
                # Opción para mostrar sugerencias
                # TODO: Implementar función de sugerencias (usando distancia de Levenshtein)
                # sugerencias = obtener_sugerencias(palabra, tabla_sentimientos)
                sugerencias = ["bueno", "bien", "bonito"]  # Ejemplo temporal

                if not sugerencias:
                    print("No se encontraron sugerencias adecuadas.")
                    continue

                print("\nSugerencias:")
                for i, sug in enumerate(sugerencias[:3], 1):
                    print(
                            f"{i}. {sug} (Puntaje: {tabla_sentimientos.obtener_puntaje(sug)})"
                            )

                print(f"{len(sugerencias)+1}. Volver al menú anterior")

                seleccion = int(
                        input("Seleccione una opción para reemplazar o volver: ")
                        )

                if seleccion <= len(sugerencias):
                    palabra_seleccionada = sugerencias[seleccion - 1]
                    print(
                            f"Usando palabra '{palabra_seleccionada}' en lugar de '{palabra}'"
                            )
                    return (
                            "reemplazada",
                            {
                                "original": palabra,
                                "reemplazo": palabra_seleccionada,
                                "puntaje": tabla_sentimientos.obtener_puntaje(
                                    palabra_seleccionada
                                    ),
                                },
                            )
                # Si selecciona volver, continua el ciclo

            elif opcion == 3:
                print(f"Palabra '{palabra}' será ignorada.")
                return ("ignorada", {"palabra": palabra})

            elif opcion == 4:
                print("Procesamiento cancelado por el usuario.")
                return ("cancelada", None)

            else:
                print("Opción no válida. Intente nuevamente.")

        except ValueError:
            print("Entrada inválida. Por favor ingrese un número del 1 al 4.")
