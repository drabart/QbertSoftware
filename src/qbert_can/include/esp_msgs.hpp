#pragma once

#include "can_msgs/msg/frame.hpp"
#include "can_utils.hpp"

using CanFrame = can_msgs::msg::Frame;

enum EspCommand {
    HeartBeat = 0x01,
    SetAxePos = 0x02,
    SetGripperState = 0x03,
    GetAxePos = 0x04,
    GetGripperState = 0x05,
};

struct Msg_HeartBeat {
    // TBD

    Msg_HeartBeat(const CanFrame& _) {}
};

struct Msg_GetAxePos {
    float pos_0;
    float pos_1;

    Msg_GetAxePos(const CanFrame& frame) {
        pos_0 = read_le<float>(frame.data.data());
        pos_1 = read_le<float>(frame.data.data() + 4);
    }
};

struct Msg_GetGripperState {
    bool extended;

    Msg_GetGripperState(const CanFrame& frame) {
        extended = frame.data.at(0);
    }
};
