#include <stdio.h>
#include <unistd.h>
#include <ftdi.h>

int main(int argc, char **argv)
{
    struct ftdi_context ftdic;
    char buf[1];
    int f,i;

    if (ftdi_init(&ftdic) < 0)
    {
        fprintf(stderr, "ftdi_init failed\n");
        return EXIT_FAILURE;
    }

    ftdi_set_interface(&ftdic, INTERFACE_B);
    f = ftdi_usb_open(&ftdic, 0x0403, 0x6011);
    if (f < 0 && f != -5)
    {
        fprintf(stderr, "unable to open ftdi device: %d (%s)\n", f, ftdi_get_error_string(&ftdic));
        exit(-1);
    }
    //ftdi_set_bitmode(&ftdic, 0xFF, BITMODE_MPSSE);
    ftdi_set_bitmode(&ftdic, 0xFF, BITMODE_BITBANG);

    // Write data
    for (i = 0; i < 5; i++)
    {
        buf[0] = 0x0;
        f = ftdi_read_data(&ftdic, buf, 1);
        if (f < 0)
            fprintf(stderr,"read failed on channel 1 for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(&ftdic));
        printf("read: %02i: 0x%02x \n",i,buf[0]);

        buf[0] = 0x0;
        printf("porta: %02i: 0x%02x \n",i,buf[0]);
        f = ftdi_write_data(&ftdic, buf, 1);
        if (f < 0)
            fprintf(stderr,"write failed on channel 1 for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(&ftdic));
        sleep(1);

        buf[0] = 0x0;
        f = ftdi_read_data(&ftdic, buf, 1);
        if (f < 0)
            fprintf(stderr,"read failed on channel 1 for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(&ftdic));
        printf("read: %02i: 0x%02x \n",i,buf[0]);

        buf[0] = 0xf0;
        printf("porta: %02i: 0x%02x \n",i,buf[0]);
        f = ftdi_write_data(&ftdic, buf, 1);
        if (f < 0)
            fprintf(stderr,"write failed on channel 1 for 0x%x, error %d (%s)\n", buf[0], f, ftdi_get_error_string(&ftdic));
        sleep(1);
    }
    printf("\n");

    ftdi_disable_bitbang(&ftdic);
    ftdi_usb_close(&ftdic);
    ftdi_deinit(&ftdic);
}
