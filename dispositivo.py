#!/usr/bin/env python3
"""
Clase Dispositivo para Meshtastic MQTT
"""

import time
import base64
import random
import re
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2
from meshtastic import BROADCAST_NUM, protocols

from queue import Queue # para trabajar con cola de mensajes
from excepciones import ErrorDeConexion  # type: ignore


class Dispositivo:
    #Constructor, se pueden pasar coordenadas GPS, por defecto las del Instituto Tecnologico de Miranda de Ebro
    def __init__(self, mqtt_broker, mqtt_port, mqtt_username, mqtt_password, root_topic, channel, key, tipo, lat="42.6818",lon="-2.9664",alt="475", cola=None, userdata=None):
        # Parámetros de conexión
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.root_topic = root_topic
        self.channel = channel
        self.key = key
        self.tipo =tipo # meshtastic / mqtt
        self.cola=cola

        # CLIENTE  
        # Segun el tipo se concretan unos callbacks u otros, para mqtt puro se usan on_connect_mqtt, 
        # on_disconnect_mqtt, on_message_mqtt
        if(tipo=='meshtastic'):
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=userdata)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
        else: #tipo=='mqtt'
            self.client = mqtt.Client(userdata=userdata)
            self.client.on_connect = self.on_connect_mqtt
            self.client.on_disconnect = self.on_disconnect_mqtt
            self.client.on_message = self.on_message_mqtt           

        # Nodo
        random_hex = ''.join(random.choices('0123456789abcdef', k=4))
        #self.node_name = '!abcd' + random_hex
        self.node_name = "!abcd5f09" #mi nodo EEESSSTTTHHHERRR
        #self.node_name = "!abcd123a" #otro nodo
        self.node_number = int(self.node_name.replace("!", ""), 16)
        self.global_message_id = random.getrandbits(32)

        # Tópicos 
        if(tipo=='meshtastic'):
            self.subscribe_topic = f"{root_topic}{channel}/#"
            ###self.publish_topic = f"{root_topic}{channel}/broadcast"
            self.publish_topic = f"{root_topic}{channel}/{self.node_name}"
        else:
            self.subscribe_topic = f"{root_topic}{channel}"
            self.publish_topic = f"{root_topic}{channel}"


        # Datos del cliente
        self.client_long_name = "Esther"
        self.client_short_name = "E.M.A"
        #self.client_long_name = ""
        #self.client_short_name = ""
        self.client_hw_model = 255
        self.lat, self.lon, self.alt = lat, lon, alt 

        # Depuración
        self.debug = True
        self.pro=False
        

    # --------------------------------------------------------------
    # Métodos de conexión MQTT
    # --------------------------------------------------------------
    def conectar(self):
        if self.debug:
            print(f"Conectando a {self.mqtt_broker}:{self.mqtt_port} ...")

        self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        try: 
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        except Exception as e:
            raise ErrorDeConexion(self.mqtt_broker,self.mqtt_port,self.mqtt_username,self.tipo,"FALLO AL CONECTAR") from e
        self.client.loop_start()

    ###
    def empezar_escucha(self):
        """Empieza a escuchar mensajes MQTT (loop_start)."""
        print("Escuchando mensajes MQTT...")
        #self.client.loop_start()
        self.pro=True

    ###
    def detener_escucha(self):
        """Detiene la escucha MQTT (loop_stop)."""
        print("Escucha detenida.")
        self.client.loop_stop()

    def desconectar(self):
        if self.debug:
            print("Desconectando...")
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Conectado al broker MQTT-MESHTASTIC ({self.mqtt_broker})")
        print(f"Suscribiéndose a: {self.subscribe_topic}")
        client.subscribe(self.subscribe_topic)

    def on_connect_mqtt(self, client, userdata, flags, reason_code):
        print(f"Conectado al broker MQTT ({self.mqtt_broker})")
        ###print(f"Suscribiéndose a: {self.subscribe_topic}")
        ###client.subscribe(self.subscribe_topic)
        #---
        # Suscribirse a los temas
        for topic in self.channel:
            client.subscribe(f"{self.root_topic}/{topic}")
            print(f"Suscrito al tema '{self.root_topic}/{topic}'")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        print("Desconectado del broker MQTT-MESHTASTIC")

    def on_disconnect_mqtt(self, client, userdata, flags, reason_code=None, properties=None):
        print("Desconectado del broker MQTT")

    # --------------------------------------------------------------
    # Recepción de mensajes
    # --------------------------------------------------------------
    def on_message_mqtt(self,client, userdata, msg):
        if(not self.pro):
           return
        try:
            texto = msg.payload.decode("utf-8")
        except Exception:
            texto = str(msg.payload)
        print(f"{self.tipo} {msg.topic}: {texto}")
        # Guardar en archivo
        with open("datos.txt", "a", encoding="utf-8") as f:
            f.write(f"{self.tipo} {msg.topic}: {texto}\n")
        # Guardar en userdata
        if isinstance(userdata, list):
            #userdata.append({"tipo": "texto", "contenido": texto})
            userdata.append(f"{self.tipo} {msg.topic}: {texto}")
        # Enviar a cola de mensajes para la interfaz Tkinter (gráfica)
        if self.cola is not None:
            self.cola.put(f"{self.tipo} {msg.topic}: {texto}")

    def on_message(self, client, userdata, msg):
        if(not self.pro):
           return
        print(f"\n[Mensaje recibido] {msg.topic}")
        try:
            se = mqtt_pb2.ServiceEnvelope()
            se.ParseFromString(msg.payload)
            mp = se.packet

            # Intentar descifrar si está encriptado
            if mp.HasField("encrypted") and not mp.HasField("decoded"):
                self._decodificar(mp)

            # --- Mensajes de texto ---
            if mp.HasField("decoded") and mp.decoded.portnum == portnums_pb2.TEXT_MESSAGE_APP:
                texto = mp.decoded.payload.decode("utf-8", errors="replace")
                #print(f"Texto_recibido: {texto}")
                print(f"{self.tipo} {msg.topic}: {texto}")
                # Guardar en archivo
                with open("datos.txt", "a", encoding="utf-8") as f:
                    #f.write(f"MENSAjE: {texto}\n")
                    f.write(f"{self.tipo} {msg.topic}: {texto}\n")
                # Guardar en userdata
                if isinstance(userdata, list):
                    #userdata.append({"tipo": "texto", "contenido": texto})
                    userdata.append(f"{self.tipo} {msg.topic}: {texto}")
                # Enviar a cola de mensajes para la interfaz Tkinter (gráfica)
                if self.cola is not None:
                    self.cola.put(f"{self.tipo} {msg.topic}: {texto}")

            # --- Coordenadas GPS ---
            elif mp.HasField("decoded") and mp.decoded.portnum == portnums_pb2.POSITION_APP:
                try:
                    pos = mesh_pb2.Position()
                    pos.ParseFromString(mp.decoded.payload)
                    lat = pos.latitude_i / 1e7
                    lon = pos.longitude_i / 1e7
                    alt = pos.altitude
                    #print(f"Posición recibida: lat={lat:.6f}, lon={lon:.6f}, alt={alt} m")
                    print(f"{self.tipo} {msg.topic}: lat={lat:.6f}, lon={lon:.6f}, alt={alt} m")
                    # Guardar en archivo
                    with open("datos.txt", "a", encoding="utf-8") as f:
                        #f.write(f"GPS: {lat:.6f}, {lon:.6f}, {alt} m\n")
                        f.write(f"{self.tipo} {msg.topic}: lat={lat:.6f}, lon={lon:.6f}, alt={alt} m\n")
                    # Guardar en userdata
                    if isinstance(userdata, list):
                        #userdata.append({"tipo": "gps", "lat": lat, "lon": lon, "alt": alt})
                        userdata.append(f"{self.tipo} {msg.topic}: lat={lat:.6f}, lon={lon:.6f}, alt={alt} m")
                    # Enviar a cola de mensajes para la interfaz Tkinter (gráfica)
                    if self.cola is not None:
                        self.cola.put(f"{self.tipo} {msg.topic}: lat={lat:.6f}, lon={lon:.6f}, alt={alt} m")
                except Exception as e:
                    print(f"Error al procesar posición: {e}")

        except Exception as e:
            print(f"Error procesando mensaje: {e}")



    def _decodificar(self, mp):
        try:
            key_bytes = base64.b64decode(self.key.encode('ascii'))
            nonce_packet_id = getattr(mp, "id").to_bytes(8, "little")
            nonce_from_node = getattr(mp, "from").to_bytes(8, "little")
            nonce = nonce_packet_id + nonce_from_node
            cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_bytes = decryptor.update(getattr(mp, "encrypted")) + decryptor.finalize()
            data = mesh_pb2.Data()
            data.ParseFromString(decrypted_bytes)
            mp.decoded.CopyFrom(data)
        except Exception as e:
            print(f"*** Error de descifrado: {e}")

    # --------------------------------------------------------------
    # Envío de mensajes
    # --------------------------------------------------------------
    def enviar_texto(self, texto, canal=None):
        if not texto:
            return
        if(self.tipo=="mqtt"):
            #self.client.publish(self.publish_topic, texto)
            self.client.publish(f"{self.root_topic}/{canal}",texto)
            return
        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.TEXT_MESSAGE_APP
        encoded_message.payload = texto.encode("utf-8")
        self._enviar_mesh(BROADCAST_NUM, encoded_message)

    def enviar_texto_OLD(self, texto):
        if not texto:
            return
        if(self.tipo=="mqtt"):
            self.client.publish(self.publish_topic, texto)
            return
        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.TEXT_MESSAGE_APP
        encoded_message.payload = texto.encode("utf-8")
        self._enviar_mesh(BROADCAST_NUM, encoded_message)        

    def enviar_posicion(self):
        pos_time = int(time.time())
        latitude = int(float(self.lat) * 1e7)
        longitude = int(float(self.lon) * 1e7)
        altitude = int(float(self.alt))

        pos = mesh_pb2.Position()
        pos.latitude_i = latitude
        pos.longitude_i = longitude
        pos.altitude = altitude
        pos.time = pos_time

        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.POSITION_APP
        encoded_message.payload = pos.SerializeToString()
        self._enviar_mesh(BROADCAST_NUM, encoded_message)

    def enviar_node_info(self):
        user_payload = mesh_pb2.User()
        user_payload.id = self.node_name
        user_payload.long_name = self.client_long_name
        user_payload.short_name = self.client_short_name
        user_payload.hw_model = self.client_hw_model

        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.NODEINFO_APP
        encoded_message.payload = user_payload.SerializeToString()
        self._enviar_mesh(BROADCAST_NUM, encoded_message)

    def _enviar_mesh(self, destino, encoded_message):
        mesh_packet = mesh_pb2.MeshPacket()
        mesh_packet.id = self.global_message_id
        self.global_message_id += 1

        setattr(mesh_packet, "from", self.node_number)
        mesh_packet.to = destino
        mesh_packet.want_ack = False
        mesh_packet.hop_limit = 3
        mesh_packet.channel = self._hash(self.channel, self.key)

        if self.key == "":
            mesh_packet.decoded.CopyFrom(encoded_message)
        else:
            mesh_packet.encrypted = self._encriptar(encoded_message, mesh_packet)

        se = mqtt_pb2.ServiceEnvelope()
        se.packet.CopyFrom(mesh_packet)
        se.channel_id = self.channel
        se.gateway_id = self.node_name

        payload = se.SerializeToString()
        self.client.publish(self.publish_topic, payload)
        print(f"Enviado a {self.publish_topic}")


    # --------------------------------------------------------------
    # Utilidades
    # --------------------------------------------------------------
    def _hash(self, name, key):
        def xor_hash(data):
            result = 0
            for char in data:
                result ^= char
            return result

        replaced_key = key.replace('-', '+').replace('_', '/')
        key_bytes = base64.b64decode(replaced_key.encode('utf-8'))
        return xor_hash(bytes(name, 'utf-8')) ^ xor_hash(key_bytes)

    def _encriptar(self, encoded_message, mesh_packet):
        key_bytes = base64.b64decode(self.key.encode('ascii'))
        nonce_packet_id = mesh_packet.id.to_bytes(8, "little")
        nonce_from_node = self.node_number.to_bytes(8, "little")
        nonce = nonce_packet_id + nonce_from_node
        cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(encoded_message.SerializeToString()) + encryptor.finalize()
