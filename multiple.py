
from cola_mensajes import Cola # type: ignore
from utilidades import Utilidades # type: ignore

class Multiple(Cola,Utilidades):

    def __init__(self, fentrega, ventanaTk):
        Cola.__init__(self,fentrega,ventanaTk) # llamada al constructor de Cola
        Utilidades.__init__(self)              # llamada al constructor de Utilidades

"""
    def hola(self):
        print("HOLA DECORADOR")

#########


def recibo(mensaje):
    print("RECIBIDO: ",mensaje)

import time
from tkinter import * # para trabajar con una ventana Tk
ventana=Tk()
M=Multiple(recibo,ventana)
M.cola_mensajes.put("UNO")
M.cola_mensajes.put("DOS")
time.sleep(2)
ventana.mainloop() # !!


M.lista_mqtt.append("mqtt-01")
M.lista_mqtt.append("mqtt-02")
M.lista_mqtt.append("mqtt-03")

M.lista_meshtastic.append("meshtastic-01")
M.lista_meshtastic.append("meshtastic-02")

M.mostrar_mensajes_meshtastic()
M.mostrar_mensajes_mqtt()
"""