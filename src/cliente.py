import SocketTCP

address = ("localhost", 5000)
ruta_archivo = "../html/index.html"

cliente_socket = SocketTCP.SocketTCP()
cliente_socket.dest_ad = address
print(cliente_socket)

cliente_socket.connect(address)

archivo_en_bytes = cliente_socket.text_to_bytes(ruta_archivo)
cliente_socket.send(archivo_en_bytes)

#cerrar la conexión desde el lado del cliente
cliente_socket.close()
