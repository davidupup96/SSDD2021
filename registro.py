#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import json
import hashlib
from sys import argv

if(len(sys.argv) ==3):
    jsonFile = open("credenciales.json", "r+") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    #jsonFile.close() # Close the JSON file
    
    found=False
    
    for user in data["usuarios"]:
        if(user["nombre"] == sys.argv[1]):
            print("Ese username ya está en uso.")
            found=True
            break
        
    if(found is False) :     
        nuevoUser = {
                "nombre": sys.argv[1],
                "pass": hashlib.sha256(sys.argv[2].encode()).hexdigest()
                
            }

        data["usuarios"].append(nuevoUser) 
        # Sets file's current position at offset.
        jsonFile.seek(0)
        json.dump(data, jsonFile, ensure_ascii=False, indent = 4)
        jsonFile.close() # Close the JSON file
    

else:
   
    print("Debes introducir un usuario y password.")






