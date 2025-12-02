class ErrorDeConexion(Exception):
    def __init__(self, servidor, puerto, usuario, tipo, mensaje="Fallo de conexión"):
        super().__init__(f"{mensaje} -> Servidor: {servidor}, Puerto: {puerto}, Usuario: {usuario}, tipo: {tipo}")
        self.mensaje=mensaje
        self.servidor=servidor
        self.puerto=puerto
        self.usuario=usuario
        self.tipo=tipo

    #Si se captura la excepción se va a poder llamar a este metodo si se desea
    def imprime_error(self):
        print("CAPTURADA EXCEPCION PERSONALIZADA")
        print(f"MENSAJE: {self.mensaje}")
        print(f"SERVIDOR: {self.servidor}")
        print(f"PUERTO: {self.puerto}")
        print(f"USUARIO: {self.usuario}")
        print(f"TIPO: {self.tipo}")


