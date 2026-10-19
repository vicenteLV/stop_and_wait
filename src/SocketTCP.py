import socket
import random

class SocketTCP:
    CONT_BUF_SIZE = 16 #tamaño maximo de contenido en un mensaje

    def __init__(self):
        self.socket : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_ad : tuple[str, int] = None
        self.dest_ad : tuple[str, int] = None

        self.canales : list = [] 

        #comunicacion
        self.syn : bool = None
        self.ack : bool = None
        self.fin : bool = None
        self.seq : int = None
        self.payload : bytes = b""
        self.segment_dict : dict = {
            "syn": self.syn,     
            "ack": self.ack,
            "fin": self.fin,
            "seq": self.seq,
            "payload": self.payload
        }


    def __del__(self):
        self.socket.close()
        print("Socket cerrado")



    def __str__(self):
        if (self.bind_ad != None):
            print(f"Socket servidor\nEscucha en {self.bind_ad}")
        else:
            print(f"Socket cliente\nConsulta a {self.dest_ad}")



    def update_segment_dict(self):
        self.segment_dict["syn"] = self.syn
        self.segment_dict["ack"] = self.ack
        self.segment_dict["fin"] = self.fin
        self.segment_dict["seq"] = self.seq
        self.segment_dict["payload"] = self.payload



    def update_flags(self):
        self.syn = self.segment_dict["syn"]
        self.ack = self.segment_dict["ack"]
        self.fin = self.segment_dict["fin"]
        self.seq = self.segment_dict["seq"]
        self.payload = self.segment_dict["payload"]



    def bind(self):
        self.socket.bind(self.bind_ad)



    def connect(self):
        """SocketTCP -> None
        lado del cliente del 3 way handshake"""
        #inicializar variables en primer paso del handshake
        seq_inicial = random.randint(0, 100) #se guarda primer seq en una variable para comparacion en 2do paso
        self.syn = True
        self.ack = False
        self.fin = False
        self.seq = seq_inicial

        #primer paso
        self.update_segment_dict() #actualizar diccionario para mensajes del socket
        syn_segment = self.create_segment(self.segment_dict)
        self.socket.sendto(syn_segment, self.dest_ad) 
        print("SYN enviado...") 

        #esperar syn_ack de vuelta, 2do paso
        syn_ack_segment, _ = self.socket.recvfrom(self.CONT_BUF_SIZE + 2)
        print("SYN-ACK recibido")
        self.segment_dict = self.parse_segment(syn_ack_segment)

        #enviar ACK
        if (self.segment_dict["syn"] and self.segment_dict["ack"] and not self.segment_dict["fin"]):
            if self.segment_dict["seq"] == (seq_inicial + 1):
                self.syn = False
                self.ack = True
                self.fin = False
                self.seq = seq_inicial + 2

                self.update_segment_dict()
                ack_segment = self.create_segment(self.segment_dict)
                self.socket.sendto(ack_segment, self.dest_ad) #3er paso
                print("ACK enviado")

                return

            else:
                print("SEQ en segundo paso no coincide")
        else:
            print("Flags no corresponden a SYN-ACK")
        






    def accept(self):
        """SocketTCP -> None
        lado del servidor del 3 way handshake"""
        #espera SYN, buffer son 16 bytes (payload) + 2 bytes de header tcp (flags y seq)
        syn_segment, cliente_ad = self.socket.recvfrom(self.CONT_BUF_SIZE + 2)
        print("Primer SYN recibido")
        self.segment_dict = self.parse_segment(syn_segment)
        seq_inicial = self.segment_dict["seq"]

        #2do paso del handshake
        if (self.segment_dict["syn"] and not self.segment_dict["ack"] and not self.segment_dict["fin"]):
            self.syn = True
            self.ack = True
            self.fin = False
            self.seq = self.segment_dict["seq"] + 1

            self.update_segment_dict()
            syn_ack_segment = self.create_segment(self.segment_dict)
            self.socket.sendto(syn_ack_segment, cliente_ad)  
            print("SYN-ACK enviado")
        else:
            print("Flags no corresponden a mensaje de sincronización")

        ack_segment, _ = self.socket.recvfrom(self.CONT_BUF_SIZE + 2)
        print("ACK recibido")
        self.segment_dict = self.parse_segment(ack_segment)
        if (not self.segment_dict["syn"] and self.segment_dict["ack"] and not self.segment_dict["fin"]):
            if self.segment_dict["seq"] == seq_inicial + 2:
                print(f"ACK recibido\nConexion establecida con {cliente_ad}")
                socket_comunicacion = SocketTCP() 
                socket_comunicacion_ad = ("localhost", self.bind_ad[1] + 1)
                socket_comunicacion.bind_ad = socket_comunicacion_ad #mismo host distinto puerto (+1)
                socket_comunicacion.seq = self.seq
                socket_comunicacion.bind()

                return socket_comunicacion, socket_comunicacion_ad
            else:
                print("SEQ del mensaje ACK no corresponde")

        else:
            print("Problema con flags del ACK")

        

        




    def send_chunks(self, cadena: bytes) -> None:
        #generacion seq aleatorio
        self.seq = random.randint(0, 100)

        while cadena:
            contenido = cadena[:self.CONT_BUF_SIZE]
            segment_dict = {
                "syn": True,
                "ack": True,
                "fin": True,
                "seq": self.seq,
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
            "seq": self.seq,
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




if __name__ == "__main__":
    mi_socket = SocketTCP()
