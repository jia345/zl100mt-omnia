

#ifndef _BD_RELAY_H_
#define _BD_RELAY_H_

#include <stdlib.h>
#include <inttypes.h>
#include <termios.h>
#include "config.h"

#define IOT_BD_PID_PATH "/run/zl100mt-app.pid"

#define BD_DBG 1

#define IOT_BD_CONF        "/etc/zl100mt-app/zl100mt-app.conf"
#define IOT_BD_SEC_GENERAL "GENERAL"
#define IOT_BD_SEC_DEBUG   "DEBUG"
#define IOT_BD_SEC_REMOTE  "REMOTE"
#define IOT_BD_SEC_PM      "PM"
#define IOT_BD_KEY_TTY     "ttypath"
#define IOT_BD_KEY_BDRATE  "baudrate"
#define IOT_BD_KEY_NUMBER  "number"
#define IOT_BD_KEY_DRYRUN  "dryrun"
#define IOT_BD_KEY_COUNTER_TX_TOTAL "counter_tx_total"
#define IOT_BD_KEY_COUNTER_TX_SUCC  "counter_tx_success"
#define IOT_BD_KEY_COUNTER_TX_FAIL  "counter_tx_failure"
#define IOT_BD_KEY_LOCAL_SIM_NO     "local_sim_no"

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
    uint32_t     ttybaudrate;
    uint32_t     local_sim;
    uint32_t     target_sim;
    uint32_t     is_dryrun;
} BD_INFO;

#endif
