#ifndef _UTIL_H_
#define _UTIL_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

bool is_timer_expired(struct timeval *start, uint32_t ms);
void hexdump(int pri, const char * desc, const void * addr, const int len);
const char* find_str_in_buffer(const char* str, const char* buf, size_t buf_size);

#endif
