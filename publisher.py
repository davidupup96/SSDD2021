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
        #topic_name2 = "ServiceAvariability2"
        try:
            topic = topic_mgr.retrieve(topic_name)
            #topic2 = topic_mgr.retrieve(topic_name2)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic = topic_mgr.create(topic_name)
            #topic2 = topic_mgr.create(topic_name2)

        publisher = topic.getPublisher()

        #prueba = IceFlix.PruebaPrx.uncheckedCast(publisher)
        #try:
        #v = prueba.getPrueba()
        #except Ice.UnmarshalOutOfBoundsException:
            #print ("tratando error de unmarshal")
     
        #printer = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        #printer.authenticationService()
        
        #printer = IceFlix.MainPrx.uncheckedCast(publisher)
        #aut = IceFlix.MainPrx.uncheckedCast(publisher)
        #obtenAut = aut.getAuthenticator("toma")
        #print(obtenAut)
        
        #printer.getCatalogService()

        med = IceFlix.MediaCatalogPrx.uncheckedCast(publisher)
        #dameCatalogo = med.getTile("idd")
       # print (dameCatalogo)

        #damePorNombre = med.getTilesByName("name2", False)
        #print (damePorNombre)    

        #damePorTags = med.getTilesByTags(["tag0" , "tag4"], True)    
        #print (damePorTags)

        #renombra = med.renameTile("iii20", "nuevoNombre2", "aut")

        #anadeTags = med.addTags("Id22220", ["nuevaTag1","nuevaTag2"], "aut")

        borraTags = med.removeTags("Idfff20", ["nuevaTag1","nuevaTag2"], "aut")

        #algo similar a esto-> aut = topic.getPublisher()
        #aut = IceFlix.MainPrx.uncheckedCast(publisher)
        #aut.catalogService("Hola mundo")
        

        #printer.catalogService("Hola catalogo")
       # printer.authenticationService("Hola autenticator ")
       # printer.mediaService("Hola media")


        return 0
        


sys.exit(Publisher().main(sys.argv))
