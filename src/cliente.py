import socket
import aux_sockets
import SocketTCP
import random


cliente_socket = SocketTCP.SocketTCP()
cliente_socket.dest_ad = ("localhost", 5000)

while True:
    ruta_archivo = input("Ruta del archivo: ")

    if ruta_archivo == "cerrar":
        del cliente_socket
        break

    archivo_en_bytes = cliente_socket.text_to_bytes(ruta_archivo)

    cliente_socket.send_chunks(archivo_en_bytes)

