import socket
import random

class SocketTCP:
    CONT_BUF_SIZE = 16 #tamaño maximo de contenido en un mensaje

    def __init__(self):
        self.socket : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_ad : tuple[str, int] = None
        self.dest_ad : tuple[str, int] = None
        self.seq_number : int = None


    def __del__(self):
        self.socket.close()
        print("Socket cerrado")


    def send_chunks(self, cadena: bytes) -> None:
        #generacion seq aleatorio
        self.seq_number = random.randint(0, 100)

        while cadena:
            contenido = cadena[:self.CONT_BUF_SIZE]
            segment_dict = {
                "syn": True,
                "ack": True,
                "fin": True,
                "seq": self.seq_number,
                "payload": contenido
            }
            segment = self.create_segment(segment_dict)
            self.socket.sendto(segment, self.dest_ad)

            cadena = cadena[self.CONT_BUF_SIZE:]
            _ , _ = self.socket.recvfrom(self.CONT_BUF_SIZE)

        segment_dict["payload"] = b"1"
        final_seg = self.create_segment(segment_dict)
        self.socket.sendto(final_seg, self.dest_ad)


    def recv_chunks(self) -> str:
        msg = bytearray()
        segment, cliente_ad = self.socket.recvfrom(18)

        segment_dict = self.parse_segment(segment)
        segment_cont = segment_dict["payload"]

        response_dict = {
            "syn": True,
            "ack": True,
            "fin": True,
            "seq": self.seq_number,
            "payload": b"1"
        }

        while  segment_cont != b"1":
            msg.extend(segment_dict["payload"])
            self.socket.sendto(response_dict["payload"], cliente_ad)

            segment, _ = self.socket.recvfrom(18)
            segment_dict = self.parse_segment(segment)
            segment_cont = segment_dict["payload"]

        return msg.decode()


    @staticmethod
    def text_to_bytes(ruta: str):
        """str -> bytes
        toma ruta a archivo, lo abre con open() y codifica en bytes"""
        with open(ruta) as file:
            text = file.read()

        return text.encode()


    @staticmethod
    def create_segment(header_dict: dict) -> bytes:
        """dict -> bytes
        toma estructura de header tcp y las pasa a bytes"""
        SYN = 1 if header_dict["syn"] else 0
        ACK = 2 if header_dict["ack"] else 0
        FIN = 4 if header_dict["fin"] else 0

        flags = SYN | ACK | FIN
        payload = header_dict.get("payload", b"")

        return bytes([flags, header_dict["seq"]]) + payload
    

    @staticmethod
    def parse_segment(segment: bytes) -> dict:
        """bytes -> dict
        toma header tcp en bytes y hace slicing para sacar flags, seq y contenido"""
        flags = segment[0]  #primer byte de flags
        #00000111: marcados con uno son los bits de syn, ack y fin (desde el menos al mas significativo)
        SYN = bool(flags & 1) #00000001
        ACK = bool(flags & 2) #00000010
        FIN = bool(flags & 4) #00000100

        seq = int(segment[1])
        payload = segment[2:]

        return {
            "syn": SYN,         #bool
            "ack": ACK,         #bool
            "fin": FIN,         #bool
            "seq": seq,         #int
            "payload": payload  #bytes
        }
        





if __name__ == "__main__":
    mi_socket = SocketTCP()
