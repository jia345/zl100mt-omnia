#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

static int s = -1;

void onexit(int signum)
{
    (void)signum;
    printf("Exiting");
    close(s);
}

int main()
{
    unsigned char buf[1600];
    struct iphdr* p_iphdr = NULL;
    struct tcphdr* p_tcphdr = NULL;
    size_t iphdr_offset = 0;
    size_t tcphdr_offset = 0;
    size_t tcpdata_offset = 0;

    ssize_t recv_size = -1;

    int i = 0;

    struct sockaddr_ll socket_address;

    s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IP));

    if (s == -1)
    {
        perror("Socket creation failed");
        exit (0);
    }

    signal(SIGINT, onexit);

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

    while (1)
    {
        memset(&buf, 0, sizeof(buf));

        recv_size = recv(s, &buf, sizeof(buf), 0);
        if (recv_size == -1)
        {
            perror("Socket receive");
            exit (0);
        }

        iphdr_offset = sizeof(struct ethhdr);
        p_iphdr      = (struct iphdr*)(buf + iphdr_offset);

        /*
         * only print the TCP packets which have 0xBDBD at first two payload bytes
         */
        if (p_iphdr->protocol == IPPROTO_TCP)
        {
            tcphdr_offset  = iphdr_offset + (p_iphdr->ihl * 4);
            p_tcphdr       = (struct tcphdr*)(buf + tcphdr_offset);
            tcpdata_offset = tcphdr_offset + p_tcphdr->th_off * 4;

            unsigned char* p_tcpdata = buf + tcpdata_offset;

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
                    printf("%02hhX ", buf[i + iphdr_offset]);
                }
            	printf("\n");
            }
        }
    }
    close(s);

    return 0;
}
