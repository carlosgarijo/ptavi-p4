#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}
    def create_dicc(self, IP, line):
        newline = line.split(b' ')
        sip_user = newline[1].split(b':')[-1]
        sip_user = sip_user.decode('utf-8')
        newline = line.split(b'\r')
        expires = newline[2].split(b':')[-1][1:]
        expires = expires.decode('utf-8')
        if int(expires) > 0:
            if not sip_user in self.dicc.keys():
                self.dicc[sip_user] = [IP, expires]
        elif int(expires) == 0:
            if sip_user in self.dicc.keys():
                del self.dicc[sip_user]
        print(self.dicc)

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if line.startswith(b"REGISTER"):
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                print("El cliente nos manda " + "\n" + line.decode('utf-8'))
                self.create_dicc(IP, line)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    port = int(sys.argv[1])
    serv = socketserver.UDPServer(('', port), SIPRegisterHandler)
    print("Lanzando servidor UDP de SIP...")
    serv.serve_forever()
