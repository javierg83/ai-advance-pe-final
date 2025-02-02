#!/usr/bin/env python

"""
Este módulo contiene los diferentes moderadores que son utilizados en el flujo.

Funciones disponibles:
- moderador_generico: Se activa revisión con moderador generico de Open AI.
- moderador_intencion: Moderador que controla que las preguntas esten en el ambito medico. (REVISAR)
"""






def moderador_generico():
    """Moderador generico de OpenAI."""
    print("\nAca va el moderador generico de OpenAI")
    

    return "salida moderador"



def moderador_intencion():
    """Moderador de intencion para filtar llamados genericos o fuera del ambito de la salud establecido."""
    print("\nAca va el moderador de Intencion")
    

    return "salida moderador"
