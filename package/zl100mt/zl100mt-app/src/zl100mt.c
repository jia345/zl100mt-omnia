#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <signal.h>
#include <stdarg.h>
#include <errno.h>
#include <syslog.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/queue.h>

#include <net/if.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

#include <libubox/blobmsg_json.h>
#include <libubox/uloop.h>
#include <libubox/runqueue.h>
#include <libubus.h>

#include <pthread.h>
#include <sys/ipc.h>

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#include "zl100mt.h"
#include "util.h"
#include "rdss.h"

void iot_dbg(const char *format, ...);

static struct ubus_context *ctx;
static struct blob_buf b;
static struct runqueue q;

#define RDSS_RESPONSE_TIMEOUT_MS 1000
static const char* rdss_send_pdu(eRdssPduType pdu_type, const char* pdu, size_t pdu_len, uint32_t timeout_ms);
static ssize_t rdss_find_first_pdu(const char* buf, size_t buf_size, char** found);

struct relayer {
    struct runqueue_process proc;
    int sock;
    BD_INFO *p_bd_info;
    uint8_t sock_buf[1600];
    uint8_t bd_txbuf[256];
    uint8_t bd_rxbuf[256];
    uint8_t bd_relay_msg[70];
};

typedef enum {
    UNINITIALIZED,
    INITIALIZED,
    DISCONNECTED,
    CONNECTED,
    BEIDOU_STATUS_MAX
} eBeidouStatus;

typedef struct {
    char time_utc[16];
    char date_utc[16];
    char latitude[16];
    char longitude[16];
    char altitude[16];
    uint8_t gps_status;
    uint8_t satellite_num;
    char speed_kn[32];
    char heading[32];
} rnss_info_t;

static rnss_info_t g_rnss_info = {
    .time_utc               = {0},
    .date_utc                   = {0},
    .latitude               = {0},
    .longitude              = {0},
    .altitude               = {0},
    .gps_status             = 0,
    .satellite_num          = 0,
    .speed_kn                  = {0},
    .heading                = {0},
};

typedef struct {
    eBeidouStatus rdss_status;
    uint8_t max_power;
    uint32_t tx_total;
    uint32_t tx_succ;
    uint32_t tx_fail;
} rdss_info_t;

static rdss_info_t g_rdss_info = {
    .rdss_status  = UNINITIALIZED,
    .max_power    = 0,
    .tx_total     = 0,
    .tx_succ      = 0,
    .tx_fail      = 0,
};

static eBeidouStatus g_beidou_status = UNINITIALIZED;
static rdss_buffer_t g_rdss_rx_buf = {
    .buf          = {0},
    .raw_cursor   = NULL,
    .pdu_cursor   = NULL,
    .rest_size    = RDSS_BUF_SIZE,
    .buf_lock     = 0,
};
BD_INFO g_bd_inf;

int magic_key = 0xBD;
static int g_sock = -1;
uint32_t g_cancelled    = 0;
uint32_t g_dbg_enabled  = 0;
uint32_t g_local_sim_no = 0;
uint32_t g_rdss_status = 0;
bool     g_is_relay_data_ready = false;

uint8_t g_DWXX[20];
uint8_t g_ZJXX[10];
uint8_t g_SJXX[7];

uint8_t g_bd_relay_msg[] = {
    /* section ID */
    0xBD, 0xBD,
    /* local SIM no */
    0x00, 0x00, 0x00, 0x00,
    /* last minutes data */
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    /* this minutes data */
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

TTY_BDRATE g_baud_rates[] = {
    /*{      0, B0      },*/
    {     50, B50     },
    {     75, B75     },
    {    110, B110    },
    {    134, B134    },
    {    150, B150    },
    {    200, B200    },
    {    300, B300    },
    {    600, B600    },
    {   1200, B1200   },
    {   1800, B1800   },
    {   2400, B2400   },
    {   4800, B4800   },
    {   9600, B9600   },
    {  19200, B19200  },
    {  38400, B38400  },
    {  57600, B57600  },
    { 115200, B115200 },
    { 230400, B230400 },
    { 460800, B460800 },
    { 500000, B500000 },
    { 576000, B576000 },
    { 921600, B921600 },
    {1000000, B1000000},
    {1152000, B1152000},
    {1500000, B1500000},
    {2000000, B2000000},
    {2500000, B2500000},
    {3000000, B3000000},
    {3500000, B3500000},
    {4000000, B4000000},
};

enum {
    GET_GNSS_INFO_CONNECTION,
    GET_GNSS_INFO_SIGNAL,
    GET_GNSS_INFO_SATELLITE_NUM,
    GET_GNSS_INFO_LATITUDE,
    GET_GNSS_INFO_LONGITUDE,
    GET_GNSS_INFO_ALTITUDE,
    GET_GNSS_INFO_SPEED,
    GET_GNSS_INFO_HEADING,
    GET_GNSS_INFO_TOTAL_MSG,
    GET_GNSS_INFO_SUCC_MSG,
    GET_GNSS_INFO_FAIL_MSG,
    GET_GNSS_INFO_TARGET_SIM,
    GET_GNSS_INFO_LOCAL_SIM,
    __GET_GNSS_INFO_MAX
};

static const struct blobmsg_policy get_gnss_info_policy[] = {
    [GET_GNSS_INFO_CONNECTION]      = { .name = "connection", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_SIGNAL]          = { .name = "signal", .type = BLOBMSG_TYPE_INT8 },
    [GET_GNSS_INFO_SATELLITE_NUM]   = { .name = "satelliteNum", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_LATITUDE]        = { .name = "latitude", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_LONGITUDE]       = { .name = "longitude", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_ALTITUDE]        = { .name = "altitude", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_SPEED]           = { .name = "speed", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_HEADING]         = { .name = "heading", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_TOTAL_MSG]       = { .name = "totalMsg", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_SUCC_MSG]        = { .name = "succMsg", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_FAIL_MSG]        = { .name = "failMsg", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_TARGET_SIM]      = { .name = "targetSim", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_LOCAL_SIM]       = { .name = "localSim", .type = BLOBMSG_TYPE_STRING },
};

enum {
    GNSS_TARGET_SIM,
    __SET_GNSS_TARGET_SIM_MAX
};

static const struct blobmsg_policy set_gnss_target_sim_policy[] = {
    [GNSS_TARGET_SIM]      = { .name = "target_sim", .type = BLOBMSG_TYPE_INT32 },
};

enum {
    TXSQ_target_sim,
    TXSQ_TRANS_TYPE,
    TXSQ_NEED_ACK,
    TXSQ_CONTENT,
    __SEND_RDSS_TXSQ_MAX
};

static const struct blobmsg_policy send_rdss_txsq_policy[] = {
    [TXSQ_target_sim]       = { .name = "target_sim", .type = BLOBMSG_TYPE_INT32 },
    [TXSQ_TRANS_TYPE]        = { .name = "trans_type", .type = BLOBMSG_TYPE_STRING }, // TODO
    [TXSQ_NEED_ACK]          = { .name = "need_ack", .type = BLOBMSG_TYPE_STRING }, // TODO
    [TXSQ_CONTENT]           = { .name = "content_data", .type = BLOBMSG_TYPE_STRING },
};

static const struct blobmsg_policy send_rdss_icjc_policy[] = {
};

static const struct blobmsg_policy send_rdss_gljc_policy[] = {
};

static const struct blobmsg_policy send_rdss_xtzj_policy[] = {
};

static const struct blobmsg_policy send_rdss_bbdq_policy[] = {
};

#if 0
struct get_gnss_info_request {
    struct ubus_request_data req;
    struct uloop_timeout timeout;
    char data[];
};

struct set_gnss_target_sim_request {
    struct ubus_request_data req;
    struct uloop_timeout timeout;
    int data[];
};
#endif

#if 0
typedef struct rdss_tx_pdu_q_entry {
    STAILQ_ENTRY(rdss_tx_pdu_q_entry) entries;
    rdss_msg_t *msg;
} rdss_tx_pdu_q_entry_t;

static STAILQ_HEAD(rdss_tx_msg_q_head, rdss_tx_pdu_q_entry) rdss_tx_msg_q_head = STAILQ_HEAD_INITIALIZER(rdss_tx_msg_q_head);

static void init_rdss_tx_msg_q()
{
    STAILQ_INIT(&rdss_tx_msg_q_head);
}

static rdss_msg_t *front_rdss_tx_msg_q()
{
    rdss_tx_pdu_q_entry_t *np = STAILQ_FIRST(&rdss_tx_msg_q_head);
    return (np == NULL) ? NULL : np->msg;
}

static void push_back_rdss_tx_msg_q(rdss_msg_t *msg)
{
    rdss_tx_pdu_q_entry_t *np;

    np = malloc(sizeof(struct rdss_tx_pdu_q_entry));
    np->msg = msg;
    STAILQ_INSERT_TAIL(&rdss_tx_msg_q_head, np, entries);
}

static void pop_front_rdss_tx_msg_q()
{
    rdss_tx_pdu_q_entry_t *np;

    np = STAILQ_FIRST(&rdss_tx_msg_q_head);
    STAILQ_REMOVE_HEAD(&rdss_tx_msg_q_head, entries);
    if (np->msg) free(np->msg);
    free(np);
}
#endif

static ssize_t rdss_find_first_pdu(const char* buf, size_t buf_size, char** found)
{
    *found = NULL;

    char* pdu_list[] = {
       "$DWSQ", "$TXSQ", "$CKSC", "$ICJC", "$XTZJ", "$SJSC", "$BBDQ", "$GLJC", // TX
       "$DWXX", "$TXXX", "$FKXX", "$ICXX", "$ZJXX", "$SJXX", "$BBXX", "$GLZK"  // RX
    };

    if (g_rdss_rx_buf.buf_lock == 1) return -1; // buf is locked, wait...

    size_t list_len = sizeof(pdu_list)/sizeof(pdu_list[0]);
    int i = 0;
    for (; i < list_len; i++) {
        char* tmp = find_str_in_buffer(pdu_list[i], buf, buf_size);

        if (tmp != NULL) { // find some message header
            if (*found == NULL || (tmp - *found < 0)) {
                *found = tmp;
                break;
            }
        }
    }

    size_t pdu_len = 11; // minimal size
    if (NULL != *found) {
        // check if message is complete
        if (0 == memcmp(*found, "$GLZK", 5)) {
            pdu_len = 17;
        } else if (0 == memcmp(*found, "$DWXX", 5)) {
            pdu_len = 30;
        } else if (0 == memcmp(*found, "$ICXX", 5)) {
            pdu_len = 22;
        } else if (0 == memcmp(*found, "$ZJXX", 5)) {
            pdu_len = 21;
        } else if (0 == memcmp(*found, "$SJXX", 5)) {
            pdu_len = 18;
        } else if (0 == memcmp(*found, "$FKXX", 5)) {
            pdu_len = 16;
        }
        if (*found - buf <=  buf_size - pdu_len) {
            if (0 == memcmp(*found, "$BBXX", 5) || 0 == memcmp(*found, "$TXXX", 5)) { //variable length
                pdu_len = ((*found)[5] << 8 | (*found)[6]);
    iot_dbg("pdu_len %d\n", pdu_len);
                if (*found - buf >  buf_size - pdu_len) {
                    *found = NULL;
                    pdu_len = -1;
                }
            }
        } else {
            *found = NULL;
            pdu_len = -1;
        }

        if (pdu_len > 0) {
            // check checksum
            char* pdu = *found;
            int checksum = 0;
            int i = 0;
            for (; i < pdu_len - 1; i++) {
                checksum = checksum ^ pdu[i];
            }
            if (pdu[pdu_len - 1] != checksum || pdu[pdu_len - 1] == 0) {
                *found = NULL;
                pdu_len = -1;
            }
        }
    }
    //if (*found != NULL) hexdump(LOG_DEBUG, "pdu <--", *found, pdu_len);
    return pdu_len;
}

static int zl100mt_get_gnss_info(struct ubus_context *ctx, struct ubus_object *obj,
                                 struct ubus_request_data *req, const char *method,
                                 struct blob_attr *msg)
{
    struct blob_attr *tb[__GET_GNSS_INFO_MAX];

    //blobmsg_parse(get_gnss_info_policy, ARRAY_SIZE(get_gnss_info_policy), tb, blob_data(msg), blob_len(msg));

    char tmp[64];
    blob_buf_init(&b, 0);
    blobmsg_add_string(&b, "result", "ok");
    blobmsg_add_string(&b, "connection", g_rnss_info.gps_status ? "on" : "off");
    blobmsg_add_u32(&b, "signal", g_rdss_info.max_power);
    //blobmsg_add_string(&b, "connection", "on");

    char beam[10];

    int i;
    for (i = 0; i < 6; i++) {
        memset(beam, 0, sizeof(beam));
        sprintf(beam, "beam%d", i+1);
        memset(tmp, 0, sizeof(tmp));
        sprintf(tmp, "%x", g_ZJXX[4+i]);
        blobmsg_add_string(&b, beam, tmp);
    }
    //memset(tmp, 0, sizeof(tmp));
    //sprintf(tmp, "%.2f", g_ZJXX[4+i]);
    //blobmsg_add_string(&b, "beam1", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_rnss_info.satellite_num);
    blobmsg_add_string(&b, "satelliteNum", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%s", g_rnss_info.latitude);
    blobmsg_add_string(&b, "latitude", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%s", g_rnss_info.longitude);
    blobmsg_add_string(&b, "longitude", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%s", g_rnss_info.altitude);
    blobmsg_add_string(&b, "altitude", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%s", g_rnss_info.speed_kn);
    blobmsg_add_string(&b, "speed", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%s", g_rnss_info.heading);
    blobmsg_add_string(&b, "heading", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_rdss_info.tx_total);
    blobmsg_add_string(&b, "totalMsg", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_rdss_info.tx_succ);
    blobmsg_add_string(&b, "succMsg", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_rdss_info.tx_fail);
    blobmsg_add_string(&b, "failMsg", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_bd_inf.target_sim);
    blobmsg_add_string(&b, "targetSim", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_bd_inf.local_sim);
    blobmsg_add_string(&b, "localSim", tmp);

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_set_gnss_target_sim(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{

    struct blob_attr *tb[__SET_GNSS_TARGET_SIM_MAX];
    uint32_t target_sim = 0;

    blobmsg_parse(set_gnss_target_sim_policy, ARRAY_SIZE(set_gnss_target_sim_policy), tb, blob_data(msg), blob_len(msg));

    blob_buf_init(&b, 0);

	if (tb[GNSS_TARGET_SIM]) {
		target_sim = blobmsg_get_u32(tb[GNSS_TARGET_SIM]);
        g_bd_inf.target_sim = target_sim;
        iot_cfg_set_int(g_bd_inf.pcfg, IOT_BD_SEC_REMOTE, IOT_BD_KEY_NUMBER, target_sim);
        iot_cfg_sync(g_bd_inf.pcfg);
        blobmsg_add_string(&b, "result", "ok");
    } else {
        blobmsg_add_string(&b, "result", "fail, please make sure 'target_sim' is integer number");
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_send_rdss_txsq(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{
    struct blob_attr *tb[__SEND_RDSS_TXSQ_MAX];
    const char* data = NULL;
    uint32_t target_sim = 0;
    blobmsg_parse(send_rdss_txsq_policy, ARRAY_SIZE(send_rdss_txsq_policy), tb, blob_data(msg), blob_len(msg));
    blob_buf_init(&b, 0);

	if (tb[TXSQ_target_sim]) {
		target_sim = blobmsg_get_u32(tb[TXSQ_target_sim]);
    } else {
		target_sim = g_bd_inf.target_sim;
    }

    if (tb[TXSQ_CONTENT]) {
		data = blobmsg_get_string(tb[TXSQ_CONTENT]);

        char txbuf[256] = {0};
        rdss_msg_txsq_t msg = {
            .local_sim = g_bd_inf.local_sim,
            .target_sim = target_sim,
            .data = {0},
            .data_len = 0
        };
        strncpy(msg.data, data, sizeof(msg.data));
        msg.data_len = strlen(data);
        ssize_t txlen = compose_rdss_txsq_pdu(txbuf, sizeof(txbuf), &msg);
        if (txlen > 0) {
            const char* resp_pdu = rdss_send_pdu(RDSS_TXSQ, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
            g_rdss_info.tx_total++;
            if (resp_pdu != NULL) {
                g_rdss_info.tx_succ++;
                blobmsg_add_string(&b, "result", "ok");
                char* flag[16] = {0};
                snprintf(flag, sizeof(flag), "0x%x", resp_pdu[10]);
                blobmsg_add_string(&b, "flag", flag);
                char* additional_info[16] = {0};
                strncpy(additional_info, &(resp_pdu[11]), 4);
                blobmsg_add_string(&b, "additional_info", additional_info);
            } else {
                g_rdss_info.tx_fail++;
                blobmsg_add_string(&b, "result", "fail, please try again later");
            }
        } else {
            blobmsg_add_string(&b, "result", "fail, please make sure the buffer is long enough");
        }
    } else {
        blobmsg_add_string(&b, "result", "request to send nothing, abort sending...");
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_send_rdss_icjc(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{
    blob_buf_init(&b, 0);

    char txbuf[32] = {0};
    size_t txlen = compose_rdss_icjc_pdu(txbuf, sizeof(txbuf));
    const char* resp_pdu = rdss_send_pdu(RDSS_ICJC, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
    if (NULL == resp_pdu) {
        blobmsg_add_string(&b, "result", "no response, please try again later");
        g_beidou_status = DISCONNECTED;
    } else {
        uint32_t local_sim = (
                (resp_pdu[7] << 16)
                | (resp_pdu[8] << 8)
                | resp_pdu[9]
                & 0x1FFFFF);
        if (g_bd_inf.local_sim != local_sim) {
            g_bd_inf.local_sim = local_sim;
            iot_cfg_set_int(g_bd_inf.pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, g_bd_inf.local_sim);
            iot_cfg_sync(g_bd_inf.pcfg);
            iot_dbg("write down local_sim: %d", local_sim);
        }
        blobmsg_add_string(&b, "result", "succeed");
        blobmsg_add_u32(&b, "local_sim", g_bd_inf.local_sim);
        g_beidou_status = CONNECTED;
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_send_rdss_gljc(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{
    blob_buf_init(&b, 0);

    char txbuf[32] = {0};
    uint8_t freq = 0;
    size_t txlen = compose_rdss_gljc_pdu(txbuf, sizeof(txbuf), freq);
    const char* resp_pdu = rdss_send_pdu(RDSS_GLJC, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
    if (NULL == resp_pdu) {
        blobmsg_add_string(&b, "result", "no response, please try again later");
    } else {
        uint8_t power_beam1 = resp_pdu[10];
        uint8_t power_beam2 = resp_pdu[11];
        uint8_t power_beam3 = resp_pdu[12];
        uint8_t power_beam4 = resp_pdu[13];
        uint8_t power_beam5 = resp_pdu[14];
        uint8_t power_beam6 = resp_pdu[15];
        blobmsg_add_string(&b, "result", "succeed");
        char tmp[16] = {0};
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam1);
        blobmsg_add_string(&b, "power_beam1", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam2);
        blobmsg_add_string(&b, "power_beam2", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam3);
        blobmsg_add_string(&b, "power_beam3", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam4);
        blobmsg_add_string(&b, "power_beam4", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam5);
        blobmsg_add_string(&b, "power_beam5", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam6);
        blobmsg_add_string(&b, "power_beam6", tmp);
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_send_rdss_xtzj(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{
    blob_buf_init(&b, 0);

    char txbuf[32] = {0};
    uint8_t freq = 0;
    size_t txlen = compose_rdss_xtzj_pdu(txbuf, sizeof(txbuf), freq);
    const char* resp_pdu = rdss_send_pdu(RDSS_XTZJ, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
    if (NULL == resp_pdu) {
        blobmsg_add_string(&b, "result", "no response, please try again later");
    } else {
        uint8_t ic_status = resp_pdu[10];
        uint8_t hw_status = resp_pdu[11];
        uint8_t battery_status = resp_pdu[12];
        uint8_t station_status = resp_pdu[13];
        uint8_t power_beam1 = resp_pdu[14];
        uint8_t power_beam2 = resp_pdu[15];
        uint8_t power_beam3 = resp_pdu[16];
        uint8_t power_beam4 = resp_pdu[17];
        uint8_t power_beam5 = resp_pdu[18];
        uint8_t power_beam6 = resp_pdu[19];
        blobmsg_add_string(&b, "result", "succeed");
        char tmp[16] = {0};
        snprintf(tmp, sizeof(tmp), "0x%x", ic_status);
        blobmsg_add_string(&b, "ic_status", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", hw_status);
        blobmsg_add_string(&b, "hw_status", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", battery_status);
        blobmsg_add_string(&b, "battery_status", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", station_status);
        blobmsg_add_string(&b, "station_status", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam1);
        blobmsg_add_string(&b, "power_beam1", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam2);
        blobmsg_add_string(&b, "power_beam2", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam3);
        blobmsg_add_string(&b, "power_beam3", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam4);
        blobmsg_add_string(&b, "power_beam4", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam5);
        blobmsg_add_string(&b, "power_beam5", tmp);
        snprintf(tmp, sizeof(tmp), "0x%x", power_beam6);
        blobmsg_add_string(&b, "power_beam6", tmp);
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static int zl100mt_send_rdss_bbdq(struct ubus_context *ctx, struct ubus_object *obj,
                                       struct ubus_request_data *req, const char *method,
                                       struct blob_attr *msg)
{
    blob_buf_init(&b, 0);

    char txbuf[32] = {0};
    size_t txlen = compose_rdss_bbdq_pdu(txbuf, sizeof(txbuf));
    const char* resp_pdu = rdss_send_pdu(RDSS_BBDQ, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
    if (NULL == resp_pdu) {
        blobmsg_add_string(&b, "result", "no response, please try again later");
    } else {
        char tmp[256] = {0};
        size_t max_buf_size = sizeof(tmp) - 1;
        size_t version_len = resp_pdu[5] << 8 | resp_pdu[6] - 11;
        size_t tmp_size = version_len > max_buf_size ? max_buf_size : version_len;
        strncpy(tmp, &(resp_pdu[10]), tmp_size);
        blobmsg_add_string(&b, "result", "succeed");
        blobmsg_add_string(&b, "version", tmp);
    }

    ubus_send_reply(ctx, req, b.head);

    return 0;
}

static const struct ubus_method zl100mt_methods[] = {
    UBUS_METHOD("get_gnss_info", zl100mt_get_gnss_info, get_gnss_info_policy),
    UBUS_METHOD("set_gnss_target_sim", zl100mt_set_gnss_target_sim, set_gnss_target_sim_policy),
    UBUS_METHOD("send_rdss_txsq", zl100mt_send_rdss_txsq, send_rdss_txsq_policy),
    UBUS_METHOD("send_rdss_icjc", zl100mt_send_rdss_icjc, send_rdss_icjc_policy),
    UBUS_METHOD("send_rdss_gljc", zl100mt_send_rdss_gljc, send_rdss_gljc_policy),
    UBUS_METHOD("send_rdss_xtzj", zl100mt_send_rdss_xtzj, send_rdss_xtzj_policy),
    UBUS_METHOD("send_rdss_bbdq", zl100mt_send_rdss_bbdq, send_rdss_bbdq_policy),
};

static struct ubus_object_type zl100mt_object_type = UBUS_OBJECT_TYPE("zl100mt", zl100mt_methods);

static struct ubus_object zl100mt_object = {
    .name = "zl100mt",
    .type = &zl100mt_object_type,
    .methods = zl100mt_methods,
    .n_methods = ARRAY_SIZE(zl100mt_methods),
};

#if !(BD_DBG)
/*
 * close all fds but 'exclude_fd'
 */
static void close_allfd(int exlude_fd)
{
    int tmp;
    struct rlimit rl;

    if (getrlimit(RLIMIT_NOFILE, &rl) < 0) {
        fprintf(stderr, "Failed to get rlimit, exit!\n");
        exit(1);
    }

    if (rl.rlim_max == RLIM_INFINITY)
        rl.rlim_max = 1024;

    for (tmp = 0; tmp < rl.rlim_max; tmp++) {
        if (tmp != exlude_fd)
            close(tmp);
    }
}

/*
 *
 * open pid file, lock it, write in pid, keep it open.
 *
 * This func keep a unique daemon. If it is already running, the pid file is
 * locked and this func will return failure.
 *
 * Return:
 *     >=0  fd of the opened pid file
 *     <0   failed
 */
static int lock_pid(void)
{
    int fd = -1;
    struct flock fl;
    pid_t my_pid;
    char buf[16];
    int err = 1;


    fd = open(IOT_BD_PID_PATH, O_RDWR | O_CREAT | O_TRUNC, S_IRWXU | S_IRGRP | S_IROTH);
    if (fd < 0) {
        fprintf(stderr, "Failed to open pid file: %s\n", strerror(errno));
        goto out;
    }

    fl.l_type = F_WRLCK;
    fl.l_start = 0;
    fl.l_whence = SEEK_SET;
    fl.l_len = 0;
    fl.l_pid = 0;

    if (fcntl(fd, F_GETLK, &fl) < 0) {
        fprintf(stderr, "Failed to get lock state: %s!\n", strerror(errno));
        goto out;
    }

    if (fl.l_type == F_UNLCK) {
        fl.l_type = F_WRLCK;
        if (fcntl(fd, F_SETLK, &fl)) {
            fprintf(stderr, "Failed to lock pid file: %s\n", strerror(errno));
            goto out;
        }
    } else {
        fprintf(stderr, "Pid file already locked!\n");
        goto out;
    }

    if (ftruncate(fd, 0)) {
        fprintf(stderr, "Failed to truncate pid file: %s\n", strerror(errno));
        goto out;
    }

    my_pid = getpid();
    sprintf(buf, "%d", (int)my_pid);
    
    if (write(fd, buf, strlen(buf)) < 0) {
        fprintf(stderr, "Failed to write pid file: %s\n", strerror(errno));
        goto out;
    }
    /* don't close pid file to keep it locked */
    err = 0;

out:
    if (err) {
        if (fd >= 0) {
            close(fd);
            fd = -1;
        }
    }
    return fd;
}

/*
 * send str 'buf1' to syslog with priority 'pri', whose value is one of:
 *
 *     LOG_EMERG    LOG_ALERT   LOG_CRIT  LOG_ERR
 *     LOG_WARNING  LOG_NOTICE  LOG_INFO  LOG_INFO
 *
 * Our iothub uses only 3 of them, 'err' / 'info' / 'debug'.
 */
static void iot_log(int pri, const char *buf1)
{
	syslog(LOG_LOCAL7 | pri, "%s", buf1);
}
#else
static void iot_log(int pri, const char *buf1)
{
    printf("%s\n", buf1);
}
#endif

/*
 * write to "/var/log/iothub.err"
 */
void iot_err(const char *format, ...)
{
	va_list ap;
	char buf[512];

	va_start(ap, format);
	vsnprintf(buf, sizeof(buf), (const char *)format, ap);
	va_end(ap);

	iot_log(LOG_ERR, buf);
}
/*
 * write to "/var/log/iothub.inf"
 */
void iot_inf(const char *format, ...)
{
    va_list ap;
    char buf[512];

    va_start(ap, format);
    vsnprintf(buf, sizeof(buf), (const char *)format, ap);
    va_end(ap);

    iot_log(LOG_INFO, buf);
}
/*
 * write to "/var/log/iothub.dbg"
 */
void iot_dbg(const char *format, ...)
{
    va_list ap;
    char buf[512];

    va_start(ap, format);
    vsnprintf(buf, sizeof(buf), (const char *)format, ap);
    va_end(ap);

    iot_log(LOG_DEBUG, buf);
}
/*
 * Log one dbg line: values of each byte in 'buf', prefixed with 'label'.
 * The values are in uppercase hex format, delimited by a space.
 */
void iot_logbuf(char *label, unsigned char *buf, int len)
{
	int i;
    char *tmp = NULL;

    if (g_bd_inf.debug_mode) {
        if ((tmp = (char *)malloc(strlen(label) + (3 * len) + 1))) {
            if (label)
                sprintf(tmp, "%s", label);

            for (i = 0; i < len; i++)
                sprintf(&(tmp[strlen(tmp)]), "%02X ", buf[i]);

            tmp[strlen(tmp)] = 0;
            iot_dbg("%s", tmp);

            IOT_FREE_AND_NULL(tmp);
        }
    }
}

#if 0
static void encrypt(unsigned char* buf, int len) {
    int i = 0;
    for (i = 0; i < len; i++) {
        buf[i] ^= magic_key;
    }
}

static void decrypt(unsigned char* buf, int len) {
    int i = 0;
    for (i = 0; i < len; i++) {
        buf[i] ^= magic_key;
    }
}
#endif

/*
 * close application upon (SIGINT / SIGTERM / SIGHUP)
 */
static void sig_handler(int sig)
{
	g_cancelled = sig;
}

static void set_sighandler(void)
{
	struct sigaction sa;

	memset(&sa, 0, sizeof(sa));
	sa.sa_flags = SA_NOCLDSTOP;
	sa.sa_handler = sig_handler;
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
}

static speed_t get_termios_bdrate(int bdrate)
{
    speed_t termios_bdrate = 0;
    int number;
    int i;

    number = (int)(sizeof(g_baud_rates) / sizeof(g_baud_rates[0]));
    for (i = 0; i < number; i++) {
        if (bdrate == g_baud_rates[i].baud_rate) {
            termios_bdrate = g_baud_rates[i].termios_val;
            break;
        }
    }

    if (i == number) {
        iot_err("Err: invalid baudrate=%d, use default 115200", bdrate);
        termios_bdrate = B115200;
    }

    return termios_bdrate;
}

static int init_bdserial(BD_INFO *pinf)
{
    int ret = -1;
    speed_t rdss_bdrate;
    speed_t rnss_bdrate;
    struct termios tms;

    rdss_bdrate = get_termios_bdrate(pinf->rdss_baudrate);
    rnss_bdrate = get_termios_bdrate(pinf->rnss_baudrate);

    // RDSS
    pinf->rdss_ttyfd = open(pinf->rdss_ttypath, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (pinf->rdss_ttyfd < 0) {
        iot_err("Err: open %s. %s", pinf->rdss_ttypath, strerror(errno));
        goto out;
    }
    fcntl(pinf->rdss_ttyfd, F_SETFL, 0);

    tcflush(pinf->rdss_ttyfd, TCIOFLUSH);
    if (tcgetattr(pinf->rdss_ttyfd, &tms)) {
        iot_err("Err: tcgetattr %s. %s", pinf->rdss_ttypath, strerror(errno));
        goto out;
    }

    tms.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | INPCK | ISTRIP | INLCR | IGNCR | ICRNL | IUCLC | IXON | IXOFF | IUTF8);
    tms.c_oflag &= ~OPOST;
    tms.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    tms.c_cflag &= ~(CSIZE | PARENB | CRTSCTS | CSTOPB);
    tms.c_cflag |= CS8 | CLOCAL | CREAD;
    cfsetispeed(&tms, rdss_bdrate);
    cfsetospeed(&tms, rdss_bdrate);

    tcflush(pinf->rdss_ttyfd, TCIOFLUSH);
    tcsetattr(pinf->rdss_ttyfd, TCSANOW, &tms);

    // RNSS
    //pinf->rnss_ttyfd = open(pinf->rnss_ttypath, O_RDWR | O_NOCTTY | O_NONBLOCK);
    pinf->rnss_ttyfd = open(pinf->rnss_ttypath, O_RDWR | O_NOCTTY);
    if (pinf->rnss_ttyfd < 0) {
        iot_err("Err: open %s. %s", pinf->rnss_ttypath, strerror(errno));
        goto out;
    }
    fcntl(pinf->rnss_ttyfd, F_SETFL, 0);

    tcflush(pinf->rnss_ttyfd, TCIOFLUSH);
    if (tcgetattr(pinf->rnss_ttyfd, &tms)) {
        iot_err("Err: tcgetattr %s. %s", pinf->rdss_ttypath, strerror(errno));
        goto out;
    }

    tms.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | INPCK | ISTRIP | INLCR | IGNCR | ICRNL | IUCLC | IXON | IXOFF | IUTF8);
    tms.c_oflag &= ~OPOST;
    tms.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    tms.c_cflag &= ~(CSIZE | PARENB | CRTSCTS | CSTOPB);
    tms.c_cflag |= CS8 | CLOCAL | CREAD;
    cfsetispeed(&tms, rnss_bdrate);
    cfsetospeed(&tms, rnss_bdrate);

    tcflush(pinf->rnss_ttyfd, TCIOFLUSH);
    tcsetattr(pinf->rnss_ttyfd, TCSANOW, &tms);

    ret = 0;
out:
    return ret;
}

static void reset_cfg(BD_INFO *pinf)
{
    if (pinf->pcfg) {
        pinf->rdss_ttypath = NULL;
        pinf->rnss_ttypath = NULL;
        iot_cfg_destroy(pinf->pcfg);
        pinf->pcfg = NULL;
    }
}

static int init_bdinf(BD_INFO *pinf)
{
    int ret = -1;

    pinf->rdss_ttyfd = -1;
    pinf->rnss_ttyfd = -1;
    pinf->pcfg = iot_cfg_new(IOT_BD_CONF);
    if (NULL == pinf->pcfg) {
        iot_inf("Err: open %s", IOT_BD_CONF);
        goto out;
    }
    pinf->rdss_ttypath = iot_cfg_get_str(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_DATA_TTY, NULL);
    pinf->rnss_ttypath = iot_cfg_get_str(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_RNSS_TTY, NULL);
    pinf->rdss_baudrate = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_RDSS_BDRATE, 0);
    pinf->rnss_baudrate = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_RNSS_BDRATE, 0);
    pinf->debug_mode  = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_DBG_MODE, 0);
    pinf->target_sim  = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_REMOTE,  IOT_BD_KEY_NUMBER, 0);
    pinf->local_sim   = 0;

    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_TOTAL, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_SUCC, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_FAIL, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, 0);
    iot_cfg_sync(pinf->pcfg);

    if ((NULL == pinf->rdss_ttypath) || (0 == pinf->rnss_ttypath))
    {
        goto out;
    }

    if (pinf->rdss_baudrate == NULL) pinf->rdss_baudrate = 115200;
    if (pinf->rnss_baudrate == NULL) pinf->rnss_baudrate = 9600;

    iot_inf("Configuration:");
    iot_inf("\trdss_ttypath       = %s", pinf->rdss_ttypath);
    iot_inf("\trdss_baudrate      = %d", pinf->rdss_baudrate);
    iot_inf("\trnss_ttypath       = %s", pinf->rnss_ttypath);
    iot_inf("\trnss_baudrate      = %d", pinf->rnss_baudrate);
    iot_inf("\tremote number = %d", pinf->target_sim);

    if (init_bdserial(pinf)) {
        goto out;
    }

    ret = 0;
out:
    if (ret) {
        reset_cfg(pinf);
    }
    return ret;
}

static int rx_nbytes(BD_INFO *pinf, unsigned char *rxbuf, int number)
{
    size_t rest_size = (size_t)number;
    ssize_t out;
    int ret = 0;

    //struct timeval timeout;
    //timeout.tv_sec  = 1;
    //timeout.tv_usec = 0;

    while (rest_size) {
        out = read(pinf->rdss_ttyfd, &(rxbuf[number - rest_size]), rest_size);
        if (out > 0) {
            rest_size -= out;
            ret  += out;
        } else if (out < 0) {
            iot_err("Err: read tty. %s", strerror(errno));
            ret = -1;
            break;
        }
    }

    return ret;
}

//
// Note:
// 1. message is supposed to be populated before calling this method
// 2. main loop will block for period specified by timeout when sending RDSS message
//
// args:
//  pdu_type: RDSS PDU type
//  pdu: pointer to the whole message to be sent
//  pdu_len: length of pdu
// return:
//  pointer to the response PDU in RDSS receiving buffer. return NULL means no response
//
static const char* rdss_send_pdu(eRdssPduType pdu_type, const char* pdu, size_t pdu_len, uint32_t timeout_ms)
{
    hexdump(LOG_DEBUG, "RDSS sending...", pdu, pdu_len);

    struct timeval start;
    gettimeofday(&start, NULL);

    int ret = write(g_bd_inf.rdss_ttyfd, pdu, pdu_len);
    while (!is_timer_expired(&start, timeout_ms)) {

        // if buffer is locked, wait 10 ms
        if (g_rdss_rx_buf.buf_lock == 1) {
            usleep(1000);
            continue;
        }

        // polling the RDSS receiving buffer continuously to see if response comes back
        char* p_found = NULL;
        size_t unhandled_size = g_rdss_rx_buf.raw_cursor - g_rdss_rx_buf.pdu_cursor;
        ssize_t rx_len = rdss_find_first_pdu(g_rdss_rx_buf.pdu_cursor, unhandled_size, &p_found);
        if (p_found != NULL) {
            hexdump(LOG_DEBUG, "RDSS received...", p_found, rx_len);
            g_rdss_rx_buf.pdu_cursor = p_found + rx_len;
            // check RDSS_TXXX at first
            if (0 == memcmp(p_found, "$TXXX", 5)) {
                // read out TXXX and advance the pdu_cursor
                hexdump(LOG_DEBUG, "logging TXXX <--", p_found, pdu_len);
                continue;
            }
            switch(pdu_type) {
                case RDSS_GLJC: // wait RDSS_GLZK
                    if (0 == memcmp(p_found, "$GLZK", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_DWSQ: // wait RDSS_DWXX
                    if (0 == memcmp(p_found, "$DWXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_TXSQ: // wait RDSS_FKXX
                    if (0 == memcmp(p_found, "$FKXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_ICJC: // wait RDSS_ICXX
                    if (0 == memcmp(p_found, "$ICXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_XTZJ: // wait RDSS_ZJXX
                    if (0 == memcmp(p_found, "$ZJXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_SJSC: // wait RDSS_SJXX
                    if (0 == memcmp(p_found, "$SJXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                case RDSS_BBDQ: // wait RDSS_BBXX
                    if (0 == memcmp(p_found, "$BBXX", 5)) {
                        return p_found;
                    } else {
                        hexdump(LOG_DEBUG, "dropping <--", p_found, pdu_len);
                    }
                    break;
                default:
                    // drop this pdu
                    return NULL;
            }
        }
        usleep(50000);
    }

    return NULL;
}

//static int pos_of_checksum_in_rdss_pdu(char* cmd_str) {
//    if (strcmp(cmd_str, "$GLZK") return 16;
//    if (strcmp(cmd_str, "$DWXX") return 16;
//}

static bool is_rx_rdss_pdu_complete(char* p_pdu) {
    size_t pdu_len = (*(p_pdu + 5) << 8) | *(p_pdu + 6);
    uint8_t checksum = *(p_pdu + 10 + pdu_len - 1);
    return ((pdu_len == 0) || (checksum == 0)) ? false : true;
}

static int rx_bd_pdu(BD_INFO *pinf,
        const char* cmd_str,
        unsigned char* buf,
        uint32_t timeout_ms)
{
    int ret = 0;
    ssize_t out;
    struct timeval start;
    gettimeofday(&start, NULL);
    unsigned char rxbuf[RDSS_BUF_SIZE];
    memset(rxbuf, 0, sizeof(rxbuf));
    char* pos = NULL;
    size_t rest_size = sizeof(rxbuf);
    bool is_data_complete = false;
    bool is_txxx_complete = false;

    while (!is_timer_expired(&start, timeout_ms)) {
        out = read(pinf->rdss_ttyfd, &(rxbuf[RDSS_BUF_SIZE - rest_size]), rest_size);
        if (out > 0) {
            rest_size -= out;
            ret  += out;
            pos = strstr((const char*)rxbuf, cmd_str);
            if (pos != NULL) is_data_complete = is_rx_rdss_pdu_complete(pos);
            if (is_data_complete) {
                size_t pdu_len = (*(pos + 5) << 8) | *(pos+ 6);
                memcpy(buf, pos, pdu_len);

                char tmp[32];
                memset(tmp, 0, sizeof(tmp));
                sprintf(tmp, "rx: %c%c%c%c%c\t", buf[0], buf[1], buf[2], buf[3], buf[4]);
                iot_logbuf(tmp, buf, pdu_len + 10);

                break;
            }
        } else if (out < 0) {
            iot_err("Err: read tty. %s", strerror(errno));
            ret = -1;
            break;
        }
    }

    char* cmd_txxx = "$TXXX";
    unsigned char txxx_buf[256];
    memset(txxx_buf, 0, sizeof(rxbuf));
    pos = strstr(rxbuf, cmd_txxx);
    if (pos != NULL) {
        is_txxx_complete = is_rx_rdss_pdu_complete(pos);
        if (!is_txxx_complete) {
            gettimeofday(&start, NULL);
            while (!is_timer_expired(&start, 100)) {
                out = read(pinf->rdss_ttyfd, &(rxbuf[RDSS_BUF_SIZE - rest_size]), rest_size);
                if (out > 0) {
                    rest_size -= out;
                    ret  += out;
                    pos = strstr(rxbuf, cmd_txxx);
                    if (pos != NULL) is_txxx_complete = is_rx_rdss_pdu_complete(pos);
                    if (is_txxx_complete) {
                        size_t pdu_len = (*(pos + 5) << 8) | *(pos+ 6);
                        memcpy(txxx_buf, pos, pdu_len);
                        unsigned char tmp[32];
                        memset(tmp, 0, sizeof(tmp));
                        sprintf(tmp, "rx: %c%c%c%c%c\t", buf[0], buf[1], buf[2], buf[3], buf[4]);
                        iot_logbuf(tmp, txxx_buf, pdu_len + 10);
                        break;
                    }
                } else if (out < 0) {
                    iot_err("Err: read tty. %s", strerror(errno));
                    ret = -1;
                    break;
                }
            }
        }
    }

    return ret;
}

#if 0
static int rx_bd_msg(BD_INFO *pinf, unsigned char* buf, size_t* len)
{
    int ret = 0;
    size_t msg_len = 0;

    ret = rx_nbytes(pinf, buf, 10); // read msg header, cmd + len + number
    *len = ret;
    if (10 == ret) {
        msg_len = (buf[5] << 8) | buf[6];
        ret = rx_nbytes(pinf, buf+10, msg_len-10); // read content
        *len += ret;
        if (ret == msg_len-10) {
            ret = *len;
        } else {
            ret = -1;
        }
    } else {
        ret = -1;
    }

    unsigned char tmp[32];
    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "rx: %c%c%c%c%c\t", buf[0], buf[1], buf[2], buf[3], buf[4]);
    iot_logbuf(tmp, buf, *len);

    return ret;
}

static void recv_rdss_txxx(BD_INFO *pinf)
{
    iot_dbg("\nreceiving beidou TXXX...\n");

    unsigned char rxbuf[256];

    struct timeval timeout;
    timeout.tv_sec  = 0;
    timeout.tv_usec = 10000; // 10ms

    int rdss_ttyfd = pinf->rdss_ttyfd;

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(rdss_ttyfd, &fds);

    size_t msg_len = 0;
    size_t txlen = 0;
    int rc = 0;

    memset(rxbuf, 0, sizeof(rxbuf));

    rc = select(rdss_ttyfd + 1, &fds, NULL, NULL, &timeout);
    if (rc < 0) {
        iot_dbg("%s: select error, rc %d, errno %d !!\n", __FUNCTION__, rc, errno);
    } else if (rc > 0) { // data available
        rc = rx_bd_msg(pinf, rxbuf, &msg_len);
        if (rc > 0) {
            if (0 == memcmp(rxbuf, "$TXXX", 5)) {
                memcpy(g_bd_relay_msg + 2, &(rxbuf[7]), 3); // assign local user address
                uint32_t local_sim = ((rxbuf[7] << 16) | (rxbuf[8] << 8) | rxbuf[9]) & 0x1FFFFF;
                if (pinf->local_sim != local_sim) {
                    pinf->local_sim = local_sim;
                    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, pinf->local_sim);
                    iot_cfg_sync(pinf->pcfg);
                    iot_dbg("write down local_sim: %d", local_sim);
                }
            }
        }
    }
}
#endif

static eBeidouStatus check_beidou_status(BD_INFO *pinf)
{
    iot_dbg("\nchecking beidou status...\n");

    char txbuf[32] = {0};

    ssize_t txlen = compose_rdss_xtzj_pdu(txbuf, sizeof(txbuf), 0);
    const char* resp_pdu = rdss_send_pdu(RDSS_XTZJ, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
    if (resp_pdu != NULL) {
        uint32_t local_sim = (
                (resp_pdu[7] << 16)
                | (resp_pdu[8] << 8)
                | resp_pdu[9]
                & 0x1FFFFF);
        if (pinf->local_sim != local_sim) {
            pinf->local_sim = local_sim;
            iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, pinf->local_sim);
            iot_cfg_sync(pinf->pcfg);
            iot_dbg("write down local_sim: %d", local_sim);
        }
        uint8_t ic_status = resp_pdu[10];
        uint8_t hw_status = resp_pdu[11];
        uint8_t battery_status = resp_pdu[12];
        uint8_t station_status = resp_pdu[13];
        uint8_t power_beam1 = resp_pdu[14];
        uint8_t power_beam2 = resp_pdu[15];
        uint8_t power_beam3 = resp_pdu[16];
        uint8_t power_beam4 = resp_pdu[17];
        uint8_t power_beam5 = resp_pdu[18];
        uint8_t power_beam6 = resp_pdu[19];
        int i = 0;
        uint8_t max_power = 0;
        // 00: < -158 dBW
        // 01: -156 ~ -157 dBW
        // 02: -154 ~ -155 dBW
        // 03: -152 ~ -153 dBW
        // 04: > -152 dBW
        for (; i < 6; i++) {
            max_power = max_power > resp_pdu[14+i] ? max_power : resp_pdu[14+i];
        }
        g_rdss_info.max_power = max_power;
        return CONNECTED;
    } else {
        return DISCONNECTED;
    }
    return DISCONNECTED;
}

static int init_dpi_socket()
{
    struct sockaddr_ll socket_address;

    int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));

    if (s == -1)
    {
        perror("Socket creation failed");
        exit (-1);
    }

    memset(&socket_address, 0, sizeof (socket_address));
    socket_address.sll_family = PF_PACKET;
    socket_address.sll_ifindex = if_nametoindex("lo");
    socket_address.sll_protocol = htons(ETH_P_ALL);

    if (0 > bind(s, (struct sockaddr*)&socket_address, sizeof(socket_address)))
    {
        perror("Bind");
        exit (-1);
    }

    return s;
}

static void rdss_thread_func(void *params)
{
    BD_INFO* bd_info = (BD_INFO*)params;
    int fd = bd_info->rdss_ttyfd;

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(fd, &fds);

    char buf[RDSS_BUF_SIZE];

    ssize_t rc = -1;
    while (!g_cancelled) {
        rc = read(fd, g_rdss_rx_buf.raw_cursor, g_rdss_rx_buf.rest_size);
        if (rc > 0) {
            g_rdss_rx_buf.raw_cursor += rc;
            g_rdss_rx_buf.rest_size -= rc;
        }

        // if buffer is full and no complete messages exist, move incomplete data to the start
        if (g_rdss_rx_buf.rest_size == 0) {
            iot_dbg("\n!!! receiving buffer is full, locking... !!!\n");
            g_rdss_rx_buf.buf_lock = 1;

            char* p_found = NULL;
            size_t unhandled_size = g_rdss_rx_buf.raw_cursor - g_rdss_rx_buf.pdu_cursor;
            char tmp_buffer[RDSS_BUF_SIZE];
            memcpy(tmp_buffer, g_rdss_rx_buf.pdu_cursor, unhandled_size);
            memset(g_rdss_rx_buf.buf, 0, sizeof(g_rdss_rx_buf.buf));
            memcpy(g_rdss_rx_buf.buf, tmp_buffer, unhandled_size);
            g_rdss_rx_buf.raw_cursor = g_rdss_rx_buf.buf + unhandled_size;
            g_rdss_rx_buf.pdu_cursor = g_rdss_rx_buf.buf;
            g_rdss_rx_buf.rest_size = sizeof(g_rdss_rx_buf.buf);

            iot_dbg("\n!!! receiving buffer is back !!!\n");
            g_rdss_rx_buf.buf_lock = 0;
        }
    }
}

static char* find_comma(const char* str, size_t str_len, uint32_t next_n)
{
    int count = 0;

    if (next_n == 0) return NULL;

    int i = 0;
    for (; i < str_len; i++) {
        if (str[i] == ',') {
            count += 1;
            if (count >= next_n) return &(str[i]);
        }
    }
}

static void rnss_thread_func(void *params)
{
    iot_dbg("\nrnss\n");
    BD_INFO* bd_info = (BD_INFO*)params;
    int fd = bd_info->rnss_ttyfd;

    char buf[1024];
    const char *delim = ",";
    char *ptr_prev = NULL;
    char *ptr_next = NULL;

    FILE* ss = fdopen(g_bd_inf.rnss_ttyfd, "r+");
    //FILE* ss = fopen("/dev/ttyUSB3", "r");
    //iot_dbg("\nopen /dev/ttyUSB3...\n");
    while (!g_cancelled) {

        //if (g_beidou_status != CONNECTED) continue;

        memset(buf, 0, sizeof(buf));

        char* line = fgets(buf, sizeof(buf), ss);
        if (line != NULL) {
            if (0 == strncmp(line, "$GNGGA", 6)) {
                iot_dbg("\nRNSS <--: %s", line);
                // time_UTC
                // latitude
                ptr_prev = find_comma(line, strlen(line), 2);
                ptr_next = find_comma(line, strlen(line), 4);
                memset(g_rnss_info.latitude, 0, sizeof(g_rnss_info.latitude));
                memcpy(g_rnss_info.latitude, ptr_prev + 1, ptr_next - ptr_prev - 1);
                // longitude
                ptr_prev = ptr_next;
                ptr_next = find_comma(line, strlen(line), 6);
                memset(g_rnss_info.longitude, 0, sizeof(g_rnss_info.longitude));
                memcpy(g_rnss_info.longitude, ptr_prev + 1, ptr_next - ptr_prev - 1);
                // RNSS status
                g_rnss_info.gps_status = atoi(ptr_next + 1);
                // satellite number
                ptr_prev = find_comma(line, strlen(line), 7);
                g_rnss_info.satellite_num = atoi(ptr_prev + 1);
                ptr_prev = find_comma(line, strlen(line), 9);
                ptr_next = find_comma(line, strlen(line), 11);
                memset(g_rnss_info.altitude, 0, sizeof(g_rnss_info.altitude));
                memcpy(g_rnss_info.altitude, ptr_prev + 1, ptr_next - ptr_prev - 1);
                iot_dbg("GNGGA update:\n \
                        gps status\t <%d>\n \
                        satellite num\t <%d>\n \
                        latitude\t <%s>\n \
                        longitue\t <%s>\n \
                        altitude\t <%s>\n",
                        g_rnss_info.gps_status,
                        g_rnss_info.satellite_num,
                        g_rnss_info.latitude,
                        g_rnss_info.longitude,
                        g_rnss_info.altitude);
            } else if (0 == strncmp(line, "$GNRMC", 6)) {
                iot_dbg("\nRNSS <--: %s", line);
                ptr_prev = find_comma(line, strlen(line), 1);
                ptr_next = find_comma(line, strlen(line), 2);
                memset(g_rnss_info.time_utc, 0, sizeof(g_rnss_info.time_utc));
                memcpy(g_rnss_info.time_utc, ptr_prev + 1, ptr_next - ptr_prev - 1);
                ptr_prev = find_comma(line, strlen(line), 7);
                ptr_next = find_comma(line, strlen(line), 8);
                memset(g_rnss_info.speed_kn, 0, sizeof(g_rnss_info.speed_kn));
                memcpy(g_rnss_info.speed_kn, ptr_prev + 1, ptr_next - ptr_prev - 1);
                ptr_prev = ptr_next;
                ptr_next = find_comma(line, strlen(line), 9);
                memset(g_rnss_info.heading, 0, strlen(g_rnss_info.heading));
                memcpy(g_rnss_info.heading, ptr_prev + 1, ptr_next - ptr_prev - 1);
                ptr_prev = ptr_next;
                ptr_next = find_comma(line, strlen(line), 10);
                memset(g_rnss_info.date_utc, 0, sizeof(g_rnss_info.date_utc));
                memcpy(g_rnss_info.date_utc, ptr_prev + 1, ptr_next - ptr_prev - 1);
                iot_dbg("GNRMC update:\n \
                        time_utc\t <%s>\n \
                        date_utc\t <%s>\n \
                        speed_kn\t <%s>\n \
                        heading\t <%s>\n",
                        g_rnss_info.time_utc,
                        g_rnss_info.date_utc,
                        g_rnss_info.speed_kn,
                        g_rnss_info.heading);
            }
        }
    }
}

//static hexdump(const char* buf, size_t len)
//{
//    char* tmp = NULL;
//    if ((tmp = (char *)malloc((3 * len) + 1))) {
//        if (label)
//            sprintf(tmp, "%s", label);
//
//        for (i = 0; i < len; i++)
//            sprintf(&(tmp[strlen(tmp)]), "%02X ", buf[i]);
//
//        tmp[strlen(tmp)] = 0;
//        iot_dbg("%s", tmp);
//
//        IOT_FREE_AND_NULL(tmp);
//    }
//    for (i = 0; i < len; i++) {
//        sprintf(&(output[strlen(output)]), "%02X ", buf[i]);
//    }
//}
//
static void rdss_check_status_cb(struct uloop_timeout *t)
{
    g_rdss_info.rdss_status = check_beidou_status(&g_bd_inf);
    uloop_timeout_set(t, 500);
}

static void rdss_txxx_poller_cb(struct uloop_timeout *t)
{
    if (g_rdss_rx_buf.buf_lock == 0) {
        size_t unhandled_size = g_rdss_rx_buf.raw_cursor - g_rdss_rx_buf.pdu_cursor;

        //if (unhandled_size) iot_dbg("\ntxxx reader unhandled_size %d\n", unhandled_size);

        char* p_found = NULL;
        ssize_t pdu_len = rdss_find_first_pdu(g_rdss_rx_buf.pdu_cursor, unhandled_size, &p_found);
        if (p_found != NULL) {
            hexdump(LOG_DEBUG, "TXXX RDSS received...", p_found, pdu_len);
            if (0 == memcmp(p_found, "$TXXX", 5)) {
            }
        }
    }
    uloop_timeout_set(t, 50);
}

#if 0
static void bd_rdss_poller_cb(struct uloop_timeout *t)
{
    iot_dbg("\npolling\n");
    BD_INFO* pinf = &g_bd_inf;
    int ret = 0;
    int fd = pinf->rdss_ttyfd;

    unsigned char txbuf[256];
    unsigned char rxbuf[256];
    memset(rxbuf, 0, sizeof(rxbuf));
    memset(txbuf, 0, sizeof(txbuf));
    size_t txlen   = 0;
    size_t msg_len = 0;

    struct timeval timeout;
    timeout.tv_sec  = 0;
    timeout.tv_usec = 50000; // 50ms

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(fd, &fds);

    ssize_t rc = 0;

    rc = select(fd + 1, &fds, NULL, NULL, &timeout);
    if (rc < 0) {
        iot_dbg("%s: select error, ret %d, errno %d !!\n", __FUNCTION__, ret, errno);
    } else if (rc > 0) { // data available
        rc = read(fd, g_rdss_rx_buf.raw_cursor, g_rdss_rx_buf.rest_size);
        if (rc > 0) {
            g_rdss_rx_buf.raw_cursor += rc;
            g_rdss_rx_buf.rest_size -= rc;
        }

        // if buffer is full, clear the buffer and move incomplete data to the start
        size_t unhandled_size = g_rdss_rx_buf.raw_cursor - g_rdss_rx_buf.pdu_cursor;
        if (g_rdss_rx_buf.rest_size == 0) {
            char tmp_buffer[RDSS_BUF_SIZE];
            memcpy(tmp_buffer, g_rdss_rx_buf.pdu_cursor, unhandled_size);
            memset(g_rdss_rx_buf.buf, 0, sizeof(g_rdss_rx_buf.buf));
            memcpy(g_rdss_rx_buf.buf, tmp_buffer, unhandled_size);
            g_rdss_rx_buf.raw_cursor = g_rdss_rx_buf.buf;
            g_rdss_rx_buf.pdu_cursor = g_rdss_rx_buf.buf;
        }

        while (true) {
            char* p_found = NULL;

            ssize_t msg_len = rdss_find_first_pdu(g_rdss_rx_buf.pdu_cursor, unhandled_size, &p_found);
            if (p_found == NULL) break; // quit the loop when all messages are handled

            // if message is not complete, read more at next time
            // if it's the response of message which has been sent out, call the callback
            rdss_msg_t *front_msg = front_rdss_tx_msg_q();

            g_rdss_rx_buf.pdu_cursor = p_found;
        }
        rc = rx_bd_msg(&g_bd_inf, "$ICXX", rxbuf, 500);
        if (ret > 0) {
            memcpy(g_bd_relay_msg + 2, &(rxbuf[7]), 3); // assign local user address
            uint32_t local_sim = ((rxbuf[7] << 16) | (rxbuf[8] << 8) | rxbuf[9]) & 0x1FFFFF;
            if (pinf->local_sim != local_sim) {
                pinf->local_sim = local_sim;
                iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, pinf->local_sim);
                iot_cfg_sync(pinf->pcfg);
                iot_dbg("write down local_sim: %d", local_sim);
            }
            return CONNECTED;
        }
        // check beidou status
        //g_beidou_status = check_beidou_status(&g_bd_inf);
        txlen = compose_rdss_icjc_pdu(txbuf);
        send_rdss_msg(pinf, txbuf, txlen);
    }

    if (g_beidou_status == CONNECTED) {
        if (g_is_relay_data_ready) {
            iot_dbg("xijia 111\n");
            txlen = compose_rdss_txsq_pdu(&g_bd_inf, txbuf, g_bd_relay_msg, sizeof(g_bd_relay_msg) / sizeof(g_bd_relay_msg[0]));
            send_rdss_msg(&g_bd_inf, txbuf, txlen);

            g_is_relay_data_ready = false;
            g_tx_total++;

#if 0
            while (true) {
                ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len, 500);
            iot_dbg("xijia 222\n");
                if (ret > 0) {
                    if (0 == memcmp(rxbuf, "$FKXX", 5)) {
            iot_dbg("xijia 333\n");
                        if (rxbuf[10]) { // check the feedback flag
                            iot_dbg("INFO: sending fail, error code 0x%hhx\n", rxbuf[10]);
            iot_dbg("xijia 444\n");
                            g_tx_fail++;
                            g_rdss_status = 0;
                        } else {
            iot_dbg("xijia 555\n");
                            g_tx_succ++;
                            g_rdss_status = 1;
                        }
                        break;
                    }
                }
            }
#endif
        }
    }

    //// update local SIM
    //txlen = compose_rdss_icjc_pdu(txbuf);
    //send_rdss_msg(&g_bd_inf, txbuf, txlen);
    //ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    //    iot_dbg("xijia 666\n");
    //if (ret > 0) {
    //    if (0 == memcmp(rxbuf, "$ICXX", 5)) {
    //        memcpy(g_bd_relay_msg + 2, &(rxbuf[7]), 3); // assign local user address
    //        uint32_t local_sim = ((rxbuf[7] << 16) | (rxbuf[8] << 8) | rxbuf[9]) & 0x1FFFFF;
    //        if (g_bd_inf.local_sim != local_sim) {
    //            g_bd_inf.local_sim = local_sim;
    //            iot_cfg_set_int(g_bd_inf.pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, g_bd_inf.local_sim);
    //            iot_cfg_sync(g_bd_inf.pcfg);
    //            iot_dbg("write down local_sim: %d", local_sim);
    //        }
    //    }
    //}

    // update connection status and position
    //txlen = compose_DWSQ_once(txbuf);
    //send_rdss_msg(&g_bd_inf, txbuf, txlen);
    //    iot_dbg("xijia 777\n");
    //ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    //if (ret > 0) {
    //    if (0 == memcmp(rxbuf, "$FKXX", 5)) {
    //        if (rxbuf[10]) { // check the feedback flag
    //            g_rdss_status = 0;
    //        } else {
    //            g_rdss_status = 1;

    //            ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    //            if (ret > 0) {
    //                if (0 == memcmp(rxbuf, "$DWXX", 5)) {
    //                    memcpy(g_DWXX, &(rxbuf[10]), 20);
    //                }
    //            }

    //            //rx_nbytes(&g_bd_inf, rxbuf, 10);
    //            //msg_len = (rxbuf[5] << 8) | rxbuf[6];
    //            //rx_nbytes(&g_bd_inf, rxbuf + 10, msg_len - 10);
    //            //if (0 == memcmp(rxbuf, "$DWXX", 5)) {
    //            //    memcpy(g_DWXX, &(rxbuf[10]), 20);
    //            //}
    //        }
    //    }
    //}

    // update signal strength ($XTZJ/$ZJXX)
    //txlen = compose_XTZJ(txbuf, 0);
    //send_rdss_msg(&g_bd_inf, txbuf, txlen);
    //ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    //if (ret > 0) {
    //    if (0 == memcmp(rxbuf, "$ZJXX", 5)) {
    //        memcpy(g_ZJXX, &(rxbuf[10]), sizeof(g_ZJXX));
    //    }
    //}

    iot_dbg("xijia 999\n");
    uloop_timeout_set(t, 0);
}
#endif

static void rdss_bdbd_relayer_cb(struct uloop_timeout *t)
{
    //iot_dbg("beidou relay callback ... \n");

    unsigned char buf_ip[1600];
    struct iphdr* p_iphdr   = NULL;
    struct tcphdr* p_tcphdr = NULL;
    size_t iphdr_offset     = 0;
    size_t tcphdr_offset    = 0;
    size_t tcpdata_offset   = 0;
    ssize_t recv_size       = -1;

    int i = 0;
    int fd_max = g_sock;
    size_t msg_len = 0;

    memset(&buf_ip, 0, sizeof(buf_ip));

    struct timeval timeout;
    timeout.tv_sec  = 0;
    timeout.tv_usec = 5000;

    fd_set fds;
    FD_ZERO(&fds);
    //FD_SET(g_bd_inf.rdss_ttyfd, &fds);
    FD_SET(g_sock, &fds);
    //fd_max = (g_sock > g_bd_inf.rdss_ttyfd) ? g_sock : g_bd_inf.rdss_ttyfd;

    int ret = select(fd_max + 1, &fds, NULL, NULL, &timeout);
    if (ret < 0) {
        iot_dbg("%s: select error, ret %d, errno %d !!\n", __FUNCTION__, ret, errno);
    } else if (ret > 0) {
        if (FD_ISSET(g_sock, &fds)) {
            recv_size = recv(g_sock, &buf_ip, sizeof(buf_ip), 0);
            if (recv_size == -1)
            {
                iot_dbg("%s: recv error, errno %d !!\n", __FUNCTION__, errno);
            }

            iphdr_offset = sizeof(struct ethhdr);
            p_iphdr      = (struct iphdr*)(buf_ip + iphdr_offset);

            /*
             * only print the TCP packets which have 0xBDBD at first two payload bytes
             */
            if (p_iphdr->protocol == IPPROTO_TCP)
            {
                tcphdr_offset   = iphdr_offset + (p_iphdr->ihl * 4);
                p_tcphdr        = (struct tcphdr*)(buf_ip + tcphdr_offset);
                tcpdata_offset = tcphdr_offset + p_tcphdr->th_off * 4;

                uint8_t * p_tcpdata = buf_ip + tcpdata_offset;
                char tmp[1600];

                memset(tmp, 0, 1600);
                if (p_tcpdata[0] == 0xbd && p_tcpdata[1] == 0xbd)
                {
                    sprintf(tmp, "\n* %s -> %s (IP packet)", \
                            inet_ntoa(*((struct in_addr *)&(p_iphdr->saddr))), \
                            inet_ntoa(*((struct in_addr *)&(p_iphdr->daddr))));
                    for(i = 0; i < recv_size - iphdr_offset; i++)
                    {
                        if (i%16 == 0)
                        {
                            sprintf(&(tmp[strlen(tmp)]), "\n0x%04hhx: ", i);
                        }
                        sprintf(&(tmp[strlen(tmp)]), "%02hhX ", buf_ip[i + iphdr_offset]);
                    }
                    iot_dbg("%s\n", tmp);
                    /* NOTICE: relay to beidou. Assuming no sticky package and only relay 32 bytes */
                    if (recv_size - tcpdata_offset >= 32) {
                        memcpy(g_bd_relay_msg + 6, g_bd_relay_msg + 6 + 32, 32); // move previous to current
                        memcpy(g_bd_relay_msg + 6 + 32, &(p_tcpdata[2]), 32); // fill current with new data
                        //g_is_relay_data_ready = true;
                        iot_cfg_sync(g_bd_inf.pcfg);
                        iot_dbg("relaying ...\n");
                        char txbuf[256] = {0};
                        rdss_msg_txsq_t msg = {
                            .local_sim = g_bd_inf.local_sim,
                            .target_sim = g_bd_inf.target_sim,
                            .data = {0},
                            .data_len = 0
                        };
                        size_t data_len = sizeof(g_bd_relay_msg) / sizeof(g_bd_relay_msg[0]);
                        strncpy(msg.data, g_bd_relay_msg, data_len);
                        msg.data_len = data_len;
                        //txlen = compose_rdss_txsq_pdu(&g_bd_inf, txbuf, g_bd_relay_msg, sizeof(g_bd_relay_msg) / sizeof(g_bd_relay_msg[0]));
                        //send_rdss_msg(&g_bd_inf, txbuf, txlen);
                        ssize_t txlen = compose_rdss_txsq_pdu(txbuf, sizeof(txbuf), &msg);
                        if (txlen > 0) {
                            const char* resp_pdu = rdss_send_pdu(RDSS_TXSQ, txbuf, txlen, RDSS_RESPONSE_TIMEOUT_MS);
                            g_rdss_info.tx_total++;
                            if (resp_pdu != NULL) {
                                g_rdss_info.tx_succ++;
                            } else {
                                g_rdss_info.tx_fail++;
                            }
                        }
                        //g_is_relay_data_ready = false;
                        //g_tx_total++;
                    }
                }
            }
        }
    }

    uloop_timeout_set(t, 50);
}

#if 0
            if (ret == pinf->rdss_ttyfd) {
                rx_nbytes(pinf, rxbuf, 22);
                iot_logbuf("received: ", rxbuf, 22);

                sleep(1);
                tcflush(pinf->rdss_ttyfd, TCIOFLUSH);

                txlen = compose_rdss_txsq_pdu(pinf, txbuf, content, sizeof(content) / sizeof(content[0]));
                write(pinf->rdss_ttyfd, txbuf, txlen);
                rx_nbytes(pinf, rxbuf, 16);
                iot_logbuf("received: ", rxbuf, 16);
                rx_nbytes(pinf, rxbuf, 54);
                iot_logbuf("received: ", rxbuf, 54);
            } else if (ret == s) {
            }
#endif

//int old_main (int argc, char *argv[])
//{
//    int pid_fd = -1;
//    BD_INFO *pinf = &g_bd_inf;
//    
//    if (argc == 2 && !(strcmp(argv[1], "-d"))) {
//        g_dbg_enabled = 1;
//    }
//
//#if !(BD_DBG)
//    int ret = 0;
//    //if (!g_dbg_enabled) {
//        /* daemonize */
//        if ((ret = daemon(0, 1))) {
//            fprintf(stderr, "Err: daemonize. %s\n\n", strerror(errno));
//            exit(1);
//        }
//        /* unique instance */
//        if ((pid_fd = lock_pid()) < 0) {
//            fprintf(stderr, "Err: lock failure!\n\n");
//            exit(1);
//        }
//        /* close all inheritated fd, excluding pid file */
//        close_allfd(pid_fd);
//    //}
//#endif
//    iot_inf("Starting zl100mt-app ...");
//
//    set_sighandler();
//
//    if (init_bdinf(pinf)) {
//        goto out;
//    }
//
//    mainloop(pinf);
//
//out:
//    g_cancelled = 1;
//    if (pid_fd >= 0) {
//        unlink(IOT_BD_PID_PATH);
//        close(pid_fd);
//        pid_fd = -1;
//    }
//
//    return 0;
//}

static void q_empty(struct runqueue *q)
{
    fprintf(stderr, "All done!\n");
    uloop_end();
}

static void q_relay_run(struct runqueue *q, struct runqueue_task *t)
{
    iot_dbg("q_relay_run ... \n");
}

static void q_relay_cancel(struct runqueue *q, struct runqueue_task *t, int type)
{
	iot_dbg("[%d/%d] cancel relay\n", q->running_tasks, q->max_running_tasks);
    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n", q->stopped,
            list_empty(&q->tasks_inactive.list), list_empty(&q->tasks_active.list),
            q->running_tasks, q->empty, t->queued);
    runqueue_task_add(q, t, false);
	runqueue_process_cancel_cb(q, t, type);
}

static void q_relay_complete(struct runqueue *q, struct runqueue_task *t)
{
    struct relayer *r = container_of(t, struct relayer, proc.task);
	iot_dbg("[%d/%d] finish relay\n", q->running_tasks, q->max_running_tasks);

    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n",
            q->stopped, list_empty(&q->tasks_inactive.list), list_empty(&q->tasks_active.list),
            q->running_tasks, q->empty, t->queued);
    struct relayer *nr = calloc(1, sizeof(*r));

	nr->proc = r->proc;
	//nr->proc.task.run_timeout = r->proc.task.proc.task.run_timeout;
	//nr->proc.task.complete = q_relay_complete;
    nr->sock = r->sock;
    nr->p_bd_info = r->p_bd_info;

    memcpy(nr->bd_relay_msg, r->bd_relay_msg, sizeof(r->bd_relay_msg));

	runqueue_task_add(q, &nr->proc.task, false);

	free(r);
}

void add_relayer_task()
{
    static const struct runqueue_task_type relayer_type = {
        .run = q_relay_run,
        .cancel = q_relay_cancel,
        .kill = runqueue_process_kill_cb,
    };

    uint8_t bd_relay_msg[] = {
        /* section ID */
        0xBD, 0xBD,
        /* local SIM no */
        0x00, 0x00, 0x00, 0x00,
        /* last minutes data */
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        /* this minutes data */
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    };

    int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));
    if (s == -1)
    {
        perror("Socket creation failed");
        exit (0);
    }

    //fd_set fds;
    //FD_ZERO(&fds);
    //FD_SET(pinf->rdss_ttyfd, &fds);
    //FD_SET(s, &fds);
    //fd_max = (s > pinf->rdss_ttyfd) ? s : pinf->rdss_ttyfd;

    struct sockaddr_ll socket_address;
    memset(&socket_address, 0, sizeof (socket_address));
    socket_address.sll_family = PF_PACKET;
    socket_address.sll_ifindex = if_nametoindex("lo");
    socket_address.sll_protocol = htons(ETH_P_ALL);

    int rc = bind(s, (struct sockaddr*)&socket_address, sizeof(socket_address));
    if (rc == -1)
    {
        perror("Bind");
        exit (0);
    }

    struct relayer *r = calloc(1, sizeof(*r));

  	r->proc.task.type = &relayer_type;
  	r->proc.task.run_timeout = 0;
  	r->proc.task.complete = q_relay_complete;
    r->sock = s;
    r->p_bd_info = &g_bd_inf;

    memcpy(r->bd_relay_msg, bd_relay_msg, sizeof(r->bd_relay_msg));

    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n",
        q.stopped, list_empty(&q.tasks_inactive.list), list_empty(&q.tasks_active.list),
        q.running_tasks, q.empty, &r->proc.task.queued);
	  runqueue_task_add(&q, &r->proc.task, false);
}

#if 0
void rdss_thread_func(void *params) {
    BD_INFO* bd_info = (BD_INFO*)params;
    int fd = bd_info->rnss_ttyfd;
    while(true) {
        // send ICJC every 3 seconds in order to check Beidou status

    }

    unsigned char txbuf[256];
    unsigned char rxbuf[256];

    struct timeval timeout;
    timeout.tv_sec  = 2;
    timeout.tv_usec = 0;

    int fd = bd_info->rdss_ttyfd;

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(fd, &fds);

    size_t msg_len = 0;
    size_t txlen = 0;
    int retry = RDSS_MAX_RETRY;
    int ret = 0;
    int rc = 0;

    while (retry--) {
        memset(rxbuf, 0, sizeof(rxbuf));
        memset(txbuf, 0, sizeof(txbuf));

        txlen = compose_rdss_icjc_pdu(txbuf);
        send_rdss_msg(pinf, txbuf, txlen);

        rc = select(fd + 1, &fds, NULL, NULL, &timeout);
        if (rc < 0) {
            iot_dbg("%s: select error, ret %d, errno %d !!\n", __FUNCTION__, ret, errno);
        } else if (rc > 0) { // data available
            ret = rx_bd_msg(pinf, rxbuf, &msg_len);
            if (ret > 0) {
                if (0 == memcmp(rxbuf, "$ICXX", 5)) {
                    memcpy(g_bd_relay_msg + 2, &(rxbuf[7]), 3); // assign local user address
                    uint32_t local_sim = ((rxbuf[7] << 16) | (rxbuf[8] << 8) | rxbuf[9]) & 0x1FFFFF;
                    if (pinf->local_sim != local_sim) {
                        pinf->local_sim = local_sim;
                        iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, pinf->local_sim);
                        iot_cfg_sync(pinf->pcfg);
                        iot_dbg("write down local_sim: %d", local_sim);
                    }
                }
            }
            return CONNECTED;
        } else { // (rc == 0) means timeout
            return DISCONNECTED;
        }
    }
    return DISCONNECTED;
}
#endif

int main(int argc, char **argv)
{
    int pid_fd = -1;
    int ret = 0;
    const char *ubus_socket = NULL;
    
    if (argc == 2 && !(strcmp(argv[1], "-d"))) {
        g_dbg_enabled = 1;
    }

    // initial the RDSS receiving buffer
    g_rdss_rx_buf.raw_cursor = g_rdss_rx_buf.buf;
    g_rdss_rx_buf.pdu_cursor = g_rdss_rx_buf.buf;
    g_rdss_rx_buf.rest_size = sizeof(g_rdss_rx_buf.buf);
    memset(g_rdss_rx_buf.buf, 0, sizeof(g_rdss_rx_buf.buf));

#if !(BD_DBG)
    //if (!g_dbg_enabled) {
        /* daemonize */
        if ((ret = daemon(0, 1))) {
            fprintf(stderr, "Err: daemonize. %s\n\n", strerror(errno));
            exit(1);
        }
        /* unique instance */
        if ((pid_fd = lock_pid()) < 0) {
            fprintf(stderr, "Err: lock failure!\n\n");
            exit(1);
        }
        /* close all inheritated fd, excluding pid file */
        close_allfd(pid_fd);
    //}
#endif
    iot_inf("Starting zl100mt-app ...");

    if (init_bdinf(&g_bd_inf)) {
        goto out;
    }

    g_sock = init_dpi_socket();

    //wait_bd_ready(&g_bd_inf);

    // start thread
    pthread_t rnss_thread;
    if (pthread_create(&rnss_thread, NULL, rnss_thread_func, (void*)&g_bd_inf)) {
        fprintf(stderr, "Error creating RNSS thread\n");
        return -1;
    }   

    pthread_t rdss_thread;
    if (pthread_create(&rdss_thread, NULL, rdss_thread_func, (void*)&g_bd_inf)) {
        fprintf(stderr, "Error creating RDSS thread\n");
        return -1;
    }   

    uloop_init();

    ctx = ubus_connect(ubus_socket);
    if (!ctx) {
        fprintf(stderr, "Failed to connect to ubus\n");
        return -1;
    }

    ubus_add_uloop(ctx);

    // add methods
    ret = ubus_add_object(ctx, &zl100mt_object);

    if (ret) fprintf(stderr, "Failed to add object: %s\n", ubus_strerror(ret));

    struct uloop_timeout rdss_check_status_timeout = {
        .cb = rdss_check_status_cb
    };
    uloop_timeout_set(&rdss_check_status_timeout, 0);

    struct uloop_timeout rdss_txxx_poller_timeout = {
        .cb = rdss_txxx_poller_cb
    };
    uloop_timeout_set(&rdss_txxx_poller_timeout, 0);

    // listen on 0xBDBD messages
    struct uloop_timeout relayer_timeout = {
        .cb = rdss_bdbd_relayer_cb
    };
    uloop_timeout_set(&relayer_timeout, 0);

    // RDSS: poll beidou status and send relayed messages out
    //struct uloop_timeout rdss_poller_timeout = {
    //    .cb = bd_rdss_poller_cb
    //};
    //uloop_timeout_set(&rdss_poller_timeout, 0);

    uloop_run();

    ubus_free(ctx);
    uloop_done();
    close(g_sock);

out:
    if (pid_fd >= 0) {
        unlink(IOT_BD_PID_PATH);
        close(pid_fd);
        pid_fd = -1;
    }

    return 0;
}
