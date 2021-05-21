#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix

import os
import hashlib
import uuid


class StreamProvider(IceFlix.StreamProvider):
    def __init__ (self, comunicador, diccionarioAvailability):
        self.com = comunicador
        self.dic = diccionarioAvailability

    def getStream(self, id, authentication, current):
        servant = StreamController()
        mediaServer = current.adapter.addWithUUID(servant)
        streamprx = IceFlix.StreamControllerPrx.checkedCast(mediaServer)

        print("dentro del getStream:")
        print(streamprx)

        return streamprx
        
        
    def isAvailable(self, id, current=None):
        print("IsAvailable: {0}".format(id))
        sys.stdout.flush()

    def reannounceMedia(self, current=None):
        #Hay que guardar una lista como dijo Tobias de tuplas
        #id y streamController para determinar aqui facil quien ya 
        #existe y quien es nuevo o ha desaparecido para reenviar a
        #catalogo con newMedia.

        #Codigo premilinar por si hacemos uso de el:
        topic_name_newMedia = "MediaAnnouncements"

        try:
            topic_newMedia = MediaStream.topic_mgr.retrieve(topic_name_newMedia)

        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic_newMedia = MediaStream.topic_mgr.create(topic_name_newMedia)
        publisher_newMedia = topic_newMedia.getPublisher()

        nuevoMEdia = IceFlix.StreamAnnouncesPrx.uncheckedCast(publisher_newMedia)
        print("reanounce")

        basepath = 'media/'
        for entry in os.listdir(basepath):
            print(entry)


class StreamerSync(IceFlix.StreamerSync):

    def requestAuthentication(self, id, authentication, current=None):
        print("RequestAutentication en STREAMERSYNC")


class StreamController(IceFlix.StreamController):
    def getSDP(self, authentication, port, current=None):
        print("getSPD")

    def getSyncTopic(self,current=None):
        print("getSyncTopic")

    def refreshAuthentication(self,authentication, current=None):
        print("reflesh autentication")

    def stop(self, current=None):
        print("stop")



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



class MediaStream(Ice.Application):
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
        diccionarioAvailability = {"Service_availability": [],"Authenticator":[],
        "MediaStream":[],"Catalogo":[],"StreamerSync":[]}
        broker = self.communicator()
        servant = StreamProvider(broker, diccionarioAvailability)
        servantAvailability = ServiceAvailability(diccionarioAvailability)
        adapter = broker.createObjectAdapter("StreamProviderAdapter")
        mediaServer = adapter.addWithUUID(servant)
        serviceAvailability = adapter.addWithUUID(servantAvailability)

        topic_name = "ServiceAvailability" 
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, serviceAvailability)
        topic.subscribeAndGetPublisher(qos, mediaServer)
        print("Creando Media Stream...'{}'".format(mediaServer))

        adapter.activate()

        #nuevo checkedCast
        streamprx = IceFlix.StreamProviderPrx.checkedCast(mediaServer)

        publisher = topic.getPublisher()
        print("Soy STREAM PROVIDER :  \n")
        print(streamprx)
        media = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        streamid = str(uuid.uuid4())
        media.mediaService(streamprx,streamid)


        ############################################################
        ##   LA LLAMADA A NEW MEDIA PARA LLENAR EL CATALOGO       ##
        ############################################################


        topic_name_newMedia = "MediaAnnouncements"

        try:
            topic_newMedia = topic_mgr.retrieve(topic_name_newMedia)

        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic_newMedia = topic_mgr.create(topic_name_newMedia)
        publisher_newMedia = topic_newMedia.getPublisher()

        nuevoMEdia = IceFlix.StreamAnnouncesPrx.uncheckedCast(publisher_newMedia)

       
        # Iniciamos leyendo el directorio de medias
        basepath = 'media/'
        for entry in os.listdir(basepath):
            # Ahora calculamos el SHA256 de cada fichero leido
            id=hashlib.sha224(entry.encode()).hexdigest()
                    
            # Ahora creamos StreamProvider para añadirlo a newMedia()
            providerPrueba = streamprx.getStream(id, "token")
            #Por ultimo se harian las llamadas a newMedia para meterlas
            #en el catalogo 
            nuevoMEdia.newMedia( id, "initialName", str(streamprx) )
        print("\n Ya añadi los media al catalogo.")

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(mediaServer)

        return 0


sys.exit(MediaStream().main(sys.argv))
