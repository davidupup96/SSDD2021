#!/usr/bin/make -f
# -*- mode:makefile -*-


all: clean \
	start
	sleep 1
	$(MAKE) run-publisher

start:
	$(MAKE) run-icestorm
	sleep 1
	$(MAKE) run-subscriber

run-subscriber:
	gnome-terminal -- bash -c \
	"./subscriber.py --Ice.Config=subscriber.config; bash"

run-publisher:
	gnome-terminal -- bash -c \
	"./publisher.py --Ice.Config=publisher.config; bash"

run-icestorm:
	mkdir -p IceStorm/
	gnome-terminal -- bash -c \
	"icebox --Ice.Config=icebox.config; bash"

clean:
	$(RM) *.out
	$(RM) -r __pycache__ IceStorm
