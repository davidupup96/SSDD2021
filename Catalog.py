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
from IceFlix import Media



class MediaCatalog (IceFlix.MediaCatalog):
    def __init__(self, comunicador, diccionario):
        self.com = comunicador
        self.dic = diccionario
        # topic_mgr = StreamAnnounces.get_topic_manager()
        # topic_main = "AuthenticationStatus"
        # try:
        # 	topic2 = topic_mgr.retrieve(topic_main)
        # except IceStorm.NoSuchTopic:
        #     print("no such topic found, creating")
        #     topic2 = topic_mgr.create(topic_main)

        # publicador = topic2.getPublisher()
        # mai= IceFlix.MainPrx.checkedCast(pAut)

    def getTile(self, id, current=None):
        with open('catalogo.json') as f:
            # ToDo Controlar cuando el archivo esta vacio.
            # Y TemporaryUnavailable
            data = json.load(f)

        # recorrer el json
        found = False
        encontrado = IceFlix.Media()
        try:
            for media in data["peliculas"]:
                if(media["id"] == id):
                    listaTags = list(media["info"]["tags"])
                    print(media["provider"])
                    providerprx = self.com.stringToProxy(media["provider"])
                    print("GETTILE PROXY\n")
                    print(providerprx)
                    print(type(providerprx))
                    provider = IceFlix.StreamProviderPrx.checkedCast(providerprx)
                    print("VEMOS media[provider]\n")
                    print(media["provider"])
                    print("VEMOS TYPE\n")
                    print(type(provider))
                    print("VEMOS provider")
                    print(provider)
                    encontrado = IceFlix.Media(media["id"], provider, IceFlix.MediaInfo(
                        media["info"]["name"], listaTags))
                    print("Lo encontre! ")
                    print(encontrado)
                    found = True

                    if(media["provider"] is ""):
                        raise IceFlix.TemporaryUnavailable

            if not found:
                raise IceFlix.WrongMediaId

        except IceFlix.WrongMediaId:
            print("El identificador: "+id + " no existe")
            raise IceFlix.WrongMediaId
            # return None

        except IceFlix.TemporaryUnavailable:
            print("El Media no está disponible.")
            raise IceFlix.TemporaryUnavailable

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
                        lista.append(encontrado)
                else:
                    if(name.lower() in media["info"]["name"].lower()):
                        encontrado = media["id"]
                        lista.append(encontrado)
            print(lista)

        return lista

    def getTilesByTags(self, tags, includeAllTags, current=None):
        with open('catalogo.json') as f:

            encontrado = None

            data = json.load(f)

            listaADevolver = list()
            listaAux = list()
            if(includeAllTags == False):
                for media in data["peliculas"]:

                    #coincide = False

                    for tag in tags:
                        if tag in media["info"]["tags"]:
                            encontrado = media["id"]

                            if encontrado not in listaAux:
                                listaAux.append(encontrado)
                                listaADevolver.append(encontrado)

            else:
                for media in data["peliculas"]:
                    if(sorted(tags) == sorted(media["info"]["tags"])):
                        encontrado = media["id"]
                        listaADevolver.append(encontrado)
            print(listaADevolver)

        return listaADevolver

    def renameTile(self, id, name, authentication, current=None):
        # ToDo comprobar Authentication
        jsonFile = open("catalogo.json", "r")  # Open the JSON file for reading
        data = json.load(jsonFile)  # Read the JSON into the buffer
        jsonFile.close()  # Close the JSON file
        posicion = len(self.dic["Authenticator"])
        posicion = posicion - 1
        proxy = self.dic["Authenticator"][posicion]["valor"]
        print("\nVoy a mostrar el proxy de authenticator\n")
        print(proxy)

        print(type(proxy))
        found = False

        try:
            if (proxy.isAuthorized(authentication) == True):
                print("HE ENTRADO EN LA AUTHENTICACION")
                for media in data["peliculas"]:
                    if(media["id"] == id):
                        encontrado = media
                        found = True
                        print("CAmbiado el nombre de: ")
                        print(encontrado["info"]["name"])
                        encontrado["info"]["name"] = name
                        # Save our changes to JSON file
                        jsonFile = open("catalogo.json", "w+")
                        jsonFile.write(json.dumps(data, indent=4))
                        jsonFile.close()
            else:
                raise IceFlix.Unauthorized
            if not found:
                raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId:
            print("El identificador: "+id + " no existe")
            raise IceFlix.WrongMediaId
        except IceFlix.Unauthorized:
            print("El identificador: "+id + " no esta autorizado")
            raise IceFlix.Unauthorized

    def addTags(self, id, tags, authentication, current=None):
        # ToDo comprobar Authentication

        jsonFile = open("catalogo.json", "r")
        data = json.load(jsonFile)
        jsonFile.close()
        posicion = len(self.dic["Authenticator"])
        posicion = posicion - 1
        proxy = self.dic["Authenticator"][posicion]["valor"]
        found = False
        try:
            if (proxy.isAuthorized(authentication) == True):
                for media in data["peliculas"]:
                    if(media["id"] == id):
                        encontrado = media
                        found = True
                        encontrado["info"]["tags"].extend(tags)
                        print("Añadidos los tags: ")
                        print(encontrado["info"]["tags"])

                        jsonFile = open("catalogo.json", "w+")
                        jsonFile.write(json.dumps(data, indent=4))
                        jsonFile.close()
            else:
                raise IceFlix.Unauthorized
            if not found:
                raise IceFlix.WrongMediaId
        except IceFlix.Unauthorized:
            print("El identificador: "+id + " no esta autorizado")
            raise IceFlix.Unauthorized
        except IceFlix.WrongMediaId:
            print("El identificador: "+id + " no existe")
            raise IceFlix.WrongMediaId

    def removeTags(self, id, tags, authentication, current=None):
        # Utilizando el recorrido inverso tambien borramos tags repes :)
        # ToDo comprobar Authentication
        jsonFile = open("catalogo.json", "r")
        data = json.load(jsonFile)
        jsonFile.close()
        posicion = len(self.dic["Authenticator"])
        posicion = posicion - 1
        proxy = self.dic["Authenticator"][posicion]["valor"]
        found = False
        try:
            if (proxy.isAuthorized(authentication) == True):
                for media in data["peliculas"]:
                    if(media["id"] == id):
                        encontrado = media
                        found = True  # Recorremos tags al reves para no interferir
                        i = len(encontrado["info"]["tags"])-1
                        for tagEncontrado in reversed(encontrado["info"]["tags"]):
                            for tagParams in tags:
                                if(tagParams == tagEncontrado):
                                    print("Encuentro tag a borrar: " + tagParams)
                                    del(encontrado["info"]["tags"][i])
                            i -= 1
            else:
                raise IceFlix.Unauthorized
            if not found:
                raise IceFlix.WrongMediaId
        except IceFlix.WrongMediaId:
            print("El identificador: "+id + " no existe")
            raise IceFlix.WrongMediaId
        except IceFlix.Unauthorized:
            print("El identificador: "+id + " no esta autorizado")
            raise IceFlix.Unauthorized
            # Save our changes to JSON file
        jsonFile = open("catalogo.json", "w+")
        jsonFile.write(json.dumps(data, indent=4))
        jsonFile.close()

        ############################################################
        ##   EL NEW MEDIA QUE ESTABA DESDE EL PRINCIPIO AQUI      ##
        ############################################################


class StreamAnnounces(IceFlix.StreamAnnounces):

    def newMedia(self, id, initialName, providerId, current=None):

        # a continuacion vamos a escribir en catalogo.json el nuevo MEdia
        # Open the JSON file for reading
        jsonFile = open("catalogo.json", "r+")
        data = json.load(jsonFile)  # Read the JSON into the buffer

        found = False
        for media in data["peliculas"]:
            if(media["id"] == id):
                jsonFile.close()
                found = True
                encontrado = media
                print("Cambiado el Provider de: ")
                print(encontrado["info"]["name"])
                encontrado["provider"] = providerId
                # Save our changes to JSON file
                jsonFile = open("catalogo.json", "w+")
                jsonFile.write(json.dumps(data, indent=4))
                jsonFile.close()

        if found == False:
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
            json.dump(data, jsonFile, ensure_ascii=False, indent=4)
            jsonFile.close()  # Close the JSON file


class ServiceAvailability (IceFlix.ServiceAvailability):
    def __init__(self, dic):
        self.dic = dic

    def catalogService(self, message, id, current=None):
        print("Catalogo recibido {0}".format(message))
        print("Estoy en catalog y es diccionario de catalogo")
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["Catalogo"].append(nuevoProxy)
        print(self.dic)

    def authenticationService(self, message, id, current=None):

        print("autenticador recibido {0}".format(message))
        print("Estoy en catalog y es diccionario de autenticator")
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["Authenticator"].append(nuevoProxy)
        print(self.dic)

    def mediaService(self, message, id, current=None):

        print("Media Stream recibido: {0}".format(message))
        print("Estoy en catalog y es diccionario de media")
        sys.stdout.flush()
        nuevoProxy = {}
        nuevoProxy['id'] = id
        nuevoProxy['valor'] = message
        self.dic["MediaStream"].append(nuevoProxy)
        print(self.dic)


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
        diccionarioAvailability = {"Service_availability": [], "Authenticator": [],
                                   "MediaStream": [], "Catalogo": [], "StreamerSync": []}
        broker = self.communicator()
        servant = MediaCatalog(broker, diccionarioAvailability)
        servantAvailability = ServiceAvailability(diccionarioAvailability)
        servant_newMedia = StreamAnnounces()
        adapter = broker.createObjectAdapter("MediaCatalogAdapter")
        catalogServer = adapter.addWithUUID(servant)
        catalogServerMedia = adapter.addWithUUID(servant_newMedia)
        serviceAvailability = adapter.addWithUUID(servantAvailability)

        topic_name = "ServiceAvailability"
        topic_name_media = "MediaAnnouncements"
        qos = {}
        qos_media = {}

        try:
            topic = topic_mgr.retrieve(topic_name)
            topic_media = topic_mgr.retrieve(topic_name_media)
        except IceStorm.NoSuchTopic:
            #topic = topic_mgr.create(topic_name)
            topic_media = topic_mgr.create(topic_name_media)

        topic.subscribeAndGetPublisher(qos, catalogServer)
        topic_media.subscribeAndGetPublisher(qos_media, catalogServerMedia)
        topic.subscribeAndGetPublisher(qos, serviceAvailability)
        print("Catalogo suscrito..'{}'".format(catalogServer))
        print("Catalogo suscrito a MEdiaAnounce..'{}'".format(catalogServerMedia))

        adapter.activate()

        # nuevo checkedCast
        catalogprx = IceFlix.MediaCatalogPrx.checkedCast(catalogServer)

        publisher = topic.getPublisher()

        catalogo = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        catalogo.catalogService(catalogprx, str(uuid.uuid4()))

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(catalogServer)
        topic.unsubscribe(catalogServerMedia)

        return 0


sys.exit(Catalogo().main(sys.argv))
