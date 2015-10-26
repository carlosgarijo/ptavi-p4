#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}
    def create_dicc(self, sip_user, address, expires):
        if int(expires) > 0:
            if not sip_user in self.dicc.keys():
                self.dicc[sip_user] = [address, expires]
        elif int(expires) == 0:
            if sip_user in self.dicc.keys():
                del self.dicc[sip_user]
        print(self.dicc)

    def register2json(self, sip_user):
        self.tag = []
        if sip_user in self.dicc.keys():
            help_dicc = {}
            for dato in self.dicc[sip_user]:
                if dato.startswith("127."):
                    help_dicc["address"] = dato
                else:
                    help_dicc["expires"] = dato
        self.tag.append([sip_user, help_dicc])
        print(self.tag)
        with open('registered.json', 'w') as outfile_json:
            json.dump(self.tag, outfile_json, sort_keys=True,
                      indent=3, separators=(' ', ': '))

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        address = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if line.startswith(b"REGISTER"):
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                print("El cliente nos manda " + "\n" + line.decode('utf-8'))
                newline = line.split(b' ')
                sip_user = newline[1].split(b':')[-1]
                sip_user = sip_user.decode('utf-8')
                newline = line.split(b'\r')
                expires = newline[2].split(b':')[-1][1:]
                expires = expires.decode('utf-8')
                self.create_dicc(sip_user, address, expires)
                self.register2json(sip_user)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    port = int(sys.argv[1])
    serv = socketserver.UDPServer(('', port), SIPRegisterHandler)
    print("Lanzando servidor UDP de SIP...")
    serv.serve_forever()
