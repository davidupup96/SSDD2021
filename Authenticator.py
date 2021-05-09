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
        #me he llevado 2 lineas de cerrar servicio

        #topic.unsubscribe(MServer)

        #parte publicadora
        #topic_mgr = self.get_topic_manager()
        #if not topic_mgr:
            #print('Invalid proxy')
            #return 2

        # = "ServiceAvariability"
        #topic_name2 = "ServiceAvariability2"
        #try:
            #topic = topic_mgr.retrieve(topic_name)
            #topic2 = topic_mgr.retrieve(topic_name2)
        #except IceStorm.NoSuchTopic:
            #print("no such topic found, creating")
            #topic = topic_mgr.create(topic_name)
            #topic2 = topic_mgr.create(topic_name2)
              
        #nuevo checkedCast
        autprx = IceFlix.AuthenticatorPrx.checkedCast(MServer)

        publisher = topic.getPublisher()
        printer = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)

        printer.authenticationService(autprx,"idPrueba")

        topic.unsubscribe(MServer)

        #las 2 lineas de cerrar servicio
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        return 0


sys.exit(Autenticador().main(sys.argv))
