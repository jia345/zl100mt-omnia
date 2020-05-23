#ifndef _ZL100MT_H_
#define _ZL100MT_H_

#include <stdlib.h>
#include <inttypes.h>
#include <termios.h>
#include "config.h"

#define IOT_BD_PID_PATH "/run/zl100mt-app.pid"

#define BD_DBG 0

#define IOT_BD_CONF                 "/etc/zl100mt-app/zl100mt-app.conf"
#define IOT_BD_SEC_GENERAL          "GENERAL"
#define IOT_BD_SEC_DEBUG            "DEBUG"
#define IOT_BD_SEC_REMOTE           "REMOTE"
#define IOT_BD_SEC_PM               "PM"
#define IOT_BD_KEY_DBG_MODE         "debug"
#define IOT_BD_KEY_DATA_TTY         "rdss_ttypath"
#define IOT_BD_KEY_RDSS_BDRATE      "rdss_baudrate"
#define IOT_BD_KEY_RNSS_TTY         "rnss_ttypath"
#define IOT_BD_KEY_RNSS_BDRATE      "rnss_baudrate"
#define IOT_BD_KEY_NUMBER           "number"
#define IOT_BD_KEY_DRYRUN           "dryrun"
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
    const char  *rdss_ttypath;
    const char  *rnss_ttypath;
    int         rdss_ttyfd;
    int         rnss_ttyfd;
    uint32_t     rnss_baudrate;
    uint32_t     rdss_baudrate;
    uint32_t     local_sim;
    uint32_t     target_sim;
    uint32_t     is_dryrun;
    uint32_t     debug_mode;
} BD_INFO;

#endif
