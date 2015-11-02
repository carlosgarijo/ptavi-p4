#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time
from copy import deepcopy


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}

    def create_dicc(self, sip_user, expires, atrib_dicc):
        """
        Vamos añadiendo usuarios al diccionario
        o eliminando si Expires = 0
        """
        self.dicc[sip_user] = atrib_dicc
        if expires <= 0:
            del self.dicc[sip_user]

    def del_user(self, actual_time):
        """
        Comprobamos los Expires de cada usuario
        y eliminamos si es menor que la hora actual
        """
        help_dicc = deepcopy(self.dicc)
        for user in self.dicc.keys():
            atribs = self.dicc[user]
            expires = atribs['expires']
            if actual_time > expires:
                help_dicc.pop(user)
        self.dicc = help_dicc

    def register2json(self):
        """
        Creamos fichero json con el
        diccionario de usuarios
        """
        with open('registered.json', 'w') as outfile_json:
            json.dump(self.dicc, outfile_json, sort_keys=True,
                      indent=4, separators=(',', ': '))

    def json2registered(self):
        """
        Si existe fichero json lo abrimos
        y lo usamos de diccionario
        """
        try:
            with open("registered.json", 'r') as json_fich:
                datos = json.load(json_fich)
            users = datos.keys()
            for user in users:
                self.dicc[user] = datos[user]
        except:
            pass

    def handle(self):
        """
        Programa que espera las peticiones de
        usuarios y las procesa
        """
        self.json2registered()
        print(self.dicc)
        address = self.client_address[0]
        atrib_dicc = {}
        while 1:
        # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line = line.decode('utf-8')
            if line.startswith("REGISTER"):
                print("El cliente nos manda " + "\n" + line)
                newline = line.split(' ')
                sip_user = newline[1].split(':')[-1]
                newline = line.split('\r')
                expires = int(newline[1].split(':')[-1][1:])
                expires_time = time.gmtime(time.time()+expires)
                exp_time_str = time.strftime('%Y-%m-%d %H:%M:%S', expires_time)
                atrib_dicc['address'] = address
                atrib_dicc['expires'] = exp_time_str
                self.create_dicc(sip_user, expires, atrib_dicc)
                self.register2json()
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                actual_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.gmtime(time.time()))
                self.del_user(actual_time)
                self.register2json()
            else:
                if line:
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n")
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
