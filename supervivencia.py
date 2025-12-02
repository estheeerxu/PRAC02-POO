
from interfazterminal import InterfazTerminal
from excepciones import ErrorDeConexion # type: ignore # para excepcion personalizada

interfaz = InterfazTerminal() # instanciamos clase InterfazTerminal
try:
    interfaz.ejecutar()           # y llamamos a su metodo ejecutar que procesa la linea de comando 
                              # y llama a los métodos correspondientes del comunicador
except ErrorDeConexion as e:
    e.imprime_error()
    exit() # innecesario