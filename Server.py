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
        servantMain=Main(broker,diccionario)
        adapter = broker.createObjectAdapter("MainAdapter")
        MServer = adapter.addWithUUID(servant)
        MServerMain = adapter.addWithUUID(servantMain)

        topic_name = "ServiceAvailability" 
        qos = {}
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


        topic.subscribeAndGetPublisher(qos, MServerMain)
        f = open("proxys/main", "w")
        f.write(str(MServerMain))       
        f.close()

        print("Main server en marchaa!")
      

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(MServer)
        topic.unsubscribe(MServerMain)

        return 0


sys.exit(MainServer().main(sys.argv))
