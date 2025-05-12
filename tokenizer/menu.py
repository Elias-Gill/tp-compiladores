def manejar_palabra_desconocida(palabra, tabla_sentimientos, tokenizador):
    """
    Muestra un menú interactivo para manejar palabras no encontradas en la tabla de símbolos.

    Args:
        palabra (str): Palabra no reconocida
        tabla_sentimientos (TablaSentimientos): Instancia de la tabla de símbolos
        tokenizador: Instancia del tokenizador para posibles actualizaciones

    Returns:
        tuple: (acción_tomada, datos_relevantes)
               acciones: 'agregada', 'reemplazada', 'ignorada', 'cancelada'
               datos: información relevante según la acción
    """
    print(f"\nPalabra no reconocida: '{palabra}'")

    while True:
        print("\nOpciones:")
        print("1. Agregar palabra a la tabla de símbolos")
        print("2. Ver sugerencias de palabras similares")
        print("3. Ignorar y continuar")
        print("4. Cancelar procesamiento")

        try:
            opcion = int(input("Seleccione una opción (1-4): "))

            if opcion == 1:
                # Opción para agregar nueva palabra
                while True:
                    try:
                        puntaje = int(
                            input(
                                f"Ingrese puntaje de sentimiento para '{palabra}' "
                                f"(ej. 2 para positivo, -1 para negativo, 0 para neutral): "
                            )
                        )
                        break
                    except ValueError:
                        print("Error: Debe ingresar un número entero para el puntaje.")

                # Agregar la palabra a la tabla
                tabla_sentimientos.agregar_palabra(palabra, puntaje)

                # Reconstruir AFD si es necesario
                if hasattr(tokenizador, "_construir_afd"):
                    tokenizador._construir_afd()

                print(f"✓ Palabra '{palabra}' agregada con puntaje {puntaje}.")
                return (
                    "agregada",
                    {"palabra": palabra, "puntaje": puntaje, "tipo": "PALABRA"},
                )

            elif opcion == 2:
                # Opción para mostrar sugerencias (simplificada)
                palabras_conocidas = list(tabla_sentimientos.palabras.keys())

                # TODO: Implementar mejor sistema de sugerencias (Levenshtein, etc.)
                sugerencias = [
                    p
                    for p in palabras_conocidas
                    if p.startswith(palabra[0]) and len(p) >= len(palabra) - 1
                ][
                    :5
                ]  # Limitar a 5 sugerencias

                if not sugerencias:
                    print("No se encontraron sugerencias adecuadas.")
                    continue

                print("\nSugerencias disponibles:")
                for i, sug in enumerate(sugerencias, 1):
                    print(
                        f"{i}. {sug} (Puntaje: {tabla_sentimientos.obtener_puntaje(sug)})"
                    )

                print(f"{len(sugerencias)+1}. ↩ Volver al menú anterior")

                try:
                    seleccion = int(input("\nSeleccione una opción: "))

                    if 1 <= seleccion <= len(sugerencias):
                        palabra_seleccionada = sugerencias[seleccion - 1]
                        print(
                            f"✓ Usando palabra '{palabra_seleccionada}' en lugar de '{palabra}'"
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
                    elif seleccion == len(sugerencias) + 1:
                        continue  # Volver al menú principal
                    else:
                        print("Opción fuera de rango. Intente nuevamente.")
                except ValueError:
                    print("Entrada inválida. Debe ingresar un número.")

            elif opcion == 3:
                print(f"✓ Palabra '{palabra}' será ignorada.")
                return ("ignorada", {"palabra": palabra})

            elif opcion == 4:
                print("✗ Procesamiento cancelado por el usuario.")
                return ("cancelada", None)

            else:
                print("Opción no válida. Intente nuevamente.")

        except ValueError:
            print("Error: Debe ingresar un número del 1 al 4.")
