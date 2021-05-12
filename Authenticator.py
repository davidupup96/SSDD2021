#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix
import json
import threading


class Authenticator(IceFlix.Authenticator):
    def prueba(self, current=None):
        print("hola")

    def refreshAuthorization(self, user, passwordHash, current=None):
        #ToDo desde aqui se llama a TokenRevocation una vez pasados 30 segundos
        with open('credenciales.json') as f:
            
            data = json.load(f)

        #recorrer el json
        found=False
        try:
            for persona in data["usuarios"]:
                if(persona["nombre"] == user and persona["pass"] == passwordHash ):
                    encontrado = persona
                    print("Lo encontre! ")
                    print(encontrado)
                    found=True             

                    #hacer el timer
                    #t = threading.Timer(5.0, Authenticator.prueba())
                    #t.start()  
            if not found:
                raise IceFlix.Unauthorized
        except IceFlix.Unauthorized: 
            print("La persona buscada no existe")

        ## a continuacion vamos a escribir en tokens.json el id de este usuario
        jsonFile = open("tokens.json", "r+") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        #jsonFile.close() # Close the JSON file

        nuevoToken = {"id": "Dani",
     "valor": "nikhil@geeksforgeeks.org"
    }

        print(nuevoToken)

        data.update(nuevoToken) 

        print (data)

        # Sets file's current position at offset.
        jsonFile.seek(0)
        # convert back to json.
        json.dump(data, jsonFile, indent = 4)
        jsonFile.close() # Close the JSON file
                
        ## Save our changes to JSON file
        #jsonFile = open("tokens.json", "w+")
        #jsonFile.write(json.dumps(data, indent = 4))
        #jsonFile.close()
        

        return "OK!"


        
    def isAuthorized(self, authentication, current=None):

        with open('tokens.json') as f:
            
            data = json.load(f)

        #recorrer el json
        found=False
        
        for tok in data["tokens"]:
            if(tok["valor"] == authentication):
                encontrado = tok
                print("Lo encontre! ")
                print(encontrado)
                found=True               
        if not found:
            print ("token NO encontrado!")
        

        return found


class Token(IceFlix.TokenRevocation):
    def revoke(self, authentication, current=None):
        
        jsonFile = open("tokens.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        found=False
        try:
            for tok in data["tokens"]:
                if(tok["valor"] == authentication):
                    encontrado = tok
                    found=True
                    print(authentication)
                    ## Working with buffered content
                    encontrado["valor"] = ""                 
                    ## Save our changes to JSON file
                    jsonFile = open("tokens.json", "w+")
                    jsonFile.write(json.dumps(data, indent = 4))
                    jsonFile.close()
            if not found:
                raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId: 
            print("El json no existe")
        
        

######### Clase prueba para los testeos de Unmarshal ######

class Prueba(IceFlix.Prueba):
    

    def getPrueba(self, msg, current=None):
        print("AUTH")
        print("Event received: {0}".format(msg))
        sys.stdout.flush()

##############

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

        broker = self.communicator()
        servant = Authenticator()
        servantTokenRev = Token()
        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        autServer = adapter.addWithUUID(servant)
        tokenRevServer = adapter.addWithUUID(servantTokenRev)

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
        topic2.subscribeAndGetPublisher(qos, tokenRevServer)
        print("Autenticando credenciales...'{}'".format(autServer))
        print("Revocando tokens...'{}'".format(tokenRevServer))

        adapter.activate()
        #me he llevado 2 lineas de cerrar servicio
       

        #parte publicadora
        #topic_mgr = self.get_topic_manager()

        #topic_name2 = "ServiceAvariability2"
        #try:
            #topic = topic_mgr.retrieve(topic_name)
            #topic2 = topic_mgr.retrieve(topic_name2)
        #except IceStorm.NoSuchTopic:
            #print("no such topic found, creating")
            #topic = topic_mgr.create(topic_name)
            #topic2 = topic_mgr.create(topic_name2)


        #nuevo checkedCast

        autprx = IceFlix.AuthenticatorPrx.checkedCast(autServer)
        publisher = topic.getPublisher()
        aut = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        aut.authenticationService(autprx,"idPrueba")

        topic.unsubscribe(autServer)

        #las 2 lineas de cerrar servicio
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


sys.exit(Autenticador().main(sys.argv))
