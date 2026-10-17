import socket

BUFSIZE = 16

def text_to_bytes(ruta: str):
    """str -> bytes
    toma ruta a archivo, lo abre con open() y codifica en bytes"""
    with open(ruta) as file:
        text = file.read()

    return text.encode()


def send_chunks(cadena: bytes, origin: socket.socket, to: tuple[str, int]) -> None:
    """bytes socket (str, int) -> None
    toma mensaje en bytes y lo envia por socket udp a la direccion to"""
    while cadena:
        contenido = cadena[:BUFSIZE]
        origin.sendto(contenido, to)
        cadena = cadena[BUFSIZE:]
        _ , _ = origin.recvfrom(BUFSIZE)

    origin.sendto(b"1", to)


def recv_chunks(receiver: socket.socket) -> str:
    msg = bytearray()
    mensaje_parcial, cliente_ad = receiver.recvfrom(BUFSIZE)

    while mensaje_parcial != b"1":
        msg.extend(mensaje_parcial)
        receiver.sendto(b"1", cliente_ad)

        mensaje_parcial, _ = receiver.recvfrom(BUFSIZE)

    return msg.decode()



    
    



    



def receive_full_msg(receiver: socket.socket, bufsize: int = BUFSIZE):
    final_msg = ""

    partial_msg, sender_ad = receiver.recvfrom(bufsize)

    final_msg += partial_msg.decode()
    