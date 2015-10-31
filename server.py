#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time
import calendar

class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}
    def create_dicc(self, sip_user, expires, atrib_dicc):
        if expires > 0:
            if not sip_user in self.dicc.keys():
                self.dicc[sip_user] = atrib_dicc
        elif expires <= 0:
            if sip_user in self.dicc.keys():
                del self.dicc[sip_user]

    def del_user(self, actual_time, expires):
        for user in self.dicc:
            atribs = self.dicc[user]
            if actual_time >= calendar.timegm(expires):
                del self.dicc[user]

    def register2json(self):
        with open('registered.json', 'w') as outfile_json:
            json.dump(self.dicc, outfile_json, sort_keys=True,
                      indent=3, separators=(',', ': '))

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        address = self.client_address[0]
        atrib_dicc = {}
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line = line.decode('utf-8');
            if line.startswith("REGISTER"):
                print("El cliente nos manda " + "\n" + line)
                newline = line.split(' ')
                sip_user = newline[1].split(':')[-1]
                newline = line.split('\r')
                expires = int(newline[1].split(':')[-1][1:])
                expires_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()+expires))
                atrib_dicc['address'] = address
                atrib_dicc['expires'] = expires_time
                self.create_dicc(sip_user, expires, atrib_dicc)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                actual_time = time.gmtime(time.time())
                #self.del_user(actual_time, expires)
                self.register2json()
            else:
                self.wfile.write(b"Peticion recibida\r\n\r\n")
                print("El cliente nos manda " + "\n" + line)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    port = int(sys.argv[1])
    serv = socketserver.UDPServer(('', port), SIPRegisterHandler)
    print("Lanzando servidor UDP de SIP...")
    serv.serve_forever()
