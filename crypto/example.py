#! /usr/bin/env python

from operator import xor
import os

# Funcion de encriptacion con XOR. Toma un
# string o bytearray y lo encripta en modo ECB
# con el operador XOR, tomando de a un byte a la
# vez y encriptandolo con la clave de un byte de
# largo.
def encriptar_xor(texto_plano, clave_un_byte):

    # Si es string se pasa a bytearray (por comodidad)
    if isinstance(texto_plano, str):
        texto_plano = string_a_bytearray(texto_plano)

    texto_encriptado = bytearray()

    for byte in texto_plano:
        texto_encriptado.append(xor(byte, clave_un_byte))

    return texto_encriptado


# Para pasar de un string al formato bytearray, utilizado por
# la funcion anterior de encriptacion.
def string_a_bytearray(s):
    ba = bytearray()
    ba.extend(s)
    return ba


# Funcion que inspecciona el string para ver cuantos
# caracteres alfanumericos tiene y retorna la proporcion
# expresada de 0% a 100%.
def proporcion_de_alfanumericos(string):

    cantidad_alfanum = sum(c.isalnum() for c in string)

    proporcion = float(cantidad_alfanum) / len(string) * 100.0

    return proporcion


if __name__ == "__main__":

    # Abre un archivo con un string en texto plano a encriptar
    with open(os.path.join(os.path.dirname(__file__), "secreto.txt"), "rb") as in_file:
        texto_plano = bytearray(in_file.read())

    # Se realiza la encripcion con todas las claves posibles, 256 combinaciones.
    texto_encriptado = [None] * 256
    for clave in range(256):
        texto_encriptado[clave] = encriptar_xor(texto_plano, clave)


    # Para visualizar los textos encriptados se convierten a string.
    texto_encriptado_como_string = []
    for clave in range(256):
        try:
            ascii_string = texto_encriptado[clave].decode("ascii")

            texto_encriptado_como_string.append((clave, ascii_string))

        except UnicodeDecodeError:
            # print("No es un string ascii valido")
            pass


    # Opcionalmente, solo para que quede mas claro, se puede ordenar
    # la lista de texto encriptado (en formato string) segun
    # la cantidad de caracteres alfanumericos
    # texto_encriptado_como_string = [x for x in sorted(texto_encriptado_como_string,
    #                                                  key = lambda par: proporcion_de_alfanumericos(par[1]),
    #                                                  reverse= True)]

    # Se imprimen todas las posibles encripciones del texto plano secreto,
    # incluyendo entre parentesis la proporcion de caracteres alfanumericos.
    for (clave, string) in texto_encriptado_como_string:
        print("Clave: 0x{:02x} ({: >5.2f}%). Encriptado: {:s}".format(
            clave,
            proporcion_de_alfanumericos(string),
            "".join(c if (ord(c) >= 32) else '.' for c in string)
            # Reemplazo los chars que no se imprimen por puntos
        ))
