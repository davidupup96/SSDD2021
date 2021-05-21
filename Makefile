#!/usr/bin/make -f
# -*- mode:makefile -*-


all: clean \
	start
	sleep 1
	$(MAKE) run-publisher

start:
	$(MAKE) run_icestorm
	sleep 1
	$(MAKE) run_iceflix

run-subscriber:
	gnome-terminal -- bash -c \
	"./subscriber.py --Ice.Config=subscriber.config; bash"

run_iceflix:
	gnome-terminal -- bash -c \
	$(MAKE) run_server 
	sleep 1
	$(MAKE) run_catalog
	sleep 1
	$(MAKE) run_media
	sleep 1
	$(MAKE) run_authenticator
	
add_user <user> <pass>:
	
	python registro.py ${PARAMS}
	
run_authenticator:
	gnome-terminal -- bash -c \
	"python3 Authenticator.py --Ice.Config=Authenticator.config; bash"

run_server:
	gnome-terminal -- bash -c \
	"python3 Server.py --Ice.Config=Server.config; bash"

run_catalog:
	gnome-terminal -- bash -c \
	"python3 Catalog.py --Ice.Config=Catalog.config; bash"

run_media:
	gnome-terminal -- bash -c \
	"python3 Media.py --Ice.Config=Media.config; bash"

run_icestorm:
	mkdir -p IceStorm/
	gnome-terminal -- bash -c \
	"icebox --Ice.Config=icebox.config &; bash"

clean:
	$(RM) *.out
	$(RM) -r __pycache__ IceStorm
