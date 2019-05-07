
SOURCES = config.c zl100mt.c
INCDPND = config.h zl100mt.h list.h

all: zl100mt-app ft4232_bitbang

zl100mt-app:$(SOURCES) $(INDDPND)
	@echo $(CC) -Wall $(SOURCES) $(CFLAGS) $(LDFLAGS) -o zl100mt-app
	$(CC) -Wall $(SOURCES) $(CFLAGS) $(LDFLAGS) -o zl100mt-app

ft4232_bitbang: ft4232_bitbang.c
	@echo $(CC) -Wall -lftdi $^ $(CFLAGS) $(LDFLAGS) -o $@
	$(CC) -Wall -lftdi $^ $(CFLAGS) $(LDFLAGS) -o $@
