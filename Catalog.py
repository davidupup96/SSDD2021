#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix
import json
from IceFlix import Media

#class Media (object):
    # def __init__(self, id, provider, info):
    #     self.id = id
    #     self.provider = provider
    #     self.info = info


class MediaCatalog (IceFlix.MediaCatalog):
    def __init__ (self, comunicador):
        self.com = comunicador

    def getTile(self, id, current=None):
        with open('catalogo.json') as f:
            # ToDo Controlar cuando el archivo esta vacio.
            # Y TemporaryUnavailable
            data = json.load(f)
           
        #recorrer el json
        found=False
        encontrado = IceFlix.Media()

        # servant_newMedia=StreamAnnounces()
        # adapter = self.com.createObjectAdapter("StreamProviderAdapter")
        # catalogServer = adapter.addWithUUID(servant_newMedia)

        # catalogprx = IceFlix.MediaCatalogPrx.uncheckedCast(catalogServer)

        try:
            for media in data["peliculas"]:
                if(media["id"] == id):
                    listaTags = list(media["info"]["tags"])
                    provider = IceFlix.StreamProviderPrx.checkedCast(self.com.stringToProxy(media["provider"]))
                    print("VEMOS media[provider]")
                    print(media["provider"])
                    print("VEMOS TYPE")
                    print(type(provider))
                    print("VEMOS provider")
                    print(provider)
                    encontrado = IceFlix.Media(media["id"], provider, IceFlix.MediaInfo(media["info"]["name"],listaTags))
                    #probando Media
                    #encontrado = Media(media["id"],media["provider"],media["info"])
                    print("Lo encontre! ")
                    print(encontrado)
                    found=True            
                       
            if not found:
                raise IceFlix.WrongMediaId
    
        except IceFlix.WrongMediaId: 
            print("El identificador: "+id+ " no existe")

        print(encontrado)
        print(type(encontrado))
        return encontrado
            

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
        
        return lista


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

        return listaADevolver


    def renameTile(self, id, name, authentication, current=None):
        #ToDo comprobar Authentication
        jsonFile = open("catalogo.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        found=False
        try:
            for media in data["peliculas"]:
                if(media["id"] == id):
                    encontrado = media
                    found=True
                    print("CAmbiado el nombre de: ")
                    print(encontrado["info"]["name"])
                    ## Working with buffered content
                    encontrado["info"]["name"] = name                 
                    ## Save our changes to JSON file
                    jsonFile = open("catalogo.json", "w+")
                    jsonFile.write(json.dumps(data, indent = 4))
                    jsonFile.close()
            if not found:
                raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId: 
            print("El identificador: "+id+ " no existe")


    def addTags(self, id, tags, authentication, current=None):

        #ToDo comprobar Authentication
                        
        jsonFile = open("catalogo.json", "r") 
        data = json.load(jsonFile) 
        jsonFile.close()

        found=False
        try:
            for media in data["peliculas"]:
                if(media["id"] == id):
                    encontrado = media
                    found=True
                    encontrado["info"]["tags"].extend(tags)
                    print("Añadidos los tags: ")
                    print(encontrado["info"]["tags"])

                    jsonFile = open("catalogo.json", "w+")
                    jsonFile.write(json.dumps(data, indent = 4))
                    jsonFile.close()
            if not found:
                    raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId: 
            print("El identificador: "+id+ " no existe")


    def removeTags(self, id, tags, authentication, current=None):
        #Utilizando el recorrido inverso tambien borramos tags repes :)
        #ToDo comprobar Authentication
        jsonFile = open("catalogo.json", "r") 
        data = json.load(jsonFile) 
        jsonFile.close() 

        found=False
        try:
            for media in data["peliculas"]:
                if(media["id"] == id):
                    encontrado = media
                    found=True  #Recorremos tags al reves para no interferir
                    i = len(encontrado["info"]["tags"])-1
                    for tagEncontrado in reversed(encontrado["info"]["tags"]):                        
                        for tagParams in tags:  
                            if(tagParams == tagEncontrado):
                                print("Encuentro tag a borrar: "+ tagParams)
                                del(encontrado["info"]["tags"][i])
                        i-=1
            if not found:
                    raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId: 
            print("El identificador: "+id+ " no existe")
                
                ## Save our changes to JSON file
        jsonFile = open("catalogo.json", "w+")
        jsonFile.write(json.dumps(data, indent = 4))
        jsonFile.close()


        ############################################################
        ##   EL NEW MEDIA QUE ESTABA DESDE EL PRINCIPIO AQUI      ##
        ############################################################

class StreamAnnounces(IceFlix.StreamAnnounces):
    
    def newMedia(self, id, initialName, providerId, current=None):

        ## a continuacion vamos a escribir en catalogo.json el nuevo MEdia
        jsonFile = open("catalogo.json", "r+") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer

        found=False     
        for media in data["peliculas"]:
            if(media["id"] == id): 
                jsonFile.close()              
                found=True
                encontrado = media
                print("Cambiado el Provider de: ")
                print(encontrado["info"]["name"])
                ## Working with buffered content
                encontrado["provider"]= providerId                 
                ## Save our changes to JSON file
                jsonFile = open("catalogo.json", "w+")
                jsonFile.write(json.dumps(data, indent = 4))
                jsonFile.close()
 

        if found==False:
            nuevoMedia = {
                "id": id,
                "provider": providerId,
                "info": {
                    "name": initialName,
                    "tags": []
                }
            }
            print(nuevoMedia)
            data["peliculas"].append(nuevoMedia) 
            # Sets file's current position at offset.
            jsonFile.seek(0)
            json.dump(data, jsonFile, ensure_ascii=False, indent = 4)
            jsonFile.close() # Close the JSON file

            


       
class Catalogo(Ice.Application):
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
        servant = MediaCatalog (broker)
        servant_newMedia=StreamAnnounces()
        adapter = broker.createObjectAdapter("MediaCatalogAdapter")
        catalogServer = adapter.addWithUUID(servant)
        catalogServerMedia = adapter.addWithUUID(servant_newMedia)

        topic_name = "ServiceAvailability" 
        topic_name_media="MediaAnnouncements"
        qos = {}
        qos_media={}

        try:
            topic = topic_mgr.retrieve(topic_name)
            topic_media=topic_mgr.retrieve(topic_name_media)
        except IceStorm.NoSuchTopic:
            #topic = topic_mgr.create(topic_name)
            topic_media=topic_mgr.create(topic_name_media)
       
        topic.subscribeAndGetPublisher(qos, catalogServer)
        topic_media.subscribeAndGetPublisher(qos_media, catalogServerMedia)

        print("Catalogo suscrito..'{}'".format(catalogServer))
        print("Catalogo suscrito a MEdiaAnounce..'{}'".format(catalogServerMedia))

        adapter.activate()

        #nuevo checkedCast
        catalogprx = IceFlix.MediaCatalogPrx.checkedCast(catalogServer)

        publisher = topic.getPublisher()

        catalogo = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        catalogo.catalogService(catalogprx,"idPrueba")

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(catalogServer)
        topic.unsubscribe(catalogServerMedia)

        return 0


sys.exit(Catalogo().main(sys.argv))
