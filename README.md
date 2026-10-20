# Actividad: Sockets con Stop & Wait

Implementación de `SocketTCP` sobre UDP usando Stop & Wait[cite: 4].

## Archivos

* `SocketTCP.py`: Clase que maneja los headers (5 bytes: 1 para flags y 4 para `seq`), el 3-way handshake, el envío/recepción en trozos de máximo 16 bytes con timeouts y el cierre de conexión[cite: 4].
* `server.py`: Escucha en `("localhost", 5000)`, acepta la conexión pasando al puerto `5001` y recibe el archivo con `recv()`.
* `cliente.py`: Se conecta al servidor, lee el archivo `../html/index.html` y lo envía por partes con `send()`.

## Ejecución

Para probar el código se deben abrir dos terminales en la carpeta donde están los archivos (teniendo el archivo de prueba en `../html/index.html`):

1. Primero correr el servidor en una terminal:
   `python3 server.py`

2. Luego correr el cliente en otra terminal:
   `python3 cliente.py`

El cliente establecerá la conexión con el servidor, enviará el archivo completo y al terminar ambos cerrarán el socket.