import SocketTCP

address = ("localhost", 5000)

server_socket = SocketTCP.SocketTCP()
server_socket.bind(address)
print(server_socket)

connection_socketTCP, new_address = server_socket.accept()

buff_size = 16
mensaje_cliente = bytearray()

trozo = connection_socketTCP.recv(buff_size)
mensaje_cliente.extend(trozo)

while connection_socketTCP.bytes_restantes > 0:
    trozo = connection_socketTCP.recv(buff_size)
    mensaje_cliente.extend(trozo)

print("\n--- CONTENIDO RECIBIDO DE ../html/index.html ---")
print(mensaje_cliente.decode())
print("------------------------------------------------\n")


connection_socketTCP.recv_close()
server_socket.socket.close()