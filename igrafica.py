from tkinter import *
from tkintermapview import TkinterMapView # componente para trabajar con mapas en Tkinter Requiere librería tkintermapview
##
from comunicador import Comunicador # el de la práctica 1 algo modificado
import threading # para hilos de espera de mensajes mqtt y meshtastic
import time # para usar time.sleep()
##
from multiple import Multiple # type: ignore
from excepciones import ErrorDeConexion # type: ignore # para excepcion personalizada




# -------------------------------------------------------
# FUNCIÓN: salir de la aplicación
# -------------------------------------------------------
def salir():
    ventana.destroy()


# -------------------------------------------------------
# FUNCIÓN: enviar mensaje MQTT o MESHTASTIC
# -------------------------------------------------------
def enviar_mensaje():
    mensaje = entrada_mensaje.get()
    canal = canal_var.get()
    entrada_mensaje.delete(0, END)
    if(canal=="TestMQTT"):
        comunicadorMESHTASTIC.enviar(mensaje)
    else:
        comunicadorMQTT.enviar(mensaje,canal)


# -------------------------------------------------------
# FUNCIÓN: para añadir mensajes al final del textarea
# -------------------------------------------------------
def recibir_mensaje(texto):
    texto_mensajes.configure(state="normal")       # permitir escribir
    texto_mensajes.insert(END, texto + "\n")       # añadir al final
    texto_mensajes.configure(state="disabled")     # impedir edición
    texto_mensajes.see(END)                        # scroll automático
    #Si hay coordenadas GPS ponemos marcador en el mapa
    tupla=M.extraer_coord(texto)
    if(tupla is not None):
        actualizar_coordenadas(tupla[0],tupla[1])



# -------------------------------------------------------
# FUNCIÓN: actualizar mapa con nuevas coordenadas
# -------------------------------------------------------
def actualizar_coordenadas(lat, lon):
    global marcador_actual
    # Eliminar marcador previo si lo hay
    if marcador_actual is not None:
        marcador_actual.delete()

    marcador_actual = mapa.set_marker(lat, lon)
    mapa.set_position(lat, lon)
    mapa.set_zoom(18)            # zoom con mucho detalle, se ven calles cercanas


# -------------------------------------------------------
# VENTANA PRINCIPAL
# -------------------------------------------------------
ventana = Tk()
ventana.title("PRACTICA2")
ventana.geometry("900x900")

marcador_actual = None  # para el mapa


# -------------------------------------------------------
# ETIQUETA TÍTULO PRINCIPAL
# -------------------------------------------------------
label_titulo = Label(ventana, text="MQTT / MESTASHTIC",
                     font=("Arial", 18, "bold"))
label_titulo.pack(pady=5)


# -------------------------------------------------------
# RADIO BUTTONS CANAL
# -------------------------------------------------------
frame_radios = Frame(ventana)
frame_radios.pack(pady=5)

Label(frame_radios, text="CANAL:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)

canal_var = StringVar(value="TestMQTT")
opciones = ["TestMQTT", "sen55", "gas_sensor", "esther"] # los 4 canales

for i, op in enumerate(opciones):
    r = Radiobutton(frame_radios, text=op, variable=canal_var, value=op)
    r.grid(row=0, column=i+1, padx=5)


# -------------------------------------------------------
# ETIQUETA PARA MENSAJE a ENVIAR
# -------------------------------------------------------
Label(ventana, text="MENSAJE a ENVIAR",
      font=("Arial", 12, "bold")).pack(pady=(5, 2))


# -------------------------------------------------------
# CAMPO PARA MENSAJE a ENVIAR
# -------------------------------------------------------
frame_envio = Frame(ventana)
frame_envio.pack(pady=5)

entrada_mensaje = Entry(frame_envio, width=50)
entrada_mensaje.grid(row=0, column=0, padx=10)

boton_enviar = Button(frame_envio, text="ENVIAR", command=enviar_mensaje)
boton_enviar.grid(row=0, column=1, padx=10)


# -------------------------------------------------------
# ETIQUETA "MENSAJES RECIBIDOS"
# -------------------------------------------------------
Label(ventana, text="MENSAJES RECIBIDOS",
      font=("Arial", 12, "bold")).pack(pady=(5, 5))


# -------------------------------------------------------
# TEXT AREA + SCROLL
# -------------------------------------------------------
frame_texto = Frame(ventana)
frame_texto.pack()

scroll = Scrollbar(frame_texto)
scroll.pack(side=RIGHT, fill=Y)

texto_mensajes = Text(frame_texto, width=80, height=12,
                      state="disabled", wrap="word",
                      yscrollcommand=scroll.set)
texto_mensajes.pack()

scroll.config(command=texto_mensajes.yview)


# -------------------------------------------------------
# ETIQUETA "ULTIMAS COORDENADAS", para el mapa
# -------------------------------------------------------
Label(ventana,
      text="ULTIMAS COORDENADAS GPS (lat,lon) MESHTASTIC RECIBIDAS",
      font=("Arial", 12, "bold")).pack(pady=(5, 5))


# -------------------------------------------------------
# MAPA
# -------------------------------------------------------
frame_mapa = Frame(ventana)
frame_mapa.pack(pady=5)

mapa = TkinterMapView(frame_mapa, width=800, height=300)
mapa.pack()

# Puerta del Sol (Madrid)
lat0, lon0 = 40.4168, -3.7038
mapa.set_position(lat0, lon0)
mapa.set_zoom(18)
marcador_actual = mapa.set_marker(lat0, lon0, text="Puerta del Sol")


# -------------------------------------------------------
# BOTÓN SALIR
# -------------------------------------------------------
boton_salir = Button(ventana, text="SALIR", command=salir,
                     fg="white", bg="red", width=12)
boton_salir.pack(pady=5)
# -------------------------------------------------------


M=Multiple(recibir_mensaje,ventana) # Instacia de un objeto de la clase Multiple que hereda de otras 2: Cola y Utilidades


#DECORADORES para Decorar los métodos mostrar_mensajes_1 y mostrar_mensajes_2 de M (Multiple)
# Esos métodos se han definido sin saber si una lista es de mensajes mqtt o meshtastic
# Pero desde este programa sí sabemos que los mqtt van a la lista1 y los meshtastic a la lista2
# y con estos decoradores podemos añadir un "antes" para informar si son mqtt o meshtastic
def mostrar1(func):
    def wrapper(*args, **kwargs):
        print("\nResumen de mensajes MQTT recibidos:")
        print("----------------------------------")
        func(*args, **kwargs)
        print("----------------------------------")
    return wrapper

def mostrar2(func):
    def wrapper(*args, **kwargs):
        print("\nResumen de mensajes MESHTASTIC recibidos:")
        print("----------------------------------------")
        func(*args, **kwargs)
        print("----------------------------------------")
    return wrapper
 
M.mostrar_mensajes_1 = mostrar1(M.mostrar_mensajes_1)
M.mostrar_mensajes_2 = mostrar2(M.mostrar_mensajes_2)

#COMUNICADOR
######################################################################
try:
    comunicadorMQTT = Comunicador("mqtt", M.lista1, M.cola_mensajes)
    comunicadorMESHTASTIC = Comunicador("meshtastic", M.lista2, M.cola_mensajes)
except ErrorDeConexion as e:
    e.imprime_error()
    ventana.destroy()
    exit()

hiloMQTT=threading.Thread(target=comunicadorMQTT.recibir)
hiloMQTT.start();
##comunicadorMQTT.recibir()

hiloMESHTASTIC=threading.Thread(target=comunicadorMESHTASTIC.recibir)
hiloMESHTASTIC.start()
##comunicadorMESHTASTIC.recibir()

######################################################################


ventana.mainloop()   # a la espera de eventos Tk


#FINAL####################
##########################
comunicadorMQTT.seguir=False        #para que termine su hilo
comunicadorMESHTASTIC.seguir=False  #para que termine su hilo
time.sleep(3)

# --- Resumen de mensajes recibidos ---

"""
if mensajesMQTT:
    print("\nResumen de mensajes MQTT recibidos:")
    print("--------------------------------")
    for m in mensajesMQTT:
        print(m)

if mensajesMESHTASTIC:
    print("\nResumen de mensajes MESHTASTIC recibidos:")
    print("--------------------------------")
    for m in mensajesMESHTASTIC:
        print(m)
"""
M.mostrar_mensajes_1() # se llamará al decorador mostrar1
M.mostrar_mensajes_2() # se llamará al decorador mostrar2