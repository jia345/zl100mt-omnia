#include <sys/time.h>
#include <syslog.h>
#include <string.h>
#include <stdio.h>

#include "util.h"

bool is_timer_expired(struct timeval *start, uint32_t ms) {
    struct timeval now;
    gettimeofday(&now, NULL);
    double now_ms = now.tv_sec * 1000 + now.tv_usec / 1000;
    double start_ms = start->tv_sec * 1000 + start->tv_usec / 1000;
    return (now_ms - start_ms) > ms;
}

#if 0
void hexdump(int pri, const char * desc, const void * addr, const int len) {
    int i;
    unsigned char buff[17];
    const unsigned char * pc = (const unsigned char *)addr;

    // Output description if given.
    if (desc != NULL)
        syslog(pri, "%s\n", desc);

    // Length checks.
    if (len == 0) {
        syslog(pri, "  ZERO LENGTH\n");
        return;
    }
    else if (len < 0) {
        syslog(pri, "  NEGATIVE LENGTH: %d\n", len);
        return;
    }

    // Process every byte in the data.
    for (i = 0; i < len; i++) {
        // Multiple of 16 means new line (with line offset).
        if ((i % 16) == 0) {
            // Don't print ASCII buffer for the "zeroth" line.
            if (i != 0) syslog(pri, "  %s\n", buff);
            // Output the offset.
            syslog(pri, "  %04x ", i);
        }

        // Now the hex code for the specific character.
        syslog(pri, " %02x", pc[i]);

        // And buffer a printable ASCII character for later.

        if ((pc[i] < 0x20) || (pc[i] > 0x7e)) // isprint() may be better.
            buff[i % 16] = '.';
        else
            buff[i % 16] = pc[i];
        buff[(i % 16) + 1] = '\0';
    }

    // Pad out last line if not exactly 16 characters.
    while ((i % 16) != 0) {
        syslog(pri, "   ");
        i++;
    }
    // And print the final ASCII buffer.
    syslog(pri, "  %s\n", buff);
}
#else
void hexdump(int pri, const char * desc, const void * addr, const int len) {
    int i;
    char out_buff[2048];
    memset(out_buff, 0, 2048);

    char buff[17] = {0};
    const unsigned char * pc = (const unsigned char *)addr;
    int out_len = 0;
    char* tmp = out_buff;

    // Output description if given.
    if (desc != NULL)
        out_len = sprintf(tmp, "%s\n", desc);

    tmp += out_len;

    // Length checks.
    if (len == 0) {
        out_len = sprintf(tmp, "  ZERO LENGTH\n");
        syslog(pri, "  %s\n", out_buff);
        return;
    } else if (len < 0) {
        out_len = sprintf(tmp, "  NEGATIVE LENGTH: %d\n", len);
        syslog(pri, "  %s\n", out_buff);
        return;
    }

    // Process every byte in the data.
    for (i = 0; i < len; i++) {
        // Multiple of 16 means new line (with line offset).
        if ((i % 16) == 0) {
            // Don't print ASCII buffer for the "zeroth" line.
            if (i != 0) {
                out_len = sprintf(tmp, "  %s\n", buff);
                tmp += out_len;
            }
            // Output the offset.
            out_len = sprintf(tmp, "  %04x ", i);
            tmp += out_len;
        }

        // Now the hex code for the specific character.
        out_len = sprintf(tmp, " %02x", pc[i]);
        tmp += out_len;

        // And buffer a printable ASCII character for later.

        if ((pc[i] < 0x20) || (pc[i] > 0x7e)) // isprint() may be better.
            buff[i % 16] = '.';
        else
            buff[i % 16] = pc[i];
        buff[(i % 16) + 1] = '\0';
    }

    // Pad out last line if not exactly 16 characters.
    while ((i % 16) != 0) {
        out_len = sprintf(tmp, "   ");
        tmp += out_len;
        i++;
    }
    // And print the final ASCII buffer.
    out_len = sprintf(tmp, "  %s\n", buff);
    syslog(pri, "  %s\n", out_buff);
}
#endif

/* params:
 *  str: string which is end with '\0'
 *  buf: data buffer for RNSS message
 *  buf_size: size of data buffer
 * return:
 *  pointer to the first str found
 */
const char* find_str_in_buffer(const char* str, const char* buf, size_t buf_size)
{
    int32_t str_len = strlen(str);
    const char* cursor = buf;

    while (cursor < (buf + buf_size - str_len)) {
        if (0 == memcmp(cursor, str, str_len)) {
            return cursor;
        }
        cursor += 1;
    }

    return NULL;
}

