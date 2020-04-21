#ifndef _RDSS_H_
#define _RDSS_H_

#define RDSS_BUF_SIZE 1024
#define RDSS_MAX_RETRY 3

#include <sys/types.h>

typedef struct {
    char buf[RDSS_BUF_SIZE];
    char* raw_cursor; // pointer to free space
    char* pdu_cursor; // pointer to first unhandled message
    size_t rest_size;
} rdss_buffer_t;

#if 0
typedef struct {
    const char* cmd_str;
    uint32_t addr;
    size_t data_len;
    char content[256];
    struct timeval ts;
} rdss_msg_t;
#endif

typedef enum {
    RDSS_GLJC,
    RDSS_DWSQ,
    RDSS_TXSQ,
    RDSS_CKSC,
    RDSS_ICJC,
    RDSS_XTZJ,
    RDSS_LZSZ,
    RDSS_LZDQ,
    RDSS_SJSC,
    RDSS_BBDQ,
    RDSS_BBXX,
    RDSS_GLZK,
    RDSS_DWXX,
    RDSS_TXXX,
    RDSS_ICXX,
    RDSS_ZJXX,
    RDSS_LZXX,
    RDSS_SJXX,
    RDSS_FKXX,
    RDSS_PDU_TYPE_MAX
} eRdssPduType;

typedef struct {
    eRdssPduType type;
    const char* name;
} rdss_pdu_type_t;

static const rdss_pdu_type_t g_rdss_pdu_type_list[] = {
    {
        .type = RDSS_DWSQ,
        .name = "$DWSQ",
    },
    {
        .type = RDSS_TXSQ,
        .name = "$TXSQ",
    },
    {
        .type = RDSS_CKSC,
        .name = "$CKSC",
    },
    {
        .type = RDSS_ICJC,
        .name = "$ICJC",
    },
    {
        .type = RDSS_XTZJ,
        .name = "$XTZJ",
    },
    {
        .type = RDSS_SJSC,
        .name = "$SJSC",
    },
    {
        .type = RDSS_BBDQ,
        .name = "$BBDQ",
    },
    {
        .type = RDSS_GLJC,
        .name = "$GLJC",
    },
    {
        .type = RDSS_DWXX,
        .name = "$DWXX",
    },
    {
        .type = RDSS_TXXX,
        .name = "$TXXX",
    },
    {
        .type = RDSS_FKXX,
        .name = "$FKXX",
    },
    {
        .type = RDSS_ICXX,
        .name = "$ICXX",
    },
    {
        .type = RDSS_ZJXX,
        .name = "$ZJXX",
    },
    {
        .type = RDSS_SJXX,
        .name = "$SJXX",
    },
    {
        .type = RDSS_BBXX,
        .name = "$BBXX",
    },
    {
        .type = RDSS_GLZK,
        .name = "$GLZK",
    }
};

typedef struct {
    uint32_t local_sim;
    uint32_t target_sim;
    uint8_t trans_type;
    uint8_t need_ack;
    char data[256];
    size_t data_len;
} rdss_msg_txsq_t;

ssize_t compose_rdss_dwsq_pdu(char *buf, size_t buf_size, uint16_t freq);
ssize_t compose_rdss_txsq_pdu(char * buf, size_t buf_size, const rdss_msg_txsq_t* msg);
ssize_t compose_rdss_cksc_pdu(char *buf, size_t buf_size, uint8_t rate);
ssize_t compose_rdss_gljc_pdu(char *buf, size_t buf_size, uint16_t freq);
ssize_t compose_rdss_icjc_pdu(char *buf, size_t buf_size);
ssize_t compose_rdss_xtzj_pdu(char *buf, size_t buf_size, uint16_t freq);
ssize_t compose_rdss_sjsc_pdu(char *buf, size_t buf_size, uint16_t freq);
ssize_t compose_rdss_bbdq_pdu(char *buf, size_t buf_size);

#endif
