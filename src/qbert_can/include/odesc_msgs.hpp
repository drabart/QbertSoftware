#pragma once

#include "can_msgs/msg/frame.hpp"
#include "can_utils.hpp"

using CanFrame = can_msgs::msg::Frame;

enum ODescCommand {
    HeartBeat = 0x01,
//    GetMotorError = 0x03,
//    GetEncoderError = 0x04,
//    GetSensorlessError = 0x05,
    SetRequestedState = 0x07,
    GetEncoderEst = 0x09,
//    GetEncoderCount = 0x0A,
    SetControlMode = 0x0B,
    SetInputPos = 0x0C,
    SetInputVel = 0x0D,
//    GetIQ = 0x14,
//    GetSensorlessEst = 0x15,
    Reboot = 0x16,
//    GetBusVoltageCurrent = 0x17,
    ClearErrors = 0x18,
};

struct Msg_HeartBeat {
    uint32_t axis_error = 0;
    uint8_t axis_current_state = 0;
    bool motor_error = false;
    bool encoder_error = false;
    bool controller_error = false;
    bool trajectory_done = false;

    Msg_HeartBeat(const CanFrame& frame) {
        axis_error = read_le<uint32_t>(frame.data.data());
        axis_current_state = frame.data.at(4);
        motor_error = frame.data.at(5) & 0b1;
        encoder_error = frame.data.at(6) & 0b1;
        controller_error = frame.data.at(7) & 0b1;
        trajectory_done = frame.data.at(7) & 0x80;
    }
};

struct Msg_GetEncoderEst {
    float pos_estimate = 0;
    float vel_estimate = 0;

    Msg_GetEncoderEst(const CanFrame& frame) {
        pos_estimate = read_le<float>(frame.data.data());
        vel_estimate = read_le<float>(frame.data.data() + 4);
    }
};
