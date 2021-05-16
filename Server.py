#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')


import time

import IceFlix

class Main(IceFlix.Main):
    #este init es para poder acceder a un communicator fuera del run
    def __init__ (self, comunicador,diccionario):
        self.com = comunicador
        self.dic=diccionario

    def getAuthenticator(self, current=None):
                                      
        #l=str("792F8331-6F9F-459F-8A4D-B562CC8B26D8 -t -e 1.1:tcp -h 10.0.2.13 -p 37845 -t 60000")
        aut=None
        try:
            aut=self.dic["Authenticator"][0]["valor"]
            if aut is None or aut == "":
                    raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable: 
            print("El servicio Authenticator no esta disponible")
        except IndexError:
            print("El servicio Authenticator no esta disponible")

        x = IceFlix.AuthenticatorPrx.checkedCast(aut)
        
        return x

         
    def getCatalogService(self, current=None):
        aut=None
        try:       
            aut=self.dic["Catalogo"][0]["valor"]

            if aut is None or aut == "":
                    raise IceFlix.TemporaryUnavailable
        except IceFlix.TemporaryUnavailable: 
            print("El servicio Catalog no esta disponible")
        except IndexError:
            print("El servicio Catalog no esta disponible")

        x = IceFlix.MediaCatalogPrx.checkedCast(aut)
        
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
    def __init__ (self, dic):
            self.dic = dic

    def catalogService(self, message, id,current=None):
        print("Catalogo recibido {0}".format(message))
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["Catalogo"].append(nuevoProxy)
        print(self.dic)

    def authenticationService(self, message,id, current=None):

        print("autenticador recibido {0}".format(message))
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["Authenticator"].append(nuevoProxy)
        print(self.dic)


    def mediaService(self, message, id,current=None):
        
        print("Media Stream recibido: {0}".format(message))
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["MediaStream"].append(nuevoProxy)
        print(self.dic)
      


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

        diccionario= {"Service_availability": [],"Authenticator":[],
        "MediaStream":[],"Catalogo":[],"StreamerSync":[]} 
        broker = self.communicator()
        servant = ServiceAvailability (diccionario)
        servantPrueba = Prueba()
        servantMain=Main(broker,diccionario)
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

        
        # Read the JSON into the buffer
        #jsonFile.close() # Close the JSON file
       
        nuevoToken = {}
        nuevoToken['id'] = "1"
        nuevoToken['valor'] = str(MServer)

        

        #diccionario["Service_availability"].append(nuevoToken) 
        #diccionario["mainServer"].append(nuevoToken) 
         


        # Escritura de proxys en sus archivos
        topic.subscribeAndGetPublisher(qos, MServer)
        f = open("proxys/serviceAvailability", "w")
        f.write(str(MServer))       
        f.close()
        diccionario["Service_availability"].append(nuevoToken)

        topic.subscribeAndGetPublisher(qos, MServerPrueba)
        f = open("proxys/prueba", "w")
        f.write(str(MServerPrueba))       
        f.close()

        topic.subscribeAndGetPublisher(qos, MServerMain)
        f = open("proxys/main", "w")
        f.write(str(MServerMain))       
        f.close()

        print("Main server en marchaa!")


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
