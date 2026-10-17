import socket
import aux_sockets


cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ad = ("localhost", 5000)

while True:
    ruta_archivo = input("Ruta del archivo: ")

    if ruta_archivo == "cerrar":
        cliente_socket.close()
        break

    archivo_en_bytes = aux_sockets.text_to_bytes(ruta_archivo)

    aux_sockets.send_chunks(archivo_en_bytes, cliente_socket, server_ad)
    
