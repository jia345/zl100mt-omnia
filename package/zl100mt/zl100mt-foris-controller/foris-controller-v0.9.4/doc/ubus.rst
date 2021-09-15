ubus
====
Bus inside openwrt. You can register an object on ubus and call function on the object.
It is also possible to send notifications via ubus.

Drawbacks
*********
* limit 1MB per message (downloading / uploading backups should be handled differently)
* no other functions can be called when during other function execution (each module is run within another process)
* strange ubus acl file (owner has to be root) - problem during tests under non-root user
