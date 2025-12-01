#include <iostream>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int main() {
    int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (sock < 0) {
        perror("Socket");
        return 1;
    }

    struct ifreq ifr;
    std::strcpy(ifr.ifr_name, "can0");
    ioctl(sock, SIOCGIFINDEX, &ifr);

    struct sockaddr_can addr = {};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Bind");
        return 1;
    }

    struct can_frame move_frame = {};
    move_frame.can_id  = 0x00C;       // CAN ID
    move_frame.can_dlc = 8;           // Data length
    *((float*)(move_frame.data)) = 2137.0f;
    move_frame.data[4] = 0x00;
    move_frame.data[5] = 0x00;
    move_frame.data[6] = 0x00;
    move_frame.data[7] = 0x00;

    struct can_frame clear_error_frame = {};
    clear_error_frame.can_id  = 0x018;       // CAN ID
    clear_error_frame.can_dlc = 8;           // Data length
    clear_error_frame.data[0] = 0x00;
    clear_error_frame.data[1] = 0x00;
    clear_error_frame.data[2] = 0x00;
    clear_error_frame.data[3] = 0x00;
    clear_error_frame.data[4] = 0x00;
    clear_error_frame.data[5] = 0x00;
    clear_error_frame.data[6] = 0x00;
    clear_error_frame.data[7] = 0x00;

    struct can_frame frame = move_frame;

    int bytes_sent = write(sock, &frame, sizeof(frame));
    if (bytes_sent != sizeof(frame)) {
        perror("Write");
        return 1;
    }

    std::cout << "CAN frame sent!" << std::endl;

    close(sock);
    return 0;
}
