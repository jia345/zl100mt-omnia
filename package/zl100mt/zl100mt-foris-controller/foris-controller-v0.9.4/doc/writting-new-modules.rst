Writing Foris Modules
=====================

This guide will walk you through how to write foris-controller modules

1 Prepare the skeleton of the module
====================================
You can simply copy the sample_module dir structure.
Rename it according to you project name and fill in the licenses.

2 Write the schema
==================
in `foris_controller_modules/<name>/schema/<name>.json`
Fill in the appropriate jsonschema definitions of the requests/replies and notification which will be handled by your module.

3 Prepare main module part
==========================
in `foris_controller_modules/<name>/__init__.py`
Write all action_* which are required by your schema.
You can send notifications if it is necessary (e.g. after config update).
Set required functions for you handler

4 Write Mock handler part
=========================
in `foris_controller_modules/<name>/handlers/mock.py`
You can simply return some valid jsons to test the schema without interacting with the actual backend.
Note the you need to implement all required function in all backends.
Therefore you might need to delete openwrt handler for now or fill the required functions with raise NotImplemented() for now.

5 Write Test
============
in `tests` folder
Write some tests to fill some basic requirements for the function api.
Basically theses tests should prove that your schema mathes the messages.
You might need to run the tests in debug mod to see more verbose output::

    python setup.py test --addopts="--debug-output"

6 Write the backend part
========================
in `foris_controller_backends/<name>/__init__.py`
Try to write desired actions using existing backend functions.
See the sample example how the backed classes should look like.


7 Write OpenWRT handler part
============================
in `foris_controller_modules/<name>/handlers/openwrt.py`
Write the functions in a similar manner as in mock handler, but use needed backend functions to query for responses.


8 Test the actual OpenWRT backend (optional, but recommended)
=============================================================
in `tests` folder
Make sure that you have your system in a state that resambles the actual OpenWRT setup:

  * uci install
  * /etc/config/* filled
  * /etc/init.d/what_ever_service_needed mocked
  * ...

and run::

    python setup.py test --addopts="--debug-output --backend openwrt"

Note that CI in gitlab will actually test only mock backend for now since we don't have an appropriate TurrisOS system (or something which resembles it) in the docker image.

Result
======
If you have sucessfuly performed all the steps above you should end up with a tested module which can use mock and openwrt backends.
