#include <iostream>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

#include "messages.hpp"

int main() {
    int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    CHECK_RET(sock, "socket");

    struct ifreq ifr{};
    std::strcpy(ifr.ifr_name, "can0");
    CHECK_RET(ioctl(sock, SIOCGIFINDEX, &ifr), "ioctl");

    struct sockaddr_can addr{};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    CHECK_RET(bind(sock, (struct sockaddr *)&addr, sizeof(addr)), "bind");

    Msg_GetEncoderEst est(0);
    struct can_frame resp{};

    est.send_and_recv(sock, &resp);

    close(sock);
    return 0;
}
