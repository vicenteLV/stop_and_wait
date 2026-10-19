import socket
import SocketTCP


server_socket = SocketTCP.SocketTCP()

server_socket.bind_ad = ("localhost", 5000)

server_socket.bind()
print(server_socket)

while True:

    connection_socketTCP, new_adress = server_socket.accept()

    """
    mensaje_cliente = server_socket.recv_chunks()

    print(mensaje_cliente)
    """
    