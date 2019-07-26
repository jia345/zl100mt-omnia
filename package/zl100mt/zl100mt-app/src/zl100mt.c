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

static struct runqueue q;

#include "zl100mt.h"

static struct ubus_context *ctx;
static struct blob_buf b;

void iot_dbg(const char *format, ...);

static int g_sock = -1;
uint32_t g_cancelled    = 0;
uint32_t g_dbg_enabled  = 0;
uint32_t g_local_sim_no = 0;
uint32_t g_connection_status = 0;
float    g_signal_strength = 0.0;
uint32_t g_satellite_num = 0;
uint32_t g_tx_total     = 0;
uint32_t g_tx_succ      = 0;
uint32_t g_tx_fail      = 0;
bool g_is_relay_data_ready = false;

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

int magic_key = 0xBD;

BD_INFO g_bd_inf;

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
    GET_GNSS_INFO_TOTAL_MSG,
    GET_GNSS_INFO_SUCC_MSG,
    GET_GNSS_INFO_FAIL_MSG,
    GET_GNSS_INFO_TARGET_SIM,
    GET_GNSS_INFO_LOCAL_SIM,
    __GET_GNSS_INFO_MAX
};

static const struct blobmsg_policy get_gnss_info_policy[] = {
    [GET_GNSS_INFO_CONNECTION]      = { .name = "connection", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_SIGNAL]          = { .name = "signal", .type = BLOBMSG_TYPE_STRING },
    [GET_GNSS_INFO_SATELLITE_NUM]   = { .name = "satelliteNum", .type = BLOBMSG_TYPE_STRING },
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

static int zl100mt_get_gnss_info(struct ubus_context *ctx, struct ubus_object *obj,
                                 struct ubus_request_data *req, const char *method,
                                 struct blob_attr *msg)
{
    struct blob_attr *tb[__GET_GNSS_INFO_MAX];

    blobmsg_parse(get_gnss_info_policy, ARRAY_SIZE(get_gnss_info_policy), tb, blob_data(msg), blob_len(msg));

    char tmp[64];
    blob_buf_init(&b, 0);
    blobmsg_add_string(&b, "result", "ok");
    blobmsg_add_string(&b, "connection", g_connection_status ? "on" : "off");

    char beam[10];

    int i;
    for (i = 0; i < 6; i++) {
        memset(beam, 0, sizeof(beam));
        sprintf(beam, "beam%d", i);
        memset(tmp, 0, sizeof(tmp));
        sprintf(tmp, "%x", g_ZJXX[4+i]);
        blobmsg_add_string(&b, beam, tmp);
    }
    //memset(tmp, 0, sizeof(tmp));
    //sprintf(tmp, "%.2f", g_ZJXX[4+i]);
    //blobmsg_add_string(&b, "beam1", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_satellite_num);
    blobmsg_add_string(&b, "satelliteNum", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_tx_total);
    blobmsg_add_string(&b, "totalMsg", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_tx_succ);
    blobmsg_add_string(&b, "succMsg", tmp);

    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "%d", g_tx_fail);
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

static const struct ubus_method zl100mt_methods[] = {
    UBUS_METHOD("get_gnss_info", zl100mt_get_gnss_info, get_gnss_info_policy),
    UBUS_METHOD("set_gnss_target_sim", zl100mt_set_gnss_target_sim, set_gnss_target_sim_policy),
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
    speed_t termios_bdrate;
    struct termios tms;

    termios_bdrate = get_termios_bdrate(pinf->ttybaudrate);

    pinf->ttyfd = open(pinf->ttypath, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (pinf->ttyfd < 0) {
        iot_err("Err: open %s. %s", pinf->ttypath, strerror(errno));
        goto out;
    }
    fcntl(pinf->ttyfd, F_SETFL, 0);

    tcflush(pinf->ttyfd, TCIOFLUSH);
    if (tcgetattr(pinf->ttyfd, &tms)) {
        iot_err("Err: tcgetattr %s. %s", pinf->ttypath, strerror(errno));
        goto out;
    }

    tms.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | INPCK | ISTRIP | INLCR | IGNCR | ICRNL | IUCLC | IXON | IXOFF | IUTF8);
    tms.c_oflag &= ~OPOST;
    tms.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    tms.c_cflag &= ~(CSIZE | PARENB | CRTSCTS | CSTOPB);
    tms.c_cflag |= CS8 | CLOCAL | CREAD;
    cfsetispeed(&tms, termios_bdrate);
    cfsetospeed(&tms, termios_bdrate);

    tcflush(pinf->ttyfd, TCIOFLUSH);
    tcsetattr(pinf->ttyfd, TCSANOW, &tms);

    ret = 0;
out:
    return ret;
}

static void reset_cfg(BD_INFO *pinf)
{
    if (pinf->pcfg) {
        pinf->ttypath = NULL;
        iot_cfg_destroy(pinf->pcfg);
        pinf->pcfg = NULL;
    }
}

static int init_bdinf(BD_INFO *pinf)
{
    int ret = -1;

    pinf->ttyfd = -1;
    pinf->pcfg = iot_cfg_new(IOT_BD_CONF);
    if (NULL == pinf->pcfg) {
        iot_inf("Err: open %s", IOT_BD_CONF);
        goto out;
    }
    pinf->ttypath     =          iot_cfg_get_str(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_TTY,    NULL);
    pinf->ttybaudrate = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_BDRATE, 0);
    pinf->debug_mode  = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_GENERAL, IOT_BD_KEY_DBG_MODE, 0);
    pinf->target_sim  = (int32_t)iot_cfg_get_int(pinf->pcfg,  IOT_BD_SEC_REMOTE,  IOT_BD_KEY_NUMBER, 0);
    pinf->local_sim   = 0;

    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_TOTAL, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_SUCC, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_COUNTER_TX_FAIL, 0);
    iot_cfg_set_int(pinf->pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, 0);
    iot_cfg_sync(pinf->pcfg);

    if ((NULL == pinf->ttypath) || (0 == pinf->target_sim) || (0 == pinf->ttybaudrate))
    {
        goto out;
    }
    iot_inf("Configuration:");
    iot_inf("\tttypath       = %s", pinf->ttypath);
    iot_inf("\tbaudrate      = %d", pinf->ttybaudrate);
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

static void pack_no(uint8_t *buf, uint32_t no)
{
    buf[0] = (uint8_t)((no & 0xFF0000) >> 16);
    buf[1] = (uint8_t)((no & 0x00FF00) >> 8);
    buf[2] = (uint8_t)( no & 0x0000FF);
}

static void pack_uint16(uint8_t *buf, uint16_t u16)
{
    buf[0] = (uint8_t)(u16 >> 8);
    buf[1] = (uint8_t)(u16 & 0xFF);
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |
 * |    |    |    |    |    |         |              |    |                   |                   |         |    |
 * |----+----+----+----+----+---------+--------------+----+--------------+----+--------------+----+---------+----|
 * |    |    |    |    |    |         |              |    |                   |                   |         |    |
 * | $  | D  | W  | S  | Q  | bytelen |  my  number  |type| altitude & antenna|   air pressure    |   freq  |crc |
 */
static size_t compose_DWSQ_once(unsigned char *buf)
{
    int i;
    int len = 22;
    memset(buf, 0, len);
    memcpy(buf, "$DWSQ", 5);
    buf[6] = len;
    buf[10] = 4; // b 0000 0100
    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | ....... | n |
 * |    |    |    |    |    |         |              |    |              |         |    |         |   |
 * |----+----+----+----+----+---------+--------------+----+--------------+---------+----+---------+---|
 * |    |    |    |    |    |         |              |    |              |         |    |         |   |
 * | $  | T  | X  | S  | Q  | bytelen |  my  number  |type| remote number| bit len |ACK?| content |crc|
 */
static size_t compose_TXSQ(BD_INFO *pinf, unsigned char *buf, unsigned char *content, uint16_t bytelen)
{
    uint16_t bitlen = bytelen << 3;
    uint16_t totalbytelen = bytelen + 18;
    uint16_t i;

    memcpy(buf, "$TXSQ", 5);
    pack_uint16(&(buf[5]), totalbytelen);
    pack_no(&(buf[7]), pinf->local_sim);
    buf[10] = 0x46;
    pack_no(&(buf[11]), pinf->target_sim);
    pack_uint16(&(buf[14]), bitlen);
    buf[16] = 0;
    memcpy(&(buf[17]), content, bytelen);
    buf[totalbytelen - 1] = buf[0];
    for (i = 1; i < (totalbytelen - 1); i++) {
        buf[totalbytelen - 1] = buf[totalbytelen - 1] ^ buf[i];
    }

    return totalbytelen;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 |
 * |    |    |    |    |    |         |              |    |    |
 * |----+----+----+----+----+---------+--------------+----+----|
 * |    |    |    |    |    |         |              |    |    |
 * | $  | C  | K  | S  | C  | bytelen |  user number |rate|crc |
 */
static size_t compose_CKSC(unsigned char *buf, uint8_t rate)
{
    int i;
    int len = 12;
    memset(buf, 0, len);
    memcpy(buf, "$CKSC", 5);
    buf[6] = len;
    buf[10] = rate;

    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 |
 * |    |    |    |    |    |         |              |    |    |
 * |----+----+----+----+----+---------+--------------+----+----|
 * |    |    |    |    |    |         |              |    |    |
 * | $  | I  | C  | J  | C  | bytelen | my number(0) |  0 | crc|
 */
static size_t compose_ICJC(unsigned char *buf)
{
    int i;
    int len = 12;

    memset(buf, 0, len);
    memcpy(buf, "$ICJC", 5);
    buf[6] = len;

    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 |
 * |    |    |    |    |    |         |              |         |    |
 * |----+----+----+----+----+---------+--------------+--------+-----|
 * |    |    |    |    |    |         |              |         |    |
 * | $  | X  | T  | Z  | J  | bytelen |  user number | cycle_s | crc|
 */
static size_t compose_XTZJ(unsigned char *buf, uint16_t cycle_s)
{
    int i;
    int len = 13;
    memset(buf, 0, len);
    memcpy(buf, "$XTZJ", 5);
    buf[6] = len;
    buf[10] = (cycle_s & 0xFF00) >> 8;
    buf[11] = cycle_s & 0xFF;

    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 |
 * |    |    |    |    |    |         |              |         |    |
 * |----+----+----+----+----+---------+--------------+--------+-----|
 * |    |    |    |    |    |         |              |         |    |
 * | $  | S  | J  | S  | C  | bytelen |  user number | cycle_s | crc|
 */
static size_t compose_SJSC(unsigned char *buf, uint16_t cycle_s)
{
    int i;
    int len = 13;
    memset(buf, 0, len);
    memcpy(buf, "$SJSC", 5);
    buf[6] = len;
    buf[10] = (cycle_s & 0xFF00) >> 8;
    buf[11] = cycle_s & 0xFF;

    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
 * |    |    |    |    |    |         |              |    |
 * |----+----+----+----+----+---------+--------------+----|
 * |    |    |    |    |    |         |              |    |
 * | $  | B  | B  | D  | Q  | bytelen |  user number | crc|
 */
static size_t compose_BBDQ(unsigned char *buf)
{
    int i;
    int len = 10;
    memset(buf, 0, len);
    memcpy(buf, "$BBDQ", 5);
    buf[6] = len;

    for (i = 0; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

static int rx_nbytes(BD_INFO *pinf, unsigned char *rxbuf, int number)
{
    size_t rest = (size_t)number;
    ssize_t out;
    int ret = 0;

    while (rest) {
        out = read(pinf->ttyfd, &(rxbuf[number - rest]), rest);
        if (out > 0) {
            rest -= out;
            ret  += out;
        } else if (out < 0) {
            iot_err("Err: read tty. %s", strerror(errno));
            ret = -1;
            break;
        }
    }

    return ret;
}

struct relayer {
    struct runqueue_process proc;
    int sock;
    BD_INFO *p_bd_info;
    uint8_t sock_buf[1600];
    uint8_t bd_txbuf[256];
    uint8_t bd_rxbuf[256];
    uint8_t bd_relay_msg[70];
};

static int tx_bd_msg(BD_INFO *pinf, unsigned char* buf, size_t len)
{
    unsigned char tmp[32];
    memset(tmp, 0, sizeof(tmp));
    sprintf(tmp, "tx: %c%c%c%c%c\t", buf[0], buf[1], buf[2], buf[3], buf[4]);
    iot_logbuf(tmp, buf, len);

    int ret = write(pinf->ttyfd, buf, len);

    return ret;
}

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

static void wait_bd_ready(BD_INFO *pinf)
{
    iot_dbg("\nwaiting beidou ready ...\n");

    unsigned char txbuf[256];
    unsigned char rxbuf[256];

    struct timeval timeout;
    timeout.tv_sec  = 2;
    timeout.tv_usec = 0;

    int ttyfd = pinf->ttyfd;

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(ttyfd, &fds);

    size_t msg_len = 0;
    size_t txlen = 0;
    int ret = 0;
    int rc = 0;

    while (true) {
        memset(rxbuf, 0, sizeof(rxbuf));
        memset(txbuf, 0, sizeof(txbuf));

        txlen = compose_ICJC(txbuf);
        tx_bd_msg(pinf, txbuf, txlen);

        rc = select(ttyfd + 1, &fds, NULL, NULL, &timeout);
        if (rc < 0) {
            iot_dbg("%s: select error, ret %d, errno %d !!\n", __FUNCTION__, ret, errno);
        } else if (rc > 0) {
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

            txlen = compose_BBDQ(txbuf);
            tx_bd_msg(pinf, txbuf, txlen);
            ret = rx_bd_msg(pinf, rxbuf, &msg_len);
            if (ret > 0) {
                if (0 == memcmp(rxbuf, "$BBXX", 5)) {
                    char* p_version = (char*)calloc(msg_len, sizeof(char));
                    if (p_version) {
                        memcpy(p_version, &(rxbuf[10]), msg_len - 11);
                        free(p_version);
                        break;
                    }
                }
            }
        }
    }
    iot_dbg("beidou is ready now.\n");
}

static int init_dpi_socket()
{
    struct sockaddr_ll socket_address;

    int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));

    if (s == -1)
    {
        perror("Socket creation failed");
        exit (0);
    }

    memset(&socket_address, 0, sizeof (socket_address));
    socket_address.sll_family = PF_PACKET;
    socket_address.sll_ifindex = if_nametoindex("lo");
    socket_address.sll_protocol = htons(ETH_P_ALL);

    if (0 > bind(s, (struct sockaddr*)&socket_address, sizeof(socket_address)))
    {
        perror("Bind");
        exit (0);
    }

    return s;
}

static void bd_rnss_listener_cb(struct uloop_timeout *t)
{
    uloop_timeout_set(t, 0);
}

static void bd_rdss_poller_cb(struct uloop_timeout *t)
{
    iot_dbg("\npolling\n");
    unsigned char txbuf[256];
    unsigned char rxbuf[256];
    size_t txlen   = 0;
    size_t msg_len = 0;
    int ret = 0;

    if (g_is_relay_data_ready) {
        txlen = compose_TXSQ(&g_bd_inf, txbuf, g_bd_relay_msg, sizeof(g_bd_relay_msg) / sizeof(g_bd_relay_msg[0]));
        tx_bd_msg(&g_bd_inf, txbuf, txlen);

        g_is_relay_data_ready = false;
        g_tx_total++;

        while (true) {
            ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
            if (ret > 0) {
                if (0 == memcmp(rxbuf, "$FKXX", 5)) {
                    if (rxbuf[10]) { // check the feedback flag
                        iot_dbg("INFO: sending fail, error code 0x%hhx\n", rxbuf[10]);
                        g_tx_fail++;
                        g_connection_status = 0;
                    } else {
                        g_tx_succ++;
                        g_connection_status = 1;
                    }
                    break;
                }
            }
        }
    }

    // update local SIM
    txlen = compose_ICJC(txbuf);
    tx_bd_msg(&g_bd_inf, txbuf, txlen);
    ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    if (ret > 0) {
        if (0 == memcmp(rxbuf, "$ICXX", 5)) {
            memcpy(g_bd_relay_msg + 2, &(rxbuf[7]), 3); // assign local user address
            uint32_t local_sim = ((rxbuf[7] << 16) | (rxbuf[8] << 8) | rxbuf[9]) & 0x1FFFFF;
            if (g_bd_inf.local_sim != local_sim) {
                g_bd_inf.local_sim = local_sim;
                iot_cfg_set_int(g_bd_inf.pcfg, IOT_BD_SEC_PM, IOT_BD_KEY_LOCAL_SIM_NO, g_bd_inf.local_sim);
                iot_cfg_sync(g_bd_inf.pcfg);
                iot_dbg("write down local_sim: %d", local_sim);
            }
        }
    }

    // update connection status and position
    txlen = compose_DWSQ_once(txbuf);
    tx_bd_msg(&g_bd_inf, txbuf, txlen);
    ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    if (ret > 0) {
        if (0 == memcmp(rxbuf, "$FKXX", 5)) {
            if (rxbuf[10]) { // check the feedback flag
                g_connection_status = 0;
            } else {
                g_connection_status = 1;

                ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
                if (ret > 0) {
                    if (0 == memcmp(rxbuf, "$DWXX", 5)) {
                        memcpy(g_DWXX, &(rxbuf[10]), 20);
                    }
                }

                //rx_nbytes(&g_bd_inf, rxbuf, 10);
                //msg_len = (rxbuf[5] << 8) | rxbuf[6];
                //rx_nbytes(&g_bd_inf, rxbuf + 10, msg_len - 10);
                //if (0 == memcmp(rxbuf, "$DWXX", 5)) {
                //    memcpy(g_DWXX, &(rxbuf[10]), 20);
                //}
            }
        }
    }

    // update signal strength ($XTZJ/$ZJXX)
    txlen = compose_XTZJ(txbuf, 0);
    tx_bd_msg(&g_bd_inf, txbuf, txlen);
    ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    if (ret > 0) {
        if (0 == memcmp(rxbuf, "$ZJXX", 5)) {
            memcpy(g_ZJXX, &(rxbuf[10]), sizeof(g_ZJXX));
        }
    }

    // update time ($SJSC/$SJXX)
#if 0
    txlen = compose_SJSC(txbuf, 0);
    tx_bd_msg(&g_bd_inf, txbuf, txlen);
    ret = rx_bd_msg(&g_bd_inf, rxbuf, &msg_len);
    if (ret > 0) {
        if (0 == memcmp(rxbuf, "$SJXX", 5)) {
            memcpy(g_SJXX, &(rxbuf[10]), sizeof(g_SJXX));
        }
    }
#endif

    uloop_timeout_set(t, 3000);
}

static void bd_relayer_cb(struct uloop_timeout *t)
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
    //FD_SET(g_bd_inf.ttyfd, &fds);
    FD_SET(g_sock, &fds);
    //fd_max = (g_sock > g_bd_inf.ttyfd) ? g_sock : g_bd_inf.ttyfd;

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
                uint8_t tmp[1600];

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
                        g_is_relay_data_ready = true;
                        iot_cfg_sync(g_bd_inf.pcfg);
                    }
                }
            }
        }
    }

    uloop_timeout_set(t, 0);
}

#if 0
            if (ret == pinf->ttyfd) {
                rx_nbytes(pinf, rxbuf, 22);
                iot_logbuf("received: ", rxbuf, 22);

                sleep(1);
                tcflush(pinf->ttyfd, TCIOFLUSH);

                txlen = compose_TXSQ(pinf, txbuf, content, sizeof(content) / sizeof(content[0]));
                write(pinf->ttyfd, txbuf, txlen);
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
    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n", q->stopped, list_empty(&q->tasks_inactive.list), list_empty(&q->tasks_active.list), q->running_tasks, q->empty, t->queued);
    runqueue_task_add(q, t, false);
	runqueue_process_cancel_cb(q, t, type);
}

static void q_relay_complete(struct runqueue *q, struct runqueue_task *t)
{
    struct relayer *r = container_of(t, struct relayer, proc.task);
	iot_dbg("[%d/%d] finish relay\n", q->running_tasks, q->max_running_tasks);

    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n", q->stopped, list_empty(&q->tasks_inactive.list), list_empty(&q->tasks_active.list), q->running_tasks, q->empty, t->queued);
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

static void add_relayer_task()
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
    //FD_SET(pinf->ttyfd, &fds);
    //FD_SET(s, &fds);
    //fd_max = (s > pinf->ttyfd) ? s : pinf->ttyfd;

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

    iot_dbg("stopped %u empty inact %u empty act %u running %u empty %u queued %u\n", q.stopped, list_empty(&q.tasks_inactive.list), list_empty(&q.tasks_active.list), q.running_tasks, q.empty, &r->proc.task.queued);
	runqueue_task_add(&q, &r->proc.task, false);
}

int main(int argc, char **argv)
{
    int pid_fd = -1;
    int ret = 0;
    const char *ubus_socket = NULL;
    
    if (argc == 2 && !(strcmp(argv[1], "-d"))) {
        g_dbg_enabled = 1;
    }

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

    wait_bd_ready(&g_bd_inf);

    g_sock = init_dpi_socket();

    uloop_init();

    ctx = ubus_connect(ubus_socket);
    if (!ctx) {
        fprintf(stderr, "Failed to connect to ubus\n");
        return -1;
    }

    ubus_add_uloop(ctx);

    // add methods
    ret = ubus_add_object(ctx, &zl100mt_object);
    if (ret)
        fprintf(stderr, "Failed to add object: %s\n", ubus_strerror(ret));

    // listen on 0xBDBD messages
    //struct uloop_timeout relayer_timeout = {
    //    .cb = bd_relayer_cb
    //};
    //uloop_timeout_set(&relayer_timeout, 0);

    // RDSS: poll beidou status and send relayed messages out
    struct uloop_timeout rdss_poller_timeout = {
        .cb = bd_rdss_poller_cb
    };
    uloop_timeout_set(&rdss_poller_timeout, 0);

    // RNSS: listen messages
    //struct uloop_timeout rnss_listener_timeout = {
    //    .cb = bd_rnss_listener_cb
    //};
    //uloop_timeout_set(&rnss_listener_timeout, 0);

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
