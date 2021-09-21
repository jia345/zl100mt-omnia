client socket
=============

When foris-controller is started with  `-C <path>` argument,
it creates a unix socket which can be used to forward messages to runnig instance of foris-controller.

It can handle notifications as well as request/reply messages.

Message format
--------------
First 4 bytes represent the messages length. The least significant byte comes first.
5 => '\5\0\0\0' (lenght=5)

The rest of the messages is supposed to be a json string which matches one of foris-controller's schemas.
So message which sends {} would look like this
o strip the first 4 characters of eac

    \2\0\0\0{}
and if it matched the schema (which is not) it would've been accepted.


Notifications
-------------
The notification message should be look like this

    \80\0\0\0{"module": "my_module", "kind": "notification", "action": "my_action", "data": {"my_data": "..."}}

No response is provided. And it doesn't make sense to read it.

If the notification is in an incorrect format the connection is closed and you might need to reconnect.

Request/Reply
-------------
The request message should be look like this

    \104\0\0\0{"module": "my_module", "kind": "request", "action": "my_action", "data": {"my_data": "..."}}

The response should be provided and it looks similar to the request

    \134\0\0\0{"module": "my_module", "kind": "reply", "action": "my_action", "data": {"my_data": "..."}}

If the request is in an incorrect format the connection is closed a no response is read.
