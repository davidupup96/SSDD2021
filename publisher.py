#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('./EsiFlix.ice')
import IceFlix

class Publisher(Ice.Application):
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print('Invalid proxy')
            return 2

        topic_name = "ServiceAvariability"
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic = topic_mgr.create(topic_name)

        publisher = topic.getPublisher()
        printer = IceFlix.MainPrx.uncheckedCast(publisher)
        printer.getAuthenticator("Hello World ")
        #algo similar a esto-> aut = topic.getPublisher()
        #aut = IceFlix.AuthenticatorPrx.uncheckedCast(publisher)
        #aut.refreshAuthorization("Hola mundo")
        
        return 0
        


sys.exit(Publisher().main(sys.argv))
