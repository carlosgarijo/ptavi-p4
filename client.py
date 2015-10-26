#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""
import sys
import socket

# Cliente UDP simple.

# Dirección IP del servidor.
IP = sys.argv[1]
PORT = int(sys.argv[2])

# Contenido que vamos a enviar
metodo = sys.argv[3]
metodo = metodo.upper()
user = sys.argv[4]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP, PORT))

Mssg = metodo + " sip:" + user + " SIP/2.0\r\n\r\n"
print("Enviando: " + Mssg)

my_socket.send(bytes(Mssg, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)

print('Recibido -- ', data.decode('utf-8'))
print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
