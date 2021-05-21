#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix
import json
import uuid
import threading
import hashlib


class Authenticator(IceFlix.Authenticator):
    def __init__ (self, diccionario, diccionarioAvailability):
       
        self.dic = diccionario
        self.dicAvai = diccionarioAvailability
        


    def refreshAuthorization(self, user, passwordHash, current=None):
        #ToDo desde aqui se llama a TokenRevocation una vez pasados 30 segundos
        # topic_mgr = Autenticador.get_topic_manager()
        # topic_tokens = "AuthenticationStatus"
        # try:
        #     topic2 = topic_mgr.retrieve(topic_tokens)
        # except IceStorm.NoSuchTopic:
        #     print("no such topic found, creating")
        #     topic2 = topic_mgr.create(topic_tokens)

        # publicador = topic2.getPublisher()


        with open('credenciales.json') as f:
            
            data = json.load(f)

        #recorrer el json
        found=False
        nuevoToken = {}        
        
        
        try:
            for persona in data["usuarios"]:
                
                if(persona["nombre"] == user and persona["pass"] == passwordHash ):
                    encontrado = persona
                    found=True       

                    #nuevoToken['id'] = "1"
                    nuevoToken['valor'] = str(uuid.uuid4())   

                    self.dic["Tokens"].append(nuevoToken)   

                    #hacer el timer
                    t = threading.Timer(30.0, Token.revoke,(self,nuevoToken['valor'],))
                    t.start()  
                    
            if not found:
                raise IceFlix.Unauthorized

        except IceFlix.Unauthorized: 
            print("La persona buscada no existe")
            raise IceFlix.Unauthorized
    

        
        return nuevoToken["valor"]


        
    def isAuthorized(self, authentication, current=None):
        found = False
        
        for token in self.dic["Tokens"]:

            if authentication == token["valor"]:
                found = True
      
        
        return found


class Token(IceFlix.TokenRevocation):
    def __init__ (self, diccionario):
       
        self.dic = diccionario

    def revoke(self, authentication, current=None):
        
        found=False
       
        for tok in self.dic["Tokens"]:
            if(tok["valor"] == authentication):
                encontrado = tok
                found=True
                print(authentication)
                ## Working with buffered content
                encontrado["valor"] = ""                 
                
        if not found:
            print ("el Token NO EXISTE.")
        
        print (self.dic)
        
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


    def authenticationService(self, message,id, current=None):

        print("autenticador recibido {0}".format(message))

        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["Authenticator"].append(nuevoProxy)



    def mediaService(self, message, id,current=None):
        
        print("Media Stream recibido: {0}".format(message))

        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["MediaStream"].append(nuevoProxy)


class Autenticador(Ice.Application):
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


        diccionario = {"Tokens": []} 
        diccionarioAvailability = {"Service_availability": [],"Authenticator":[],
        "MediaStream":[],"Catalogo":[],"StreamerSync":[]}
        broker = self.communicator()
        servant = Authenticator(diccionario,diccionarioAvailability)
        servantTokenRev = Token(diccionario)
        servantAvailability = ServiceAvailability(diccionarioAvailability)
        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        autServer = adapter.addWithUUID(servant)
        tokenRevServer = adapter.addWithUUID(servantTokenRev)
        serviceAvailability = adapter.addWithUUID(servantAvailability)

        topic_name = "ServiceAvailability" 
        topic_tokens = "AuthenticationStatus"
        qos = {}
        
        try:
            topic = topic_mgr.retrieve(topic_name)
            topic2 = topic_mgr.retrieve(topic_tokens)

        except IceStorm.NoSuchTopic:
            #topic = topic_mgr.create(topic_name)
            topic2 = topic_mgr.create(topic_tokens)
            

        topic.subscribeAndGetPublisher(qos, autServer)
        topic.subscribeAndGetPublisher(qos, serviceAvailability)
        topic2.subscribeAndGetPublisher(qos, tokenRevServer)
        print("Autenticando credenciales...'{}'".format(autServer))


        adapter.activate()


        autprx = IceFlix.AuthenticatorPrx.checkedCast(autServer)
        publisher = topic.getPublisher()
        aut = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        aut.authenticationService(autprx, str(uuid.uuid4()))

        
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        topic.unsubscribe(autServer)
        return 0


sys.exit(Autenticador().main(sys.argv))
