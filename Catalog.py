#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix


class MediaCatalog (IceFlix.MediaCatalog):
    def getTile(self, id, current=None):
        print("MEdia catalog {0}".format(id))
        sys.stdout.flush()
        
   
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
