import socket
import random

class SocketTCP:
    CONT_BUF_SIZE = 16 #tamaño maximo de contenido en un mensaje
    HEADER_SIZE = 5 #1 byte para flags, 4 bytes para seq
    UDP_BUF_SIZE = CONT_BUF_SIZE + HEADER_SIZE #bytes totales
    TIMEOUT = 2.0

    def __init__(self):
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_ad: tuple[str, int] = None
        self.dest_ad: tuple[str, int] = None

        #comunicacion
        self.syn: bool = False
        self.ack: bool = False
        self.fin: bool = False
        self.seq: int = 0
        self.payload: bytes = b""
        self.segment_dict: dict = {
            "syn": self.syn,     
            "ack": self.ack,
            "fin": self.fin,
            "seq": self.seq,
            "payload": self.payload
        }

        #control para recv()
        self.bytes_restantes: int = 0
        self.buffer_sobrante: bytes = b""


    def __del__(self):
        try:
            self.socket.close()
            print("Socket cerrado")
        except:
            pass



    def __str__(self):
        if (self.bind_ad != None):
            return f"Socket servidor\nEscucha en {self.bind_ad}"
        else:
            return f"Socket cliente\nConsulta a {self.dest_ad}"



    def update_segment_dict(self):
        """SocketTCP -> None
        actualiza diccionario que usa el socket en base a flags"""
        self.segment_dict["syn"] = self.syn
        self.segment_dict["ack"] = self.ack
        self.segment_dict["fin"] = self.fin
        self.segment_dict["seq"] = self.seq
        self.segment_dict["payload"] = self.payload



    def update_flags(self):
        """SocketTCP -> None
        actualiza flags en base a diccionario"""
        self.syn = self.segment_dict["syn"]
        self.ack = self.segment_dict["ack"]
        self.fin = self.segment_dict["fin"]
        self.seq = self.segment_dict["seq"]
        self.payload = self.segment_dict["payload"]



    def bind(self, address: tuple[str, int]):
        """SocketTCP tuple[str, int] -> None
        asocia el socket udp a la direccion de vinculacion"""
        self.bind_ad = address
        self.socket.bind(self.bind_ad)



    def connect(self, address: tuple[str, int]):
        """SocketTCP tuple[str, int] -> None
        lado del cliente del 3 way handshake"""
        self.dest_ad = address

        #inicializar variables en primer paso del handshake
        seq_inicial = random.randint(0, 100) #se guarda primer seq en una variable para comparacion en 2do paso
        self.syn = True
        self.ack = False
        self.fin = False
        self.seq = seq_inicial
        self.payload = b""

        #primer paso
        self.update_segment_dict() #actualizar diccionario para mensajes del socket
        syn_segment = self.create_segment(self.segment_dict)
        self.socket.sendto(syn_segment, self.dest_ad) 
        print("SYN enviado...") 

        #esperar syn_ack de vuelta, 2do paso
        syn_ack_segment, _ = self.socket.recvfrom(self.UDP_BUF_SIZE)
        print("SYN-ACK recibido")
        self.segment_dict = self.parse_segment(syn_ack_segment)

        #enviar ACK
        if self.segment_dict["syn"] and self.segment_dict["ack"] and not self.segment_dict["fin"]:
            if self.segment_dict["seq"] == (seq_inicial + 1):
                self.syn = False
                self.ack = True
                self.fin = False
                self.seq = seq_inicial + 2
                self.payload = b""

                self.update_segment_dict()
                ack_segment = self.create_segment(self.segment_dict)
                self.socket.sendto(ack_segment, self.dest_ad) #3er paso
                print("ACK enviado")

                #actualizar dest_ad
                self.dest_ad = (self.dest_ad[0], self.dest_ad[1] + 1)
                return

            else:
                print("SEQ en segundo paso no coincide")
        else:
            print("Flags no corresponden a SYN-ACK")




    def accept(self):
        """SocketTCP -> None
        lado del servidor del 3 way handshake"""
        #espera SYN del cliente
        syn_segment, cliente_ad = self.socket.recvfrom(self.UDP_BUF_SIZE)
        print("Primer SYN recibido")
        self.segment_dict = self.parse_segment(syn_segment)
        seq_inicial = self.segment_dict["seq"]

        #2do paso del handshake, responder con syn_ack
        if self.segment_dict["syn"] and not self.segment_dict["ack"] and not self.segment_dict["fin"]:
            self.syn = True
            self.ack = True
            self.fin = False
            self.seq = seq_inicial + 1
            self.payload = b""

            self.update_segment_dict()
            syn_ack_segment = self.create_segment(self.segment_dict)
            self.socket.sendto(syn_ack_segment, cliente_ad)  
            print("SYN-ACK enviado")
        else:
            print("Flags no corresponden a mensaje de sincronización")

        #3er paso
        ack_segment, _ = self.socket.recvfrom(self.UDP_BUF_SIZE)
        self.segment_dict = self.parse_segment(ack_segment)
        if not self.segment_dict["syn"] and self.segment_dict["ack"] and not self.segment_dict["fin"]:
            if self.segment_dict["seq"] == seq_inicial + 2:
                self.update_flags()
                print(f"ACK recibido\nConexion establecida con {cliente_ad}")

                #socket de comunicacion
                socket_comunicacion = SocketTCP() 
                #puerto distinto (+1)
                socket_comunicacion_ad = (self.bind_ad[0], self.bind_ad[1] + 1)
                socket_comunicacion.bind(socket_comunicacion_ad)
                socket_comunicacion.dest_ad = cliente_ad
                socket_comunicacion.seq = self.seq #sincronizado en seq_inicial + 2
                socket_comunicacion.bind()

                print(f"Canal de comunicacion establecido en {socket_comunicacion_ad}")

                return socket_comunicacion, socket_comunicacion_ad
            else:
                print("SEQ del mensaje ACK no corresponde")

        else:
            print("Problema con flags del ACK")



    def send(self, message: bytes) -> None:
        """SocketTCP bytes -> None
        envia mensajes con stopo and wait en trozos de maximo 16 bytes"""
        self.socket.settimeout(self.TIMEOUT)

        #primer segmento informa del largo
        largo_payload = str(len(message)).encode() #en primer mensaje será el contenido
        self.syn = False
        self.ack = False
        self.fin = False
        self.payload = largo_payload
        self.update_segment_dict()
        primer_segmento = self.create_segment(self.segment_dict)

        seq_esperado = self.seq + len(largo_payload)
        enviado = False
        while not enviado:
            try:
                self.socket.sendto(primer_segmento, self.dest_ad)
                primer_ack, _ = self.socket.recvfrom(self.UDP_BUF_SIZE)
                primer_ack_dict = self.parse_segment(primer_ack)

                if not primer_ack_dict["syn"] and primer_ack_dict["ack"] and not primer_ack_dict["fin"]:
                    if primer_ack_dict["seq"] == seq_esperado:
                        self.seq = seq_esperado
                        enviado = True
                        print(f"Mensaje de {len(message)} bytes en camino")
            except socket.timeout:
                print("[TIMEOUT ERROR] reenviando segmento de largo")

        #de aqui en adelante se envia el contenido
        bytes_en_camino = message
        while bytes_en_camino:
            contenido = bytes_en_camino[:self.CONT_BUF_SIZE]
            self.syn = False
            self.ack = False
            self.fin = False
            self.payload = contenido
            self.update_segment_dict()
            segment = self.create_segment(self.segment_dict)

            seq_esperado = self.seq + len(contenido)
            contenido_confirmado = False
            while not contenido_confirmado:
                try:
                    self.socket.sendto(segment, self.dest_ad)
                    segmento_respuesta, _ =self.socket.recvfrom(self.UDP_BUF_SIZE)
                    ack_dict = self.parse_segment(segmento_respuesta)

                    if not ack_dict["syn"] and ack_dict["ack"] and not ack_dict["fin"]:
                        if ack_dict["seq"] == seq_esperado:
                            self.seq = seq_esperado
                            bytes_en_camino = bytes_en_camino[self.CONT_BUF_SIZE:]
                            contenido_confirmado = True
                except socket.timeout:
                    print(f"[TIMEOUT ERROR] reenviando segmento con seq = {self.seq} ...")



    def recv(self, buff_size: int) -> bytes:
        """SocketTCP int -> bytes
        recibe hasta 16 bytes de contenido usando stop and wait"""
        self.socket.settimeout(self.TIMEOUT)

        #si no quedan pendientes, esperar
        if self.bytes_restantes == 0:
            recibido = False
            while not recibido:
                try:
                    primer_segmento, cliente_ad = self.socket.recvfrom(self.UDP_BUF_SIZE)
                    self.dest_ad = cliente_ad
                    self.segment_dict = self.parse_segment(primer_segmento)

                    if not self.segment_dict["syn"] and not self.segment_dict["ack"] and not self.segment_dict["fin"]:
                        if self.segment_dict["seq"] == self.seq:
                            largo_esperado = int(self.segment_dict["payload"].decode())
                            self.bytes_restantes = largo_esperado

                            #actualizar seq y enviar ACK del largo
                            self.seq += len(self.segment_dict["payload"])
                            self.syn = False
                            self.ack = True
                            self.fin = False
                            self.payload = b""
                            self.update_segment_dict()
                            primer_ack = self.create_segment(self.segment_dict)
                            self.socket.sendto(primer_ack, self.dest_ad)
                            recibido = True
                        elif self.segment_dict["seq"] < self.seq:
                            #segmento duplicado porquese perdio el ACK anterior, reenviar ACK actual
                            self.syn = False
                            self.ack = True
                            self.fin = False
                            self.payload = b""
                            self.update_segment_dict()
                            ack_dup = self.create_segment(self.segment_dict)
                            self.socket.sendto(ack_dup, self.dest_ad)
                except socket.timeout:
                    print("[TIMEOUT ERROR] esperando segmento de largo...")

        #cuantos bytes debe entregar esta llamada a recv
        bytes_a_entregar = min(self.bytes_restantes, buff_size)

        #cargar cualquier byte sobrante de la llamada anterior a la funcipn
        msg = bytearray(self.buffer_sobrante)
        self.buffer_sobrante = b""

        #recibir segmentos de datos hasta juntar al menos bytes_a_entregar
        while len(msg) < bytes_a_entregar:
            try:
                segmento_msg, cliente_ad = self.socket.recvfrom(self.UDP_BUF_SIZE)
                self.dest_ad = cliente_ad
                self.segment_dict = self.parse_segment(segmento_msg)

                if not self.segment_dict["syn"] and not self.segment_dict["ack"] and not self.segment_dict["fin"]:
                    if self.segment_dict["seq"] == self.seq:
                        #segmento nuevo esperado, guardar datos e incrementar seq
                        msg.extend(self.segment_dict["payload"])
                        self.seq += len(self.segment_dict["payload"])

                        self.syn = False
                        self.ack = True
                        self.fin = False
                        self.payload = b""
                        self.update_segment_dict()
                        ack_segment = self.create_segment(self.segment_dict)
                        self.socket.sendto(ack_segment, self.dest_ad)
                    elif self.segment_dict["seq"] < self.seq:
                        print(f"Segmento duplicado (seq={self.segment_dict["seq"]}), reenviando ACK...")
                        self.syn = False
                        self.ack = True
                        self.fin = False
                        self.payload = b""
                        self.update_segment_dict()
                        ack_segment = self.create_segment(self.segment_dict)
                        self.socket.sendto(ack_segment, self.dest_ad)
            except socket.timeout:
                print("[TIMEOUT ERROR] esperando segmento de datos...")

        #cortar bytes a entregar y guardar el resto en buffer
        datos_retorno = bytes(msg[:bytes_a_entregar])
        self.buffer_sobrante = bytes(msg[bytes_a_entregar:])
        self.bytes_restantes -= len(datos_retorno)

        return datos_retorno



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
        toma header tcp en bytes (5 + payload) y retorna diccionario"""
        flags = segment[0]  #primer byte de flags
        #00000111: marcados con uno son los bits de syn, ack y fin (desde el menos al mas significativo)
        SYN = bool(flags & 1) #00000001
        ACK = bool(flags & 2) #00000010
        FIN = bool(flags & 4) #00000100

        seq = int.from_bytes(segment[1:5], byteorder="big")
        payload = segment[5:]

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
        toma diccionario de segmento tcp y lo transforma a bytes (5 mas payload)"""
        SYN = 1 if header_dict["syn"] else 0
        ACK = 2 if header_dict["ack"] else 0
        FIN = 4 if header_dict["fin"] else 0

        flags_bytes = bytes([SYN | ACK | FIN])
        seq_valor = header_dict["seq"] if header_dict["seq"] is not None else 0
        seq_bytes = seq_valor.to_bytes(4, byteorder="big")
        payload = header_dict.get("payload", b"")

        return flags_bytes + seq_bytes + payload




if __name__ == "__main__":
    mi_socket = SocketTCP()
