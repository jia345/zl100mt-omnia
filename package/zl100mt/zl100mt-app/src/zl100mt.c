
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

#include "zl100mt.h"

static int s    = -1;
int g_cancelled = 0;

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
    pinf->ttypath     =          iot_cfg_get_str(pinf->pcfg, IOT_BD_SEC_GENERAL, IOT_BD_KEY_TTY,    NULL);
    pinf->ttybaudrate = (int32_t)iot_cfg_get_int(pinf->pcfg, IOT_BD_SEC_GENERAL, IOT_BD_KEY_BDRATE, 0);
    pinf->remoteno    = (int32_t)iot_cfg_get_int(pinf->pcfg, IOT_BD_SEC_REMOTE,  IOT_BD_KEY_NUMBER, 0);
    pinf->is_dryrun   = (int32_t)iot_cfg_get_int(pinf->pcfg, IOT_BD_SEC_DEBUG,   IOT_BD_KEY_DRYRUN, 0);

    if (    (NULL == pinf->ttypath)
         || (   0 == pinf->remoteno)
         || (   0 == pinf->ttybaudrate)
       )
    {
        goto out;
    }
    iot_inf("Configuration:");
    iot_inf("\tttypath       = %s", pinf->ttypath);
    iot_inf("\tbaudrate      = %d", pinf->ttybaudrate);
    iot_inf("\tremote number = %d", pinf->remoteno);

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
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | ....... | n |
 * |    |    |    |    |    |         |              |    |              |         |    |         |   |
 * |----+----+----+----+----+---------+--------------+----+--------------+---------+----+---------+---|
 * |    |    |    |    |    |         |              |    |              |         |    |         |   |
 * | $  | T  | X  | S  | Q  | bytelen |  my  number  |type| remote number| bit len |ACK?| content |crc|
 */
static uint16_t compose_txsq(BD_INFO *pinf, unsigned char *buf, unsigned char *content, uint16_t bytelen)
{
    uint16_t bitlen = bytelen << 3;
    uint16_t totalbytelen = bytelen + 18;
    uint16_t i;

    memcpy(buf, "$TXSQ", 5);
    pack_uint16(&(buf[5]), totalbytelen);
    pack_no(&(buf[7]), pinf->myno);
    buf[10] = 0x46;
    pack_no(&(buf[11]), pinf->remoteno);
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
 * | $  | I  | C  | J  | C  | bytelen | my number(0) |  0 | crc|
 */
static void compose_icjc(unsigned char *buf)
{
    int i;
    memset(buf, 0, 12);
    memcpy(buf, "$ICJC", 5);
    buf[6] = 12;
    buf[11] = buf[0];
    for (i = 1; i <= 6; i++) {
        buf[11] = buf[11] ^ buf[i];
    }
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
            break;
        }
    }

    return ret;
}

static void mainloop(BD_INFO *pinf)
{
    unsigned char txbuf[100];
    unsigned char rxbuf[100];
    uint16_t txlen;
    uint8_t content[] = {
        0xBD, 0xBD,
        0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC,
        0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xA5,
        0xA7, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xA5, 0xA6,
        0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xA5, 0xA6, 0xA7,
    };

    unsigned char buf_ip[1600];
    struct iphdr* p_iphdr   = NULL;
    struct tcphdr* p_tcphdr = NULL;
    size_t iphdr_offset     = 0;
    size_t tcphdr_offset    = 0;
    size_t tcpdata_offset   = 0;
    ssize_t recv_size       = -1;

    int i = 0;
    int fd_max;

    struct sockaddr_ll socket_address;

    s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(pinf->ttyfd, &fds);
    FD_SET(s, &fds);
    fd_max = (s > pinf->ttyfd) ? s : pinf->ttyfd;

    if (s == -1)
    {
        perror("Socket creation failed");
        exit (0);
    }

    memset(&socket_address, 0, sizeof (socket_address));
    socket_address.sll_family = PF_PACKET;
    socket_address.sll_ifindex = if_nametoindex("lo");
    socket_address.sll_protocol = htons(ETH_P_ALL);

    i = bind(s, (struct sockaddr*)&socket_address, sizeof(socket_address));
    if (i == -1)
    {
        perror("Bind");
        exit (0);
    }

    while (!g_cancelled) {
        memset(&buf_ip, 0, sizeof(buf_ip));

        recv_size = recv(s, &buf_ip, sizeof(buf_ip), 0);
        if (recv_size == -1)
        {
            perror("Socket receive");
            exit (0);
        }

        iphdr_offset = sizeof(struct ethhdr);
        p_iphdr      = (struct iphdr*)(buf_ip + iphdr_offset);

        /*
         * only print the TCP packets which have 0xBDBD at first two payload bytes
         */
        if (p_iphdr->protocol == IPPROTO_TCP)
        {
            tcphdr_offset  = iphdr_offset + (p_iphdr->ihl * 4);
            p_tcphdr       = (struct tcphdr*)(buf_ip + tcphdr_offset);
            tcpdata_offset = tcphdr_offset + p_tcphdr->th_off * 4;

            unsigned char* p_tcpdata = buf_ip + tcpdata_offset;

            if (p_tcpdata[0] == 0xbd && p_tcpdata[1] == 0xbd)
            {
                printf("\n* %s -> %s (IP packet)", \
                        inet_ntoa(*((struct in_addr *)&(p_iphdr->saddr))), \
            		inet_ntoa(*((struct in_addr *)&(p_iphdr->daddr))));
                for(i = 0; i < recv_size - iphdr_offset; i++)
                {
                    if (i%16 == 0)
                    {
                        printf("\n0x%04hhx: ", i);
                    }
                    printf("%02hhX ", buf_ip[i + iphdr_offset]);
                }
            }
            printf("\n");
        }

        compose_icjc(txbuf);
        write(pinf->ttyfd, txbuf, 12);
        rx_nbytes(pinf, rxbuf, 22);
        iot_logbuf("received: ", rxbuf, 22);

        sleep(1);
        tcflush(pinf->ttyfd, TCIOFLUSH);

        txlen = compose_txsq(pinf, txbuf, content, sizeof(content) / sizeof(content[0]));
        write(pinf->ttyfd, txbuf, txlen);
        rx_nbytes(pinf, rxbuf, 16);
        iot_logbuf("received: ", rxbuf, 16);
        rx_nbytes(pinf, rxbuf, 54);
        iot_logbuf("received: ", rxbuf, 54);
        break;
    }
    close(s);
}

int main (int argc, char *argv[])
{
    int pid_fd = -1;
    int ret = 0;
    BD_INFO *pinf = &g_bd_inf;

#if !(BD_DBG)
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
#endif
    iot_inf("Starting bdrelay...");

    set_sighandler();

    if (init_bdinf(pinf)) {
        goto out;
    }

    mainloop(pinf);

out:
    g_cancelled = 1;
    if (pid_fd >= 0) {
        unlink(IOT_BD_PID_PATH);
        close(pid_fd);
        pid_fd = -1;
    }

    return 0;
}
