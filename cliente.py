#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('EsiFlix.ice')
import IceFlix
import hashlib
import threading

from getpass import getpass






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

        broker = self.communicator()

        ############################################################
        ##              VARIABLES                                 ##
        ############################################################

        go = True
        busquedaExacta=False

        main=None
        catalog=None
        autenticator=None
        seleccionado=None
        token=None

        user=None
        password=None

        listaIds=list()
        listaSeleccion=list()

        i=0



        ############################################################
        ##                BUCLE MENU                              ##
        ############################################################

        print("\nBienvenido a EsiFlix")
        print("Introduzca una de las opciones o escriba \"help\" para ayuda.\n")
        while(go == True):

            choice = input()


            if choice == "help":
                print("Lista de opciones validas:\n help       conectar       buscar_tag\n"+ 
                " buscar     seleccionar     exit \n"+
                " nuevo_tag  borrar_tag      cambiar_nombre\n"+
                " login      refresh")


            elif choice == "conectar":
                mainProxy= input("Ahora introduzca el proxy del MainServer:\n")
                try:
                    pMain = self.communicator().stringToProxy(mainProxy)
                    main= IceFlix.MainPrx.checkedCast(pMain)
                    print("Conectado con exito a MainServer!")
                except:
                    print("El proxy de MainServer no es correcto o no esta encendido")
                
            

            elif choice == "buscar_tag":
                if main !=None:

                    tags = [item for item in input("Introduzca los tags deseados : ").split()]
                    choiceExacto=input("Desea una busqueda exacta? Introduzca \"si\" o \"no\": ")
                    if choiceExacto=="si":
                        busquedaExacta=True
                    elif choiceExacto=="no":
                        busquedaExacta=False
                    else:
                        print("Opcion incorrecta, solo se acepta: \"si\" o \"no\"")

                    try:
                        catalog=main.getCatalogService()
                        listaIds=catalog.getTilesByTags(tags,busquedaExacta)
                        listaSeleccion=list()
                        i=0
                        print("\nElementos encontrados: \n")
                        for element in listaIds:
                            media=catalog.getTile(element)
                            listaSeleccion.append(media)
                            i+=1
                            print(" "+str(i)+"- ", end=' ')
                            print(media.info.name)

                        if len(listaIds) == 0:
                            print("No se encontraron coincidencias en tu busqueda")
                    
                    except IceFlix.WrongMediaId: 
                        print("El identificador: "+element+ " no existe")
                        

                    except IceFlix.TemporaryUnavailable:
                        print("El Catalogo no está disponible.")
             


                        

                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


            elif choice == "buscar":
                if main !=None:

                    name = input("Introduzca el nombre por el que desea buscar: \n")
                    choiceExacto=input("Desea una busqueda exacta? Introduzca \"si\" o \"no\": ")
                    if choiceExacto=="si":
                        busquedaExacta=True
                    elif choiceExacto=="no":
                        busquedaExacta=False
                    else:
                        print("Opcion incorrecta, solo se acepta: \"si\" o \"no\"."+
                        " Se realizo una busqueda con el valor por defecto \"no\"")
                    catalog=main.getCatalogService()
                    listaIds=catalog.getTilesByName(name,busquedaExacta)
                    listaSeleccion=list()
                    i=0
                    print("\nElementos encontrados: \n")
                    for element in listaIds:
                        media=catalog.getTile(element)
                        listaSeleccion.append(media)
                        i+=1
                        print(" "+str(i)+"- ", end=' ')
                        print(media.info.name)

                    if len(listaIds) == 0:
                        print("No se encontraron coincidencias en tu busqueda\n")

                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


        ############################################################
        ##          LOGIN Y REFRESH AUTHORIZATION                 ##
        ############################################################

            elif choice == "login":
                if(main != None):
                    try:
                        autenticator=main.getAuthenticator()
                        user= input("Introduzca el usuario:\n")
                        print("Introduzca la contraseña\n")
                        password=hashlib.sha256(getpass().encode()).hexdigest()

                        token=autenticator.refreshAuthorization(user,password)                                            

                        print("¡Log in realizado correctamente!")
                    except IceFlix.TemporaryUnavailable:
                        print("No hay ningun autenticator disponible.")
                    except IceFlix.Unauthorized:
                        print("Credenciales incorrectas")
                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


            elif choice == "refresh":
                if user!=None and password!=None:
                    try:
                        autenticator=main.getAuthenticator()


                        token=autenticator.refreshAuthorization(user,password)

                        print("¡Se ha actualizado el token!\n")
                    except IceFlix.TemporaryUnavailable:
                        print("No hay ningun autenticator disponible.\n")
                    except IceFlix.Unauthorized:
                        print("Credenciales incorrectas\n")

                else:
                    print("Primero debe iniciar sesion con \"login\"")
                    


        ############################################################
        ##          SELECCIONAR MEDIA Y MODIFICARLO               ##
        ############################################################

            elif choice == "seleccionar":
                if main !=None:
                    if len(listaSeleccion) >>0:
                        numSelec=int(input("Seleccione el medio de los listados en la busqueda anterior indicando su numero:\n"))
                        try:
                            seleccionado=listaSeleccion[numSelec-1]
                            print("Seleccionado el siguiente media: ", end=' ')
                            print(seleccionado.info.name)
                        except IndexError:
                            print("El valor indicado no pertenece a la lista anterior\n")
                    else:
                        print("Antes de seleccionar debe realizar una busqueda con \"buscar\" o \"buscar_tag\".\n")
                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


            elif choice == "nuevo_tag":
                if main !=None:
                    if seleccionado !=None:
                        if user != None:
                            try:

                                tags = [item for item in input("Introduzca los tags que desea añadir dejando un espacio entre ellos : ").split()]
                                
                                catalog.addTags(seleccionado.id,tags,token)

                                print("Tags añadidos con éxito.\n")
                                
                            except IceFlix.WrongMediaId:
                                print("El identificador de media no es correcto\n")
                            except IceFlix.Unauthorized:
                                print("No tiene permiso para esta operacion.Pruebe a usar \"refresh\" y renovar el token\n")
                        else:
                            print("Antes debe loguearse. Utilice el comando \"login\"\n")

                    else:
                        print("Antes debe elegir un medio haciendo una busqueda y usando \"seleccionar\".\n")
                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\".\n")


            elif choice == "borrar_tag":
                if main !=None:
                    if seleccionado !=None:
                        if user != None:
                            try:

                                tags = [item for item in input("Introduzca los tags que desea borrar dejando un espacio entre ellos : ").split()]
                                
                                catalog.removeTags(seleccionado.id,tags,token)
                                print("Tags borrados con exito.\n")

                            except IceFlix.WrongMediaId:
                                print("El identificador de media no es correcto\n")
                            except IceFlix.Unauthorized:
                                print("No tiene permiso para esta operacion.Pruebe a usar \"refresh\" y renovar el token\n")
                        else:
                            print("Antes debe loguearse. Utilice el comando \"login\"\n")

                    else:
                        print("Antes debe elegir un medio haciendo una busqueda y usando \"seleccionar\"\n")
                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


            elif choice == "cambiar_nombre":
                if main !=None:
                    if seleccionado !=None:
                        if user != None:
                            nombre=input("Introduzca el nuevo nombre para el media seleccionado\n")

                            try:
                                catalog.renameTile(seleccionado.id,nombre,token)
                                
                                print("Nombre cambiado con exito.\n")
                            except IceFlix.WrongMediaId:
                                print("El identificador de media no es correcto\n")
                            except IceFlix.Unauthorized:
                                print("No tiene permiso para esta operacion.Pruebe a usar \"refresh\" y renovar el token\n")
                        else:
                            print("Antes debe loguearse. Utilice el comando \"login\"\n")
                    else:
                        print("Antes debe elegir un medio haciendo una busqueda y usando \"seleccionar\"\n")
                else:
                    print("Primero debe conectarse a MainServer usando la opcion \"conectar\"\n")


            elif choice == "exit":
                print(f'Cerrando cliente\n')
                go = False

            else:
                print(f'¡CUIDADO! \"{choice}\" no es una opcion. Para obtener un listado valido escriba: help\n')







        
        # adapter = broker.createObjectAdapter("PrinterAdapter")
        # #subscriber = adapter.addWithUUID(servant)

        # topic_name = "ServiceAvariability" #cambiar a ServiceAvariability
        # qos = {}
        # try:
        #     topic = topic_mgr.retrieve(topic_name)
        # except IceStorm.NoSuchTopic:
        #     topic = topic_mgr.create(topic_name)

        # topic.subscribeAndGetPublisher(qos, subscriber)
        # print("Waiting events... '{}'".format(subscriber))

        # adapter.activate()
        # self.shutdownOnInterrupt()
        # broker.waitForShutdown()

        # topic.unsubscribe(subscriber)

        return 0


sys.exit(Subscriber().main(sys.argv))






