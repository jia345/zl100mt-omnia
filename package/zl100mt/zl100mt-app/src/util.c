#include <sys/time.h>
#include "util.h"

bool is_timer_expired(struct timeval *start, uint32_t ms) {
    struct timeval now;
    gettimeofday(&now, NULL);
    double now_ms = now.tv_sec * 1000 + now.tv_usec / 1000;
    double start_ms = start->tv_sec * 1000 + start->tv_usec / 1000;
    return (now_ms - start_ms) > ms;
}

void hexdump(int pri, const char * desc, const void * addr, const int len) {
    int i;
    unsigned char buff[17];
    const unsigned char * pc = (const unsigned char *)addr;

    // Output description if given.
    if (desc != NULL)
        ulog(pri, "%s\n", desc);

    // Length checks.
    if (len == 0) {
        ulog(pri, "  ZERO LENGTH\n");
        return;
    }
    else if (len < 0) {
        ulog(pri, "  NEGATIVE LENGTH: %d\n", len);
        return;
    }

    // Process every byte in the data.
    for (i = 0; i < len; i++) {
        // Multiple of 16 means new line (with line offset).
        if ((i % 16) == 0) {
            // Don't print ASCII buffer for the "zeroth" line.
            if (i != 0) ulog(pri, "  %s\n", buff);
            // Output the offset.
            ulog(pri, "  %04x ", i);
        }

        // Now the hex code for the specific character.
        ulog(pri, " %02x", pc[i]);

        // And buffer a printable ASCII character for later.

        if ((pc[i] < 0x20) || (pc[i] > 0x7e)) // isprint() may be better.
            buff[i % 16] = '.';
        else
            buff[i % 16] = pc[i];
        buff[(i % 16) + 1] = '\0';
    }

    // Pad out last line if not exactly 16 characters.
    while ((i % 16) != 0) {
        ulog(pri, "   ");
        i++;
    }
    // And print the final ASCII buffer.
    ulog(pri, "  %s\n", buff);
}

/* params:
 *  str: string which is end with '\0'
 *  buf: data buffer for RNSS message
 *  buf_size: size of data buffer
 * return:
 *  pointer to the first str found
 */
char* find_str_in_buffer(const char* str, const char* buf, size_t buf_size)
{
    uint32_t str_len = strlen(str);
    char* cursor = buf;

    while (cursor < (buf + buf_size - str_len)) {
        if (0 == memcmp(cursor, str, str_len)) {
            return cursor;
        }
        cursor += 1;
    }

    return NULL;
}

