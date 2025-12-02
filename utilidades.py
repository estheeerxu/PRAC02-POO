import re # para expresiones regulares

class Utilidades():
    def __init__(self):
        self.lista1=[] # lista 1 para almacenar mensajes
        self.lista2=[] # lista 2 para almacenar mensajes


    def mostrar_mensajes_1(self):
        if self.lista1:
            for m in self.lista1:
                print(m)

    def mostrar_mensajes_2(self):
        if self.lista2:
            for m in self.lista2:
                print(m)

    def extraer_coord(self,texto):
        """
        Extrae lat, lon y alt de un mensaje tipo:
        '... lat=42.681800, lon=-2.966400, alt=475 m'
        Devuelve (lat, lon, alt) como floats o None si no encuentra algo.
        """

        patron_lat = r"lat\s*=\s*([-+]?[0-9]*\.?[0-9]+)"
        patron_lon = r"lon\s*=\s*([-+]?[0-9]*\.?[0-9]+)"
        patron_alt = r"alt\s*=\s*([-+]?[0-9]*\.?[0-9]+)"

        m_lat = re.search(patron_lat, texto)
        m_lon = re.search(patron_lon, texto)
        m_alt = re.search(patron_alt, texto)

        if not (m_lat and m_lon and m_alt):
            return None  # No estan todos los datos

        lat = float(m_lat.group(1))
        lon = float(m_lon.group(1))
        alt = float(m_alt.group(1))

        return (lat, lon, alt)


#########

"""
Uti=Utilidades()

Uti.lista_mqtt.append("mqtt-01")
Uti.lista_mqtt.append("mqtt-02")
Uti.lista_mqtt.append("mqtt-03")

Uti.lista_meshtastic.append("meshtastic-01")
Uti.lista_meshtastic.append("meshtastic-02")

Uti.mostrar_mensajes_meshtastic()
Uti.mostrar_mensajes_mqtt()
"""