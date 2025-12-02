from abc import ABC, abstractmethod  #La forma habitual de implementar clases abstractas
                                     # es importar el módulo abc estándar de Python
from queue import Queue # para trabajar con colas de mensajes


class ColaAbstracta(ABC):       #Es como que la clase ColaAbstracta es Abstracta al heredar de ABC
    def __init__(self,fentrega,ventanaTk):
        self.cola_mensajes = Queue()   # cola de mensajes vacias para empezar. Atributo de instancia.
        self.fentrega=fentrega # Funcion a la que ir entregando mensaje a mensaje
        self.ventana=ventanaTk
        self.procesar_mensajes()

    @abstractmethod
    def procesar_mensajes(self): 
        pass             #pass es la instrucción vacía, no hace nada, el método area queda sin implementar


class Cola(ColaAbstracta):
    def __init__(self,fentrega,ventanaTk):
        super().__init__(fentrega,ventanaTk)

    def procesar_mensajes(self):
        while not self.cola_mensajes.empty():
            msg = self.cola_mensajes.get()
            self.fentrega(msg)  # entregamos el mensaje
        self.ventana.after(50, self.procesar_mensajes) # se revisará la cola dentro de 50 milisegundos


#########

"""
def recibo(mensaje):
    print("RECIBIDO: ",mensaje)

import time
from tkinter import * # para trabajar con una ventana Tk
ventana=Tk()
C=Cola(recibo,ventana)
C.cola_mensajes.put("UNO")
time.sleep(2)
C.cola_mensajes.put("DOS")
time.sleep(2)
ventana.mainloop() # !!
"""