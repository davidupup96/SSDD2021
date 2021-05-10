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
        #topic_name2 = "ServiceAvariability2"
        try:
            topic = topic_mgr.retrieve(topic_name)
            #topic2 = topic_mgr.retrieve(topic_name2)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic = topic_mgr.create(topic_name)
            #topic2 = topic_mgr.create(topic_name2)

        publisher = topic.getPublisher()


        ############################################################
        ## AQUI PROBANDO LA INVOCACION DIRECTA EN LUGAR DEL TOPIC ##
        ############################################################


        #### Llamadas a Main ####

        f = open("proxys/main", "r")
        l=f.readline()       
        f.close()
        pAut = self.communicator().stringToProxy(l)
        mai= IceFlix.MainPrx.checkedCast(pAut)
    ############
        obtenAut = mai.getAuthenticator()
        print("He leido un proxy cojonudo de un archivo: \n")
        print(obtenAut)
        #mai.getCatalogService()


        #### SERVICE AVAILABILITY ####

        f = open("proxys/serviceAvailability", "r")
        l=f.readline()       
        f.close()
        pServiceA = self.communicator().stringToProxy(l)
        serviceA= IceFlix.ServiceAvailabilityPrx.checkedCast(pServiceA)
    ############
        #serviceA.catalogService("Hola catalogo")
        #serviceA.authenticationService("Hola autenticator ")
        #serviceA.mediaService("Hola media")


        #### lLAMADAS A CATALOG ####

        f = open("proxys/catalogo", "r")
        l=f.readline()       
        f.close()
        pCatalogo = self.communicator().stringToProxy(l)
        catalogo= IceFlix.MediaCatalogPrx.checkedCast(pCatalogo)
    ############ Comprobacion estandar:
        print(catalogo.getTile("Id10"))
        print(catalogo.getTilesByName("name2", False))        #Probar el True
        catalogo.getTilesByTags(["tag0" , "tag4"], False)     #El True creo que no va
        catalogo.renameTile("Id20", "nuevoNombre100", "aut")
        catalogo.addTags("Id20", ["nuevaTag1","nuevaTag2"], "aut")
        catalogo.removeTags("Id20", ["nuevaTag1","nuevaTag2"], "aut")

    ############ Comprobacion de errores:
        #catalogo.getTile("Id10dd")
        #catalogo.getTilesByName("name2dd", False)          
        #catalogo.getTilesByTags(["tag0" , "tag4"], True)    
        #catalogo.renameTile("Id2022", "nuevoNombre100", "aut")
        #catalogo.addTags("Id22220", ["nuevaTag1","nuevaTag2"], "aut")
        #atalogo.removeTags("Idfff20", ["nuevaTag1","nuevaTag2"], "aut")




                    #########################
                    ## LLAMADAS Y TESTEOS  ##
                    #########################

    #####################
        ## Llamadas a ServiceAvailability

        #available = IceFlix.ServiceAvailabilityPrx.uncheckedCast(publisher)
        #available.catalogService("Hola catalogo")
        #available.authenticationService("Hola autenticator ")
        #available.mediaService("Hola media")


    ######################
        ## Llamadas a Main 

        #mai= IceFlix.MainPrx.uncheckedCast(publisher)
        #obtenAut = mai.getAuthenticator()
        #print(obtenAut)
        #mai.getCatalogService()


    #######################
        ## Llamadas a Prueba
         
        #prueba = IceFlix.PruebaPrx.checkedCast(publisher)
        #try:
        #v = prueba.getPrueba()
        #except Ice.UnmarshalOutOfBoundsException:
            #print ("tratando error de unmarshal")
        #prueba.pruebaVacio()
     
        
    ######################
        ## Llamadas a Catalog Media       
 
        #med = IceFlix.MediaCatalogPrx.uncheckedCast(publisher)
        #dameCatalogo = med.getTile("idd")
        #print (dameCatalogo)

        #med.getTilesByName("name2", False)
            

        #damePorTags = med.getTilesByTags(["tag0" , "tag4"], True)    
        #print (damePorTags)

        #med.renameTile("Id2022", "nuevoNombre100", "aut")

        #anadeTags = med.addTags("Id22220", ["nuevaTag1","nuevaTag2"], "aut")

        #borraTags = med.removeTags("Idfff20", ["nuevaTag1","nuevaTag2"], "aut")
          
        return 0
        

sys.exit(Publisher().main(sys.argv))
