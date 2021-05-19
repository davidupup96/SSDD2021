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
            print("He leido un proxy cojonudo de un Diccionario aun mejor qu el archivo: \n")
            print(obtenAut)
        
        obtenCat = mai.getCatalogService()
        if obtenCat is not None:
            print("He leido un proxy cojonudo de un archivo Diccionario: \n")
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
        #prueba = obtenAut.refreshAuthorization("Cristian","p1")
        #print (prueba)
        #isAut = obtenAut.isAuthorized("ElT1")
        #print (isAut)


        ######################
        #### lLAMADAS A CATALOG ####

    ############ Comprobacion estandar:
        print(obtenCat.getTile("Id10"))
        print(obtenCat.getTilesByName("name2", False))        #Probar el True
        listaCat = obtenCat.getTilesByTags(["tag4"], False)
        print(listaCat)    #El True creo que no va
        #obtenCat.renameTile("Id20", "nuevoNombre100", "aut")
        #obtenCat.addTags("Id20", ["nuevaTag1","nuevaTag2"], "aut")
        #obtenCat.removeTags("Id20", ["nuevaTag1","nuevaTag2"], "aut")

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
        #streamProvider= IceFlix.StreamProviderPrx.checkedCast(pStreamProvider)
    ############ Comprobacion estandar:
        #streamProvider.reannounceMedia()


          
        return 0
        

sys.exit(Publisher().main(sys.argv))
