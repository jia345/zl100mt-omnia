Foris Controller
================
Read messages from message bus.
And performs operation based on these commands.
e.g. updating dns settings, calling updater

Goals
-----
* replacible message bus (ubus, dbus, ...)
* replacible backend (uci, augeas, ...)
* modularity (making python packages as modules)

Language
--------
Python (2/3 or both)

Componets
---------

Bus
###
* replacible
* it might change to content of the message (e.g. add / remove unique messsage-id)
* each bus has two parts:

  * Listener -  listens to bus and recieves requests + sends replies
  * Sender - sends notification to connected clients

Message Router
##############
* makes sure that the message is passed to a targeted module
* raises an exception when a module is missing
* validates input and output messages according to jsonschema
* handles excptions which are triggered within the code

Modules
#######
* independent
* each module contains an json schema which describes a schema of the incomming messages
* each module is able to translate recieved messages to handler functions
* each module should be able to initialize the notification sending procedure

Handlers
########
* system dependent (openwrt/mock)
* calls appropriate backend functions

Backends
########
* locking
* helper backend classes use by Handlers

Protocol
--------

example1
########

>>> {"id": "1234", "kind": "request", "module": "wifi", "action": "get"}
Listener
>>> {"module": "wifi", "action": "get"}
Message Router
>>> {"action": "get"}
Wifi Module
>>> handler.get_current_wifi_settings()
>>> handler.obtain_card_info()
Handler
>>> uci_backend.get_current_wifi_settings()
>>> command_backend.obtain_card_info()
UCI backend + Command backend
>>> uci show wireless
>>> iw list
UCI backend + Command backend
<<< {"card1": {...}, "card2": {...}} - uci_backend.get_current_wifi_settings()
<<< {"phy0": {...}, "phy1": {...}} - command_backend.obtain_card_info()
Handler
<<< {"card1": {...}, "card2": {...}} - handler.get_current_wifi_settings()
<<< {"phy0": {...}, "phy1": {...}} - handler.obtain_card_info()
Wifi Module
<<< {"card1": {"phy1": ...}, "card2": {"phy2": ...}}
Message Router
<<< {"module": "wifi", "action":"get", "data": {"card1": {"phy1": ...}, "card2": {"phy2": ...}}}
Listener - output verification
<<< {"id": "1234", "kind": "reply", "module": "wifi", "action":"get", "data": {"card1": {"phy1": ...}, "card2": {"phy2": ...}}}

example2
########

>>> {"id": "2345", "kind": "request", "module": "wifi", "action": "set", "data": {"card1": {"phy1": ...}, "card2": {"phy2": ...}}}
Listener
>>> {"module": "wifi", "action": "set", "data": {"card1": {"phy1": ...}, "card2": {"phy2": ...}}}
Message Router
>>> {"action": "set", "data": {"card1": {"phy1": ...}, "card2": {"phy2": ...}}}
Wifi Module
>>> handler.update_current_wifi_settings()
handler
>>> uci_backend.update_current_wifi_settings()
UCI backend + Service backend(procd)
>>> uci set wireless.card1.optionx=y
>>> ...
>>> uci commit
>>> /etc/init.d/network reload
UCI backend + Service backend(procd)
<<< {"result": "OK"} - configuration_backend.update_wifi_settings()
Handler
<<< {"result": "OK"} - handler.update_wifi_settings()
Wifi Module
<<< {"result": "OK"}
Message Router
<<< {"module": "wifi", "action":"set", "data": {"result": "OK"}}
Listener
<<< {"id": "2345", "kind": "reply", "module": "wifi", "action":"set", "data": {"result": "OK"}} (send as a reply)
Sender
<<< {"id": "3456", "kind": "notification", "module": "wifi", "action": "set"} (send as a notification - clients can reload page)
