import re

def analizar_sentimiento(lexemas, tabla_sentimientos, tokenizador):
    puntaje_total = 0
    palabras_positivas = []
    palabras_negativas = []

    palabras_rudas_detectadas = False

    for lexema in lexemas:
        estado, es_aceptado = tokenizador.afd.evaluar_lexema(lexema)
        if es_aceptado and estado == 'q_PALABRA_PROHIBIDA':
            palabras_rudas_detectadas = True
            break 

    if palabras_rudas_detectadas:
        return {
            "sentimiento": "Negativo",
            "puntaje_total": -1,
            "palabras_positivas": [],
            "palabras_negativas": []
        }
    
    for lexema in lexemas:
        puntaje = tabla_sentimientos.obtener_puntaje(lexema)
        puntaje_total += puntaje

        if puntaje > 0:
            palabras_positivas.append(lexema)
        elif puntaje < 0:
            palabras_negativas.append(lexema)
    
    sentimiento = "Positivo" if puntaje_total > 0 else "Negativo" if puntaje_total < 0 else "Neutral"
    
    return {
        "sentimiento": sentimiento,
        "puntaje_total": puntaje_total,
        "palabras_positivas": palabras_positivas,
        "palabras_negativas": palabras_negativas
    }

# Función para verificar el protocolo de atención 
def verificar_protocolo(lexemas, tokenizador):
    resultados = {
        "saludo": False,
        "identificacion": False,
        "despedida": False,
        "palabras_prohibidas": False
    }

    analizando_agente = False
    mensaje_agente = []

    for lexema in lexemas:
        # Detectar inicio de mensaje del agente
        if "agente:" in lexema:
            analizando_agente = True
            mensaje_agente.append(lexema.split("agente:", 1)[1].strip())
        elif "cliente:" in lexema and analizando_agente:
            # Si encontramos "cliente:", terminamos el análisis del agente
            analizando_agente = False
            # Procesar el mensaje del agente
            procesar_mensaje_agente(mensaje_agente, tokenizador, resultados)
            mensaje_agente = []  # Reiniciar el mensaje

        elif analizando_agente:
            # Si aún estamos en la sección del agente, añadir el lexema
            mensaje_agente.append(lexema)

    # Procesar cualquier mensaje de agente restante (si el texto termina con agente)
    if mensaje_agente:
        procesar_mensaje_agente(mensaje_agente, tokenizador, resultados)

    return resultados

def procesar_mensaje_agente(mensaje_agente, tokenizador, resultados):
    mensaje = ' '.join(mensaje_agente)
    lexemas = re.findall(r'\b\w+\b', mensaje.lower())

    for lexemas in lexemas:
        estado,es_aceptado = tokenizador.afd.evaluar_lexema(lexemas)

        if es_aceptado:
            if estado == 'q_SALUDO':
                resultados["saludo"] = True
            elif estado == 'q_IDENTIFICACION':
                resultados["identificacion"] = True
            elif estado == 'q_DESPEDIDA':
                resultados["despedida"] = True
            elif estado == 'q_PALABRA_PROHIBIDA':
                resultados["palabras_prohibidas"] = True
