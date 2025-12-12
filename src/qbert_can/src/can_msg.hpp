#pragma once

#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <linux/can.h>
#include <sys/socket.h> 

#include "qbert_msgs/msg/can_frame.hpp"

#define CHECK_RET(expr, msg)                     \
    do {                                         \
        if ((expr) < 0) {                        \
            perror(msg);                         \
            return 1;                            \
        }                                        \
    } while (0)

#define CHECK(expr, msg)                         \
    do {                                         \
        if (!(expr)) {                           \
            perror(msg);                         \
            return 1;                            \
        }                                        \
    } while (0)

/***********************************************
 *  Little-endian write helper
 ***********************************************/
template<typename T>
static inline void write_le(uint8_t* dest, T value) {
    std::memcpy(dest, &value, sizeof(T));
}

template <typename T>
T read_le(const uint8_t* p) {
    using U = std::conditional_t<(sizeof(T) == 4), uint32_t,
              std::conditional_t<(sizeof(T) == 8), uint64_t,
              uint16_t>>;

    U tmp = 0;
    for (size_t i = 0; i < sizeof(T); i++) {
        tmp |= U(p[i]) << (8 * i);
    }

    T out;
    std::memcpy(&out, &tmp, sizeof(T));
    return out;
}

/***********************************************
 *  Base CAN message
 ***********************************************/
struct CANMsg {
    using RosCANMsg = qbert_msgs::msg::CanFrame;
    can_frame frame;

    int send(int sock) {
        CHECK_RET(::send(sock, &frame, sizeof(can_frame), 0), "send");

        return 0;
    }

    void recv_callback(can_frame recv_frame) {}

    RosCANMsg to_ros_msg() {
        RosCANMsg msg = RosCANMsg();
        msg.id = frame.can_id;
        msg.dlc = frame.can_dlc;
        for (int i=0; i<frame.can_dlc; i++) {
            msg.data[i] = frame.data[i];
        }
    }

    void from_ros_msg(RosCANMsg ros_msg) {
        frame.can_id = ros_msg.id;
        frame.can_dlc = ros_msg.dlc;
        for (int i=0; i<ros_msg.dlc; i++) {
            frame.data[i] = ros_msg.data[i];
        }
    }
};