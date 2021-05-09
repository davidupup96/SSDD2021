#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix

import time

class Main(IceFlix.Main):
    def getAuthenticator(self, current=None):
        try:
            # f = open("listaAut", "r")
            # l=f.readline()
            # print(f.read())
            # f.close()
            #l=str("792F8331-6F9F-459F-8A4D-B562CC8B26D8 -t -e 1.1:tcp -h 10.0.2.13 -p 37845 -t 60000")
            r=l.rstrip(l[-1])
        except TemporaryUnavailable:
            raise
        return r

        
    def getCatalogService(self, current=None):
        print("Event received: {0}".format(message))
        sys.stdout.flush()
        catalog=5
        return catalog

class Prueba(IceFlix.Prueba):
 
    def getPrueba(self, current=None):
        print("MAIN")
        print("Event received: ".format())
        sys.stdout.flush()

        f = open("listaAut", "r")
        l=f.readline()
        print(l)
        f.close()

        return str(l)

class ServiceAvailability (IceFlix.ServiceAvailability ):
    def catalogService(self, message, id,current=None):
        print("Event received: {0}".format(message))
        sys.stdout.flush()

    def authenticationService(self, message,id, current=None):
        print("Event received: {0}".format(message))
        sys.stdout.flush()

    def mediaService(self, message, id,current=None):
        print("Event received: {0}".format(message))
        sys.stdout.flush()
      


class Subscriber(Ice.Application):
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
        servant = ServiceAvailability ()
        servantPrueba = Prueba()
        adapter = ic.createObjectAdapter("MainAdapter")
        MServer = adapter.addWithUUID(servant)
        MServerPrueba = adapter.addWithUUID(servantPrueba)


        topic_name = "ServiceAvariability" #cambiar a ServiceAvariability
        qos = {}
        listaAut={"792F8331-6F9F-459F-8A4D-B562CC8B26D8 -t -e 1.1:tcp -h 10.0.2.13 -p 37845 -t 60000"}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, MServer)
        topic.subscribeAndGetPublisher(qos, MServerPrueba)
        print("Waiting events... '{}'".format(MServer))
        #f = open("listaAut", "r")
        #l=f.read()
        #print(l)

       

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(MServer)
        topic.unsubscribe(MServerPrueba)

        return 0


sys.exit(Subscriber().main(sys.argv))
