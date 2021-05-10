#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('EsiFlix.ice')
import IceFlix

#Añadida esta clase para la comprobacion de usar comunicacion directa mediante el proxy.
#Funciono.
class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        ejemplo= IceFlix.PruebaPrx.checkedCast(proxy)

        if not ejemplo:
            raise RuntimeError('Invalid proxy')

        print(ejemplo.getPrueba())

        return 0


sys.exit(Client().main(sys.argv))
