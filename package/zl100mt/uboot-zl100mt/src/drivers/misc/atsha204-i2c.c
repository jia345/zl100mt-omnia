/*
* I2C Driver for Atmel ATSHA204
*
* Copyright (C) 2014 Josh Datko, Cryptotronix, jbd@cryptotronix.com
* Copyright (C) 2016 Tomas Hlavacek, CZ.NIC, tmshlvck@gmail.com
*
* This program is free software; you can redistribute  it and/or modify it
* under the terms of the GNU General Public License version 2 as
* published by the Free Software Foundation.
*/

/* #define DEBUG */

#include <common.h>
#include <i2c.h>
#include <errno.h>

#include "atsha204-i2c.h"

#define ATSHA204_WA_SLEEP 0x01
#define ATSHA204_WA_IDLE 0x02


#define ATSHA204A_BUF_SIZE 84
#define ATSHA204A_TWLO 60
#define ATSHA204_EXECTIME 5000
#define ATSHA204_TRANSACTION_TIMEOUT 100000
#define ATSHA204_TRANSACTION_RETRY 5

#define ATSHA204_CONF_REG_SIZE 128
#define ATSHA204_OTP_REG_SIZE 64
#define ATSHA204_LOCK_ADDR 0x15
#define ATSHA204_UNLOCKED 0x55
#define CONFIG_ZONE_LOCK_OFFSET 3
#define DATA_ZONE_LOCK_OFFSET 2
#define ATSHA204_SN_LEN 12

DECLARE_GLOBAL_DATA_PTR;
extern int twsi_i2c_xfer(struct i2c_adapter *adap, struct i2c_msg *msg,
			int nmsgs);

/**
 * I2C send xfer proxy
 */
static int i2c_master_send(const u8 *buf, int count)
{
	int ret;
	struct i2c_msg msg;

	msg.addr = CONFIG_ATSHA204_ADDR;
	msg.flags |= I2C_M_STOP;
	msg.len = count;
	msg.buf = (u8 *)buf;
 
	ret = twsi_i2c_xfer(I2C_ADAP, &msg, 1);
 
	return (ret == 0) ? count : ret;
}
/**
 * I2C recv xfer proxy
 */
static int i2c_master_recv(u8 *buf, int count)
{
	struct i2c_msg msg;
	int ret;
 
	msg.addr = CONFIG_ATSHA204_ADDR;
	msg.flags |= I2C_M_RD | I2C_M_STOP;
	msg.len = count;
	msg.buf = buf;
 
	ret = twsi_i2c_xfer(I2C_ADAP, &msg, 1);

	return (ret == 0) ? count : ret;
}

/***********************************************
 * Ultra-simple hexdump
 */
#ifdef DEBUG
static void hexdump(const void * buf, size_t size)
{
  const uchar * cbuf = (const uchar *) buf;
  const unsigned int BYTES_PER_LINE = 16;
  unsigned int offset, minioffset;

  for (offset = 0; offset < size; offset += BYTES_PER_LINE)
  {
    /* OFFSETXX  xx xx xx xx xx xx xx xx  xx xx . . .
     *     . . . xx xx xx xx xx xx   abcdefghijklmnop
     */
    printf("%08x  ", (unsigned int)(cbuf+offset));
    for (minioffset = offset;
      minioffset < offset + BYTES_PER_LINE;
      minioffset++)
    {
      if (minioffset - offset == (BYTES_PER_LINE / 2)) {
        printf(" ");
      }

      if (minioffset < size) {
        printf("%02x ", cbuf[minioffset]);
      } else {
        printf("   ");
      }
    }
    printf("  ");

    for (minioffset = offset;
      minioffset < offset + BYTES_PER_LINE;
      minioffset++)
    {
      if (minioffset >= size)
        break;

      if (cbuf[minioffset] < 0x20 ||
        cbuf[minioffset] > 0x7e)
      {
        printf(".");
      } else {
        printf("%c", cbuf[minioffset]);
      }
    }
    printf("\n");
  }
}
#endif
/**********************************************/

static u16 atsha204_crc16(const u8 *buf, const u8 len)
{
	u8 i;
	u16 crc16 = 0;
	u8 shift;

	for (i = 0; i < len; i++) {
		for (shift = 0x01; shift > 0x00; shift <<= 1) {
			u8 data_bit = (buf[i] & shift) ? 1 : 0;
			u8 crc_bit = crc16 >> 15;

			crc16 <<= 1;

			if ((data_bit ^ crc_bit) != 0)
				crc16 ^= 0x8005;
		}
	}

	return cpu_to_le16(crc16);
}

static bool atsha204_crc16_matches(const u8 *buf, const u8 len, const u16 crc)
{
	u16 crc_calc = atsha204_crc16(buf,len);
	return (crc == crc_calc) ? true : false;
}

static bool atsha204_check_rsp_crc16(const u8 *buf, const u8 len)
{
	u16 rec_crc = ((buf[len - 1]<<8) | (buf[len - 2]));
	return atsha204_crc16_matches(buf, len - 2, rec_crc);
}

int atsha204_wakeup(void)
{
	u8 buf[ATSHA204A_BUF_SIZE];
	unsigned short int try;

	for (try=0; try<10; try++) {
		debug("%s: Attempting Wakeup : %u\n", __func__, try);

		memset(buf, 0, 4);
		if (4 == i2c_master_send(buf, 4)){
			debug("%s: Wakeup/reset sent.\n", __func__);
		} else {
			debug("%s: Wakeup sent failed.\n", __func__);
			continue;
		}
		udelay(ATSHA204A_TWLO);

		if (4 == i2c_master_recv(buf, 4)) {
			debug("%s: buf[0]=%d\n", __func__, buf[0]);
			if ((buf[0] > 4) && (buf[0] < sizeof(buf)-4))
				i2c_master_recv(buf+4, buf[0]-4);

			if (atsha204_check_rsp_crc16(buf, buf[0])) {
				debug("%s: Wakeup CRC OK\n", __func__);
				return 0;
			} else {
				debug("%s: Wakeup CRC failure\n", __func__);
				return -EBADMSG;
			}
		} else {
			debug("%s: Wakeup receive failure.\n", __func__);
			return -EBADMSG;
		}
	}

	debug("%s: Wakeup Failed. No Device\n", __func__);
	return -ENODEV;
}

int atsha204_idle(void)
{
        u8 to_send[1] = {ATSHA204_WA_IDLE};

	debug("%s\n", __func__);
        if (1 == i2c_master_send(to_send, 1))
		return 0;
	else
		return -EBUSY;
}

int atsha204_sleep(void)
{
	u8 to_send[1] = {ATSHA204_WA_SLEEP};

	debug("%s\n", __func__);
	if (1 == i2c_master_send(to_send, 1))
		return 0;
	else
		return -EBUSY;
}

int atsha204_transaction(const u8* to_send, size_t to_send_len,
                             struct atsha204_buffer *buf)
{
	int rc;
	u8 status_packet[4] = {0};
	int timeout = ATSHA204_TRANSACTION_TIMEOUT;

#ifdef DEBUG
	debug("%s: About to send to device.\n", __func__);
	hexdump(to_send, to_send_len);
	debug("\n\n");
#endif

	/* Send command */
	if ((rc = i2c_master_send(to_send, to_send_len))
		!= to_send_len) {
		rc = -EBUSY;
		goto out;
	}

	/* Poll for the response */
	while (4 != i2c_master_recv(status_packet, 4)
		&& timeout > 0){
		debug("%s: Polling for response. timeout=%d\n", __func__, timeout);
		timeout -= ATSHA204_EXECTIME;
		udelay(ATSHA204_EXECTIME);
	}

	if (timeout <= 0) {
		debug("%s : timeouted\n", __func__);
		rc = -ETIMEDOUT;
		goto out;
	}

	if (buf->len < status_packet[0]) {
		debug("%s : Out of memory!\n", __func__);
		rc = -ENOMEM;
		goto out;
	}

	memcpy(buf->ptr, status_packet, sizeof(status_packet));

	/* Transfer the rest of the packet */
	if (status_packet[0] > 4) {
		debug("%s: receiving rest, sp[0]=%d\n", __func__, status_packet[0]);
		if ((rc = i2c_master_recv(buf->ptr + 4, status_packet[0] - 4))
			!= status_packet[0] - 4) {
			rc = -EBADMSG;
			goto out;
		}
	}

	/* Set the true length */
	buf->len = status_packet[0];
	rc = 0;

#ifdef DEBUG
	debug("%s: Received from device len=%d.\n", __func__, status_packet[0]);
	hexdump(buf->ptr, buf->len);
	debug("\n\n");
#endif

out:
	return rc;
}


static int atsha204_validate_rsp(const struct atsha204_buffer *packet,
                              struct atsha204_buffer *rsp)
{
	int rc;

	if (packet->len < 4)
		return -EBADMSG;
	else if (atsha204_check_rsp_crc16(packet->ptr, packet->len)){
		rsp->ptr = packet->ptr + 1;
		rsp->len = packet->len - 3;
		rc = 0;
		goto out;
	} else /* CRC failed */
		rc = -EBADMSG;
out:
	return rc;
}


int atsha204_read4(u8 *read_buf, const u16 addr, const u8 param1)
{
	u8 read_cmd[8] = {0};
	u8 buf[ATSHA204A_BUF_SIZE];
	u16 crc;
	struct atsha204_buffer rsp, msg;
	int rc, validate_status, retry = ATSHA204_TRANSACTION_RETRY; 


	rsp.ptr = buf;
	rsp.len = sizeof(buf);

	read_cmd[0] = 0x03; /* Command byte */
	read_cmd[1] = 0x07; /* length */
	read_cmd[2] = 0x02; /* Read command opcode */
	read_cmd[3] = param1;
	read_cmd[4] = cpu_to_le16(addr) & 0xFF;
	read_cmd[5] = cpu_to_le16(addr) >> 8;

	crc = atsha204_crc16(&read_cmd[1], 5);
	read_cmd[6] = cpu_to_le16(crc) & 0xFF;
	read_cmd[7] = cpu_to_le16(crc) >> 8;

	while ((0 != (rc = atsha204_transaction(read_cmd, sizeof(read_cmd),
		&rsp))) && (retry>0)) {
		debug("%s: Warn: Transaction retry. retry=%d\n", __func__, retry);
		atsha204_wakeup();
		retry--;
	}

	if (0 == rc){
		if ((validate_status = atsha204_validate_rsp(&rsp, &msg)) == 0){
			if (msg.len == 1) {
				rc = -EBADMSG;
				debug("%s: error %d while reading\n", __func__, msg.ptr[0]);
			} else {
				memcpy(read_buf, msg.ptr, msg.len);
				rc = 0;
				debug("%s: valid message len=%d\n", __func__, msg.len);
			}
		} else {
			debug("%s: validation failed status=%d\n", __func__, validate_status);
			rc = validate_status;
		}
	} else {
		debug("%s: transaction failed rc=%d\n", __func__, rc);
		rc = -EBADMSG;
	}

	return rc;
}



int atsha204_get_random(u8 *to_fill, const size_t max)
{
	int rc;
	u8 buf[ATSHA204A_BUF_SIZE];
	struct atsha204_buffer recv = {buf,sizeof(buf)};
	int rnd_len;

	const u8 rand_cmd[] = {0x03, 0x07, 0x1b, 0x01, 0x00, 0x00, 0x27, 0x47};

	rc = atsha204_transaction(rand_cmd, sizeof(rand_cmd), &recv);
	if (0 == rc){

		if (!atsha204_check_rsp_crc16(recv.ptr, recv.len)){
			rc = -EBADMSG;
			debug("%s: Bad CRC on Random\n", __func__);
		} else{
			debug("%s: CRC on Random OK\n", __func__);
			rnd_len = (max > recv.len - 3) ? recv.len - 3 : max;
			memcpy(to_fill, &recv.ptr[1], rnd_len);
			rc = rnd_len;
			debug("%s: Returning randoom bytes %d\n", __func__, rc);
		}
	}

	return rc;
}























int atsha204_dump_region(u8 param1, int size)
{
	int i;
	u16 bytes = 0;
	u8 zone[size];

	memset(zone, 0, size);

	if(atsha204_wakeup() != 0)
		return 0;

	for (bytes = 0; bytes < size; bytes += 4){
		if (0 != atsha204_read4(&zone[bytes],
				bytes / 4, param1)){
			break;
		}
	}

	for (i = 0; i < bytes; i++) {
		printf("%02X ", zone[i]);
		if ((i + 1) % 4 == 0)
			printf("\n");
	}

	atsha204_idle();
	return bytes;
}

int atsha204_dump_config(void)
{
	return atsha204_dump_region(ATSHA204_CONF_REG_SELECT,
					ATSHA204_CONF_REG_SIZE);
}

int atsha204_dump_otp(void)
{
	return atsha204_dump_region(ATSHA204_OTP_REG_SELECT,
					ATSHA204_OTP_REG_SIZE);
}



int atsha204_get_sn(u8 *sn)
{
	/* SN is 12 bytes long, use ATSHA204_SN_LEN */
	u16 bytes;
	int result = 0;

	if(atsha204_wakeup() != 0)
		return -EBUSY;

	for (bytes = 0; bytes < ATSHA204_SN_LEN; bytes += 4){
		if (0 != atsha204_read4(&sn[bytes],
			(bytes / 4), ATSHA204_CONF_REG_SELECT)) {
			result = -EBADMSG;
			goto out;
		}
	}

out:
	atsha204_idle();
	return result;
}


int atsha204_is_locked(const int offset)
{
	u8 lock_buf[4];
	int locked = 1;

	if(atsha204_wakeup() != 0)
		return -EBUSY;

	if (0 != atsha204_read4(lock_buf,
		ATSHA204_LOCK_ADDR, ATSHA204_CONF_REG_SELECT )) {
		locked = -EBADMSG;
		goto out;
	}

	if (ATSHA204_UNLOCKED == lock_buf[offset])
		locked = 0;
	else
		locked = 1;

out:
	atsha204_idle();
	return locked;
}

int atsha204_is_config_locked(void)
{
	return atsha204_is_locked(CONFIG_ZONE_LOCK_OFFSET);
}

int atsha204_is_data_locked(void)
{
	return atsha204_is_locked(DATA_ZONE_LOCK_OFFSET);
}

int atsha204_test(void)
{
	int result = -ENODEV;
#ifdef DEBUG
	u8 sn[ATSHA204_SN_LEN];
	int i;
	u8 rnd[32];
#endif

	if((result = atsha204_wakeup()) != 0) {
		printf("%s: ATSHA204 device failed to wake: 0x%x\n", __func__,
			CONFIG_ATSHA204_ADDR);
		goto out;
	}

	printf("Found ATSHA204 at addr 0x%x\n", CONFIG_ATSHA204_ADDR);
	printf("ATSHA204 data_locked=%d config_locked=%d\n",
		atsha204_is_data_locked(), atsha204_is_config_locked());

#ifdef DEBUG
	printf("ATSHA204 SN: ");
	if ((result = atsha204_get_sn(sn)) < 0)
		goto out;
	for (i = 0; i < sizeof(sn); i++)
		printf("%02X", sn[i]);
	printf("\n");

	/* Tests */
	printf("ATSHA204 random:\n");
	atsha204_wakeup();
	result = atsha204_get_random(rnd, sizeof(rnd));
	for(i=0; i<result; i++) {
		printf("%02X ", rnd[i]);
		if(((i+1) % 16) == 0)
			printf("\n");
	}
	printf("\n");

	printf("ATSHA204 config region:\n");
	atsha204_dump_config();
	printf("ATSHA204 OTP region:\n");
	atsha204_dump_otp();

	result = 0;
#endif

out:
	atsha204_idle();
        return result;
}

int atsha204_reset()
{
	atsha204_wakeup();
	atsha204_sleep();

	return 0;
}

