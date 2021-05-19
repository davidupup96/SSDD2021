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

        topic_name = "ServiceAvailability"

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic = topic_mgr.create(topic_name)

        publisher = topic.getPublisher()


        topic_tokens = "AuthenticationStatus"
        try:
            topic2 = topic_mgr.retrieve(topic_tokens)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic2 = topic_mgr.create(topic_tokens)

        publicador = topic2.getPublisher()


        ############################################################
        ## AQUI PROBANDO LA INVOCACION DIRECTA EN LUGAR DEL TOPIC ##
        ############################################################


        ######################
        #### Llamadas a Main ####

        f = open("proxys/main", "r")
        l=f.readline()       
        f.close()
        pAut = self.communicator().stringToProxy(l)
        mai= IceFlix.MainPrx.checkedCast(pAut)
    ############ Comprobacion estandar:
        obtenAut = mai.getAuthenticator()   
 
        if obtenAut is not None:
            obtenAut.refreshAuthorization("Cristian","p1") 
            print("He leido un PROXY AUTHENTICATOR: \n")
            print(obtenAut)
        
        obtenCat = mai.getCatalogService()
        if obtenCat is not None:
            print("He leido un PROXY CATALOGO: \n")
            print(obtenCat)


        ######################
        #### SERVICE AVAILABILITY ####

        f = open("proxys/serviceAvailability", "r")
        l=f.readline()       
        f.close()
        pServiceA = self.communicator().stringToProxy(l)
        serviceA= IceFlix.ServiceAvailabilityPrx.checkedCast(pServiceA)
    ############ Comprobacion estandar:
        #serviceA.catalogService("Hola catalogo")
        #serviceA.authenticationService("Hola autenticator ","id2")
        #serviceA.mediaService("Hola media")

       # Main.dictionario_proxy[availabity[valor]]


        ######################
        #### LLAMADAS A AUTHENTICATOR ####
    ############ Comprobacion estandar:
        prueba = obtenAut.refreshAuthorization("Dani","p2")
        print (prueba)
        #isAut = obtenAut.isAuthorized("ttttttt")
        #print (isAut)


        ######################Id20
        #### lLAMADAS A CATALOG ####

    ############ Comprobacion estandar:
        #print(obtenCat.getTile("6c83367e60c00168367a874238dfe1e1d75bb1848088b8fbfb14fa3c"))
        #print(obtenCat.getTilesByName("NombreEjemplo", True))        #Probar el True
        listaCat = obtenCat.getTilesByTags(["tag50","tag60"], False)
        print(listaCat)    #El True creo que no va
        #obtenCat.renameTile("2d81d2227a3141191569993563a6c6e1e524f0800fefbe62227bf25f", "nuevoNomb", "gshsds")
        #obtenCat.addTags("2d81d2227a3141191569993563a6c6e1e524f0800fefbe62227bf25f", ["DaniTag1","DaniTag2"], "gshsds")
        #obtenCat.removeTags("2d81d2227a3141191569993563a6c6e1e524f0800fefbe62227bf25f", ["tag4","tag6"], "aut")

    ############ Comprobacion de errores:
        #obtenCat.getTile("Id10dd")
        #obtenCat.getTilesByName("name2dd", False)          
        #obtenCat.getTilesByTags(["tag0" , "tag4"], True)    
        #obtenCat.renameTile("Id2022", "nuevoNombre100", "aut")
        #obtenCat.addTags("Id22220", ["nuevaTag1","nuevaTag2"], "aut")
        #obtenCat.removeTags("Idfff20", ["nuevaTag1","nuevaTag2"], "aut")


    ######################
        #### lLAMADAS A Media Stream####

        #f = open("proxys/streamProvider", "r")
        #l=f.readline()       
        #f.close()
        #pStreamProvider = self.communicator().stringToProxy(l)
        #streamProvider= IceFlix.StreamProviderPrx.checkedCast(pStreamProvider)Id20
    ############ Comprobacion estandar:
        #streamProvider.reannounceMedia()


          
        return 0
        

sys.exit(Publisher().main(sys.argv))
