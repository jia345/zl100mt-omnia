#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "rdss.h"

static void pack_addr(char *buf, uint32_t no)
{
    buf[0] = (uint8_t)((no & 0xFF0000) >> 16);
    buf[1] = (uint8_t)((no & 0x00FF00) >> 8);
    buf[2] = (uint8_t)( no & 0x0000FF);
}

static void pack_uint16(char *buf, uint16_t u16)
{
    buf[0] = (uint8_t)(u16 >> 8);
    buf[1] = (uint8_t)(u16 & 0xFF);
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 |
 * |    |    |    |    |    |         |              |    |    |
 * |----+----+----+----+----+---------+--------------+----+----|
 * |    |    |    |    |    |         |              |    |    |
 * | $  | G  | L  | J  | C  | bytelen |  user number |freq|crc |
 */
ssize_t compose_rdss_gljc_pdu(char *buf, size_t buf_size, uint16_t freq)
{
    int len = 12;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$GLJC", 5);
    buf[6] = len;
    buf[10] = freq;

    int i = 0;
    for (; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

/*
 * | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |
 * |    |    |    |    |    |         |              |    |                   |                   |         |    |
 * |----+----+----+----+----+---------+--------------+----+--------------+----+--------------+----+---------+----|
 * |    |    |    |    |    |         |              |    |                   |                   |         |    |
 * | $  | D  | W  | S  | Q  | bytelen |  my  number  |type| altitude & antenna|   air pressure    |   freq  |crc |
 */
ssize_t compose_rdss_dwsq_pdu(char *buf, size_t buf_size, uint16_t freq)
{
    int len = 22;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$DWSQ", 5);
    buf[6] = len;
    buf[10] = 4; // b 0000 0100
    pack_uint16(&(buf[19]), freq & 0xFFFF);

    int i = 0;
    for (; i < len - 1; i++) {
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
ssize_t compose_rdss_txsq_pdu(char * buf, size_t buf_size, const rdss_msg_txsq_t* msg)
{
    uint16_t bitlen = msg->data_len << 3;
    uint16_t totalbytelen = msg->data_len + 18;

    if (buf_size < totalbytelen) return -1;

    memcpy(buf, "$TXSQ", 5);
    pack_uint16(&(buf[5]), totalbytelen);
    pack_addr(&(buf[7]), msg->local_sim);
    buf[10] = 0x46; // BCD code
    pack_addr(&(buf[11]), msg->target_sim);
    pack_uint16(&(buf[14]), bitlen);
    buf[16] = 0;
    memcpy(&(buf[17]), msg->data, msg->data_len);
    buf[totalbytelen - 1] = buf[0];

    uint16_t i = 1;
    for (; i < (totalbytelen - 1); i++) {
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
ssize_t compose_rdss_cksc_pdu(char *buf, size_t buf_size, uint8_t rate)
{
    int len = 12;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$CKSC", 5);
    buf[6] = len;
    buf[10] = rate;

    int i = 0;
    for (; i < len - 1; i++) {
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
ssize_t compose_rdss_icjc_pdu(char *buf, size_t buf_size)
{
    int len = 12;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$ICJC", 5);
    buf[6] = len;

    int i = 0;
    for (; i < len - 1; i++) {
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
ssize_t compose_rdss_xtzj_pdu(char *buf, size_t buf_size, uint16_t cycle_s)
{
    int len = 13;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$XTZJ", 5);
    buf[6] = len;
    buf[10] = (cycle_s & 0xFF00) >> 8;
    buf[11] = cycle_s & 0xFF;

    int i = 0;
    for (; i < len - 1; i++) {
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
ssize_t compose_SJSC(char *buf, size_t buf_size, uint16_t cycle_s)
{
    int len = 13;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$SJSC", 5);
    buf[6] = len;
    buf[10] = (cycle_s & 0xFF00) >> 8;
    buf[11] = cycle_s & 0xFF;

    int i = 0;
    for (; i < len - 1; i++) {
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
ssize_t compose_rdss_bbdq_pdu(char *buf, size_t buf_size)
{
    int len = 11;

    if (buf_size < len) return -1;

    memset(buf, 0, len);
    memcpy(buf, "$BBDQ", 5);
    buf[6] = len;

    int i = 0;
    for (; i < len - 1; i++) {
        buf[len - 1] = buf[len - 1] ^ buf[i];
    }

    return len;
}

