

#ifndef _BD_RELAY_H_
#define _BD_RELAY_H_

#include <stdlib.h>
#include <inttypes.h>
#include <termios.h>
#include "config.h"

//#define BD_DBG 0
#define BD_DBG 1
#define IOT_BD_PID_PATH "/run/bdrelay.pid"

#define IOT_BD_CONF        "/etc/zl100mt-app/zl100mt-app.conf"
#define IOT_BD_SEC_GENERAL "GENERAL"
#define IOT_BD_SEC_REMOTE  "REMOTE"
#define IOT_BD_KEY_TTY     "ttypath"
#define IOT_BD_KEY_BDRATE  "baudrate"
#define IOT_BD_KEY_NUMBER  "number"

#define IOT_MAX_BD_NUMBER 0x1FFFFF

#define IOT_FREE_AND_NULL(ptr) do {free(ptr); ptr = NULL;} while (0)

typedef struct _tty_baud_rates {
    int32_t baud_rate;
    speed_t termios_val;
} TTY_BDRATE;

typedef struct _bd_info {
    T_IOT_CFG   *pcfg;
    const char  *ttypath;
    int         ttyfd;
    int32_t     ttybaudrate;
    int32_t     myno;
    int32_t     remoteno;
} BD_INFO;

#endif
