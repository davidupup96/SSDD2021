#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix


class StreamProvider(IceFlix.StreamProvider):

    def getStream(self, id, authentication, current=None):
        print("Get Stream: {0}".format(message))
        sys.stdout.flush()
        
    def isAvailable(self, id, current=None):
        print("IsAvailable: {0}".format(message))
        sys.stdout.flush()

    def reannounceMedia(self, current=None):
        print("reanounce")


class StreamController(IceFlix.StreamController):
    def getSDP(self, authentication, port, current=None):
        print("getSPD")

    def getSyncTopic(self,current=None):
        print("getSyncTopic")

    def refreshAuthentication(self,authentication, current=None):
        print("reflesh autentication")

    def stop(self, current=None):
        print("stop")



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

        broker = self.communicator()
        servant = StreamProvider()
        adapter = broker.createObjectAdapter("StreamProviderAdapter")
        mediaServer = adapter.addWithUUID(servant)

        topic_name = "ServiceAvailability" 
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, mediaServer)
        print("Autenticando credenciales...'{}'".format(mediaServer))

        adapter.activate()

        #nuevo checkedCast
        streamprx = IceFlix.StreamProviderPrx.checkedCast(mediaServer)

        publisher = topic.getPublisher()
        print("Soy STREAM PROVIDER :  \n")
        print(streamprx)
        media = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)

        media.mediaService(streamprx,"idPrueba")
       

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(mediaServer)

        return 0


sys.exit(MediaStream().main(sys.argv))
