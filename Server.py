#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import Server

import time

import IceFlix

class Main(IceFlix.Main):
    #este init es para poder acceder a un communicator fuera del run
    def __init__ (self, comunicador):
        self.com = comunicador

    def getAuthenticator(self, current=None):
                                      
        #l=str("792F8331-6F9F-459F-8A4D-B562CC8B26D8 -t -e 1.1:tcp -h 10.0.2.13 -p 37845 -t 60000")
        try:
            f = open("proxys/listaAut", "r")
            l=f.readline()
        
            f.close()
        
            if l is None or l is "":
                    raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable: 
            print("El servicio Authenticator no esta disponible")

        #convertimos de tipo string a tipo proxy
        #una vez que es proxy, decirque que es de tipo Authenticator
        pr = self.com.stringToProxy(l)
        x = IceFlix.AuthenticatorPrx.checkedCast(pr)

        
        return x

        
    def getCatalogService(self, current=None):
        
        try:
        
            f = open("proxys/catalogo", "r")
            l=f.readline()
        
            f.close()

            if l is None or l is "":
                    raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable: 
            print("El servicio Catalog no esta disponible")


        #convertimos de tipo string a tipo proxy
        #una vez que es proxy, decirque que es de tipo Catalog
        pr = self.com.stringToProxy(l)
        x = IceFlix.MediaCatalogPrx.checkedCast(pr)
        
        return x


    ########### Clase  Prueba  ##############

class Prueba(IceFlix.Prueba):
 
    def getPrueba(self, current=None):
        print("PRUEBA\n")
        print("Event received: ".format())
        sys.stdout.flush()

        f = open("listaAut", "r")
        l=f.readline()
        print("Soy prueba y voy a devolver: "+l+"\n")
        f.close()

        return l
    

    def pruebaVacio(self,current=None):
        print("PRUEBA VACIO\n")
        f = open("listaAut", "r")
        l=f.readline()
        print("\nESTE ES EL AUTENTICADOR: "+l+"\n")
        f.close
    ########### 

class ServiceAvailability (IceFlix.ServiceAvailability ):
    def catalogService(self, message, id,current=None):
        f = open("proxys/catalogo", "w")
        l=str(message)
        f.write(l)
        f.close()
        print("Catalogo recibido {0}".format(message))
        sys.stdout.flush()

    def authenticationService(self, message,id, current=None):
        f = open("proxys/listaAut", "w")
        l=str(message)
        f.write(l)
        f.close()
        print("autenticador recibido {0}".format(message))
        sys.stdout.flush()


    def mediaService(self, message, id,current=None):
        f = open("proxys/serviceAvailability", "w")
        l=str(message)
        f.write(l)
        f.close()
        print("Media Stream recibido: {0}".format(message))
        sys.stdout.flush()
      


class MainServer(Ice.Application):
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2

        broker = self.communicator()
        servant = ServiceAvailability ()
        servantPrueba = Prueba()
        servantMain=Main(broker)
        adapter = broker.createObjectAdapter("MainAdapter")
        MServer = adapter.addWithUUID(servant)
        MServerPrueba = adapter.addWithUUID(servantPrueba)
        MServerMain = adapter.addWithUUID(servantMain)


        topic_name = "ServiceAvailability" 
        qos = {}
        listaAut={"792F8331-6F9F-459F-8A4D-B562CC8B26D8 -t -e 1.1:tcp -h 10.0.2.13 -p 37845 -t 60000"}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

    #######
        # Escritura de proxys en sus archivos
        topic.subscribeAndGetPublisher(qos, MServer)
        f = open("proxys/serviceAvailability", "w")
        f.write(str(MServer))       
        f.close()

        topic.subscribeAndGetPublisher(qos, MServerPrueba)
        f = open("proxys/prueba", "w")
        f.write(str(MServerPrueba))       
        f.close()

        topic.subscribeAndGetPublisher(qos, MServerMain)
        f = open("proxys/main", "w")
        f.write(str(MServerMain))       
        f.close()

        print("Main server en marcha!")
       
        #f = open("listaAut", "r")
        #l=f.read()
        #print(l)

       

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(MServer)
        topic.unsubscribe(MServerPrueba)
        topic.unsubscribe(MServerMain)

        return 0


sys.exit(MainServer().main(sys.argv))
