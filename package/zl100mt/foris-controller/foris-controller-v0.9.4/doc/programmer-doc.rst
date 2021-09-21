Programmer documentation
========================

Code structure
--------------
The code itself consists of three main parts.

foris_controller
________________
the main module which contains

* basic schemas for json rpc
* buses implementation (ubus/unix-socket/...)
* app informations
* some shared base classes
* logic which routes message to a particular module

foris_controller_modules
________________________

* shared (don't touch __init__.py) other python packages will write to this directory as well
* modules recieve requests and are using backend dependent handlers to obtain responses for such requests


foris_controller_backends
_________________________

* shared (don't touch __init__.py) other python packages will write to this directory as well
* performs actual backend calls
  * read and parse files
  * executes commands and parse output
  * uci communication
  * augeas communication
  * module specifice backend actions
* is responsible for locking


Writing package plugins
=======================

see doc/examples/sample_module
