import argparse
import sys
from comunicador import Comunicador

class InterfazTerminal:
    """
    Clase encargada de procesar los argumentos de línea de comando
    y ejecutar las acciones adecuadas mediante Comunicador.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Herramienta de supervivencia: comunicación MQTT o Meshtastic"
        )
        self.parser.add_argument(
            "--modo",
            required=True,
            choices=["mqtt", "meshtastic"],
            help="Selecciona el modo de funcionamiento"
        )

        # Canal (solo usado si modo=mqtt y se envía un mensaje)
        self.parser.add_argument(
            "--canal",
            help="Canal MQTT al que enviar el mensaje (solo para modo mqtt y envío)"
        )

        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--enviar", metavar="MENSAJE", help="Envía un mensaje de texto")
        group.add_argument("--recibir", action="store_true", help="Escucha mensajes entrantes")

    def ejecutar(self, argv=None):
        """Procesa la línea de comandos y ejecuta la acción correspondiente."""
        args = self.parser.parse_args(argv)

        canales_validos = ["sen55", "gas_sensor", "esther"]

        # --- Validaciones ---
        if args.modo == "mqtt" and args.enviar:
            if not args.canal:
                print("Error: en modo MQTT al enviar debes especificar un canal con --canal.")
                print(f"Canales disponibles: {', '.join(canales_validos)}")
                sys.exit(1)
            if args.canal not in canales_validos:
                print(f"Error: canal '{args.canal}' no válido.")
                print(f"Canales disponibles: {', '.join(canales_validos)}")
                sys.exit(1)

        if args.modo == "meshtastic" and args.canal:
            print("Aviso: el argumento --canal se ignora en modo Meshtastic.")

        mensajes = []
        comunicador = Comunicador(args.modo, mensajes)

        # --- Envío ---
        if args.enviar:
            if args.modo == "mqtt":
                comunicador.enviar(args.enviar, canal=args.canal)
            else:
                comunicador.enviar(args.enviar)
            print(f"Mensaje enviado correctamente ({args.modo}).")

        # --- Recepción ---
        elif args.recibir:
            print(f"Escuchando mensajes en modo {args.modo} (Ctrl+C para salir)...")
            comunicador.recibir()

        # --- Resumen de mensajes recibidos ---
        if mensajes:
            print("\nResumen de mensajes recibidos:")
            print("--------------------------------")
            for m in mensajes:
                print(m)
