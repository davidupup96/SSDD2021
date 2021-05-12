#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix
import json


class MediaCatalog (IceFlix.MediaCatalog):
    def getTile(self, id, current=None):
        with open('catalogo.json') as f:
            data = json.load(f)
            #print(data)
            
        #recorrer el json
        
        for media in data["peliculas"]:
            if(media["id"] == id):
                encontrado = media
            #print (value)
            
            #for hijo in value:
             #   print (hijo)
              #  print (hijo["name"])
               # print (hijo["tags"])

    def getTilesByName(self, name, exact, current=None):
        with open('catalogo.json') as f:
            data = json.load(f)

            lista = list()
            for media in data["peliculas"]:
                if(exact):
                    if(media["info"]["name"].lower() == name.lower()):
                        encontrado = media["id"]
                        #print (encontrado)
                        lista.append(encontrado)
                else:
                    if(name.lower() in media["info"]["name"].lower()):
                        encontrado = media["id"]
                        #print (encontrado)
                        lista.append(encontrado)
            
            print(lista)

    def getTilesByTags(self, tags, includeAllTags, current=None):
        with open('catalogo.json') as f:
            data = json.load(f)

            listaADevolver = list()

            if(includeAllTags == False):

                for media in data["peliculas"]:

                    for tag in tags:
                        
                        if(tag) in media["info"]["tags"]:
                            encontrado = media["id"]
                            #print (encontrado)
                            listaADevolver.append(encontrado)

            else:

                for media in data["peliculas"]:

                    if(sorted(tags) == sorted(media["info"]["tags"])):
                        encontrado = media["id"]
                        listaADevolver.append(encontrado)
                    

            print(listaADevolver)


    def renameTile(self, id, name, authentication, current=None):

        #ToDo comprobar Authentication

        jsonFile = open("catalogo.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        for media in data["peliculas"]:
            if(media["id"] == id):
                encontrado = media

                ## Working with buffered content
                encontrado["info"]["name"] = name
                
                ## Save our changes to JSON file
                jsonFile = open("catalogo.json", "w+")
                jsonFile.write(json.dumps(data, indent = 4))
                jsonFile.close()

    def addTags(self, id, tags, authentication, current=None):

        #ToDo comprobar Authentication
                        
        jsonFile = open("catalogo.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        for media in data["peliculas"]:
            if(media["id"] == id):
                encontrado = media

                ## Working with buffered content
                encontrado["info"]["tags"].extend(tags)
                
                ## Save our changes to JSON file
                jsonFile = open("catalogo.json", "w+")
                jsonFile.write(json.dumps(data, indent = 4))
                jsonFile.close()

    def removeTags(self, id, tags, authentication, current=None):

        #ToDo comprobar Authentication
        jsonFile = open("catalogo.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        for media in data["peliculas"]:
            if(media["id"] == id):
                encontrado = media

                ## Working with buffered content
                i = 0
                for tagEncontrado in encontrado["info"]["tags"]:
                    
                    for tagParams in tags:  

                        if(tagParams == tagEncontrado):
                            del(encontrado["info"]["tags"][i])
                            
                    i+=1
                
                ## Save our changes to JSON file
                jsonFile = open("catalogo.json", "w+")
                jsonFile.write(json.dumps(data, indent = 4))
                jsonFile.close()



       
   
#throws WrongMediaId, TemporaryUnavailable;

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

        ic = self.communicator()
        servant = MediaCatalog ()
        adapter = ic.createObjectAdapter("MediaCatalogAdapter")
        MServer = adapter.addWithUUID(servant)

        topic_name = "ServiceAvariability" #cambiar a ServiceAvariability
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, MServer)
        print("Clase server media..'{}'".format(MServer))

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriber)

        return 0


sys.exit(Autenticador().main(sys.argv))