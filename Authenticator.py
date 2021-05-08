#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix


class Authenticator(IceFlix.Authenticator):
    def refreshAuthorization(self, message, current=None):
        print("Buenos dias: {0}".format(message))
        sys.stdout.flush()
        
    def isAuthorized(self, message, current=None):
        print("Buenas noches: {0}".format(message))
        sys.stdout.flush()

class Prueba(IceFlix.Prueba):
    

    def getPrueba(self, msg, current=None):
        print("AUTH")
        print("Event received: {0}".format(msg))
        sys.stdout.flush()



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
        servant = Authenticator()
        adapter = ic.createObjectAdapter("AuthenticatorAdapter")
        MServer = adapter.addWithUUID(servant)

        topic_name = "ServiceAvariability" #cambiar a ServiceAvariability
        qos = {}
        
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, MServer)
        print("Autenticando credenciales...'{}'".format(MServer))

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriber)

        return 0


sys.exit(Autenticador().main(sys.argv))
