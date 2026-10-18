import socket
import SocketTCP


server_socket = SocketTCP.SocketTCP()

server_socket.bind_ad = ("localhost", 5000)

server_socket.bind()

while True:

    server_socket.accept()

    """
    mensaje_cliente = server_socket.recv_chunks()

    print(mensaje_cliente)
    """
    