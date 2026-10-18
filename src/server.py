import socket
import aux_sockets
import SocketTCP


server_socket = SocketTCP.SocketTCP()

server_socket.bind_ad = ("localhost", 5000)

server_socket.socket.bind(server_socket.bind_ad)

while True:
    mensaje_cliente = server_socket.recv_chunks()

    print(mensaje_cliente)
    