
SOURCES = config.c zl100mt.c util.c rdss.c
INCDPND = config.h zl100mt.h list.h util.h rdss.h

all: zl100mt-app ft4232_bitbang bd_dump bd_ubox ubus_client ubus_server

zl100mt-app: $(SOURCES) $(INDDPND)
	$(CC) -Wall -lubus -lubox -lblobmsg_json -ljson-c -lpthread $(SOURCES) $(CFLAGS) $(LDFLAGS) -o zl100mt-app

ft4232_bitbang: ft4232_bitbang.c
	$(CC) -Wall -lftdi $^ $(CFLAGS) $(LDFLAGS) -o $@

bd_dump: bd_dump.c
	$(CC) -Wall $^ $(CFLAGS) $(LDFLAGS) -o $@

bd_ubox: bd_ubox.c
	$(CC) -Wall -O1 -Werror --std=gnu99 -g3 -lubox -lblobmsg_json -ljson-c $^ $(CFLAGS) $(LDFLAGS) -o $@

ubus_client: ubus_client.c
	$(CC) -Wall -O1 -Werror --std=gnu99 -g3 -lubus -lubox -lblobmsg_json -ljson-c $^ $(CFLAGS) $(LDFLAGS) -o $@
ubus_server: ubus_server.c
	$(CC) -Wall -O1 -Werror --std=gnu99 -g3 -lubus -lubox -lblobmsg_json -ljson-c $^ $(CFLAGS) $(LDFLAGS) -o $@
