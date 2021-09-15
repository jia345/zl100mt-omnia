Foris controller
================
An program/library which is act as a client of foris-controller.

Requirements
============

* python2/3

Installation
============

	``python setup.py install``

Usage
=====
Connect to foris-controller using unix-socket and perform `get` action on `about` module.


	foris-client -m about -a get unix-socket --path /tmp/foris-controller-socket


Connect to foris-controller using ubus -socket and perform `get` action on `about` module and use input data from selected json file.

	foris-client -m about -a get -i data.json ubus --path /tmp/ubus.soc
