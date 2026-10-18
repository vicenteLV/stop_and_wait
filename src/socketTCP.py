import socket

class socketTCP:


    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_ad = None
        self.dest_ad = None
        self.seq_number = None


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
            "syn": SYN,
            "ack": ACK,
            "fin": FIN,
            "seq": seq,
            "payload": payload
        }





if __name__ == "__main__":
    mi_socket = socketTCP()
