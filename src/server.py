import socket
import aux_sockets


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ad = ("localhost", 5000)

server_socket.bind(ad)

while True:
    mensaje_cliente = aux_sockets.recv_chunks(server_socket)

    print(mensaje_cliente)
    