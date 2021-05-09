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
        print("IsAvailabrle: {0}".format(message))
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

        ic = self.communicator()
        servant = StreamProvider()
        adapter = ic.createObjectAdapter("StreamProviderAdapter")
        MServer = adapter.addWithUUID(servant)

        topic_name = "ServiceAvariability" 
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, MServer)
        print("Autenticando credenciales...'{}'".format(MServer))

        adapter.activate()

        #nuevo checkedCast
        streamprx = IceFlix.StreamProviderPrx.checkedCast(MServer)

        publisher = topic.getPublisher()
        print("Soy STREAM PROVIDER :  \n")
        print(streamprx)
        printer = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)

        printer.mediaService(streamprx,"idPrueba")

        topic.unsubscribe(MServer)



        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriber)

        return 0


sys.exit(MediaStream().main(sys.argv))
