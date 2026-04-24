# core/openai_api.py
import random

def generar_pregunta():
    preguntas = [
        {
            "pregunta": "¿Qué es el ahorro?",
            "opciones": ["Gastar dinero", "Guardar dinero para el futuro", "Pedir dinero prestado"],
            "correcta": 1
        },
        {
            "pregunta": "¿Qué debes hacer si quieres comprar algo caro?",
            "opciones": ["Ahorrar poco a poco", "Gastar todo de una vez", "No hacer nada"],
            "correcta": 0
        },
        {
            "pregunta": "¿Por qué es importante ahorrar?",
            "opciones": ["Porque ayuda a cumplir metas", "Porque el dinero no sirve", "Porque es aburrido"],
            "correcta": 0
        },
        {
            "pregunta": "Si te dan 10.000 pesos, ¿cuál es una buena idea?",
            "opciones": ["Ahorrar una parte", "Gastarlo todo", "Pedir más dinero"],
            "correcta": 0
        }
    ]

    return random.choice(preguntas)
