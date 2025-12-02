from dispositivo import Dispositivo
import time

class Comunicador:
    """
    Clase que abstrae el uso de Dispositivo.
    Puede operar en modo 'meshtastic' o 'mqtt' puro.
    """
    def __init__(self, modo, mensajes=None, cola=None):
        if modo not in ("meshtastic", "mqtt"):
            raise ValueError("El modo debe ser 'meshtastic' o 'mqtt'.")

        self.modo = modo
        self.mensajes = mensajes if mensajes is not None else []
        self.cola=cola # de mensajes para pasarlos a una interfaz gráfica Tkinter
        self.seguir = True

        # Configuración base
        if modo == "meshtastic":
            self.config = {
                "mqtt_broker": "mqtt.meshtastic.org",
                "mqtt_port": 1883,
                "mqtt_username": "meshdev",
                "mqtt_password": "large4cats",
                #"root_topic": "msh/EU_868/2/e/",
                "root_topic": "msh/EU_868/ES/2/e/",
                "channel": "TestMQTT",
                "key": "ymACgCy9Tdb8jHbLxUxZ/4ADX+BWLOGVihmKHcHTVyo="
            }
        else:
            self.config = {
                "mqtt_broker": "broker.emqx.io",
                "mqtt_port": 1883,
                "mqtt_username": "",
                "mqtt_password": "",
                "root_topic": "sensor/data",
                "channel": ["sen55","gas_sensor","esther"],
                "key": ""
            }

        # Crear el dispositivo
        self.dispositivo = Dispositivo(
            mqtt_broker=self.config["mqtt_broker"],
            mqtt_port=self.config["mqtt_port"],
            mqtt_username=self.config["mqtt_username"],
            mqtt_password=self.config["mqtt_password"],
            root_topic=self.config["root_topic"],
            channel=self.config["channel"],
            key=self.config["key"],
            tipo=self.modo,
            cola=self.cola,
            userdata=self.mensajes
        )

        if self.cola is not None:
            # CONECTAR UNA SOLA VEZ AQUÍ
            self.dispositivo.conectar()
            # INICIAR LOOP MQTT UNA VEZ AQUÍ
            self.dispositivo.empezar_escucha()

    def enviar(self, texto, canal=None):
        """Enviar posición GPS y mensaje de texto sin reconectar."""
        if self.cola is None:
            self.dispositivo.conectar()
            time.sleep(4)  # Espera para que se conecte

        if self.modo == "meshtastic":
            # Enviar posición + texto
            self.dispositivo.enviar_posicion()
            time.sleep(4)
            self.dispositivo.enviar_texto(texto)
        else:
            self.dispositivo.enviar_texto(texto, canal)

    def recibir(self):
        """Este método puede llamarse desde un hilo pero ya NO reconecta."""
        if self.cola is None:
            self.dispositivo.conectar()
            self.dispositivo.empezar_escucha()

        try:
            while self.seguir:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.seguir=False

        # Finalizar
        self.dispositivo.detener_escucha()
        self.dispositivo.desconectar()
        print("Escucha finalizada.")
