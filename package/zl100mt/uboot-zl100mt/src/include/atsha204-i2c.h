/* -*- mode: c; c-file-style: "linux" -*- */
/*
 * I2C Driver for Atmel ATSHA204 over I2C
 *
 * Copyright (C) 2014 Josh Datko, Cryptotronix, jbd@cryptotronix.com
 *
 * This program is free software; you can redistribute  it and/or modify it
 * under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#ifndef _ATSHA204_I2C_H_
#define _ATSHA204_I2C_H_


#define ATSHA204_CONF_REG_SELECT 0
#define ATSHA204_OTP_REG_SELECT 1


struct atsha204_buffer {
    u8 *ptr;
    int len;
};


/* I2C detection */
int atsha204_test(void);
int atsha204_reset(void);

/* atsha204 specific functions */
int atsha204_wakeup(void);
int atsha204_idle(void);
int atsha204_sleep(void);
int atsha204_transaction(const u8* to_send, size_t to_send_len,
                             struct atsha204_buffer *buf);
int atsha204_get_random(u8 *to_fill, const size_t max);
int atsha204_read4(u8 *read_buf, const u16 addr, const u8 param1);

int atsha204_dump_region(u8 param1, int size);
int atsha204_dump_config(void);
int atsha204_dump_otp(void);
int atsha204_get_sn(u8 *sn);
int atsha204_is_locked(const int offset);
int atsha204_is_config_locked(void);
int atsha204_is_data_locked(void);

#endif /* _ATSHA204_I2C_H_ */
