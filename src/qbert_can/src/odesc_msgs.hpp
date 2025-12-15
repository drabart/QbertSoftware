#pragma once

#include "can_msg.hpp"

struct Msg_HeartBeat : public CANMsg {
    uint32_t axis_error;
    uint8_t axis_current_state;
    bool motor_error;
    bool encoder_error;
    bool controller_error;
    bool trajectory_done;

    Msg_HeartBeat(const CANMsg& m) : CANMsg(m) {}

    Msg_HeartBeat() {
        axis_error = 0;
        axis_current_state = 0;
        motor_error = false;
        encoder_error = false;
        controller_error = false;
        trajectory_done = false;
    }

    void recv_callback(can_frame recv_frame) {
        axis_error = read_le<uint32_t>(recv_frame.data);
        axis_current_state = read_le<uint8_t>(recv_frame.data + 4);
        uint8_t helper;
        helper = read_le<uint8_t>(recv_frame.data + 5);
        motor_error = helper & 0x01;
        helper = read_le<uint8_t>(recv_frame.data + 6);
        encoder_error = helper & 0x01;
        helper = read_le<uint8_t>(recv_frame.data + 7);
        controller_error = helper & 0x01;
        trajectory_done = helper & 0x80;
    }
};

/***********************************************
 *  0x007 – Set Axis Requested State
 ***********************************************/
struct Msg_SetRequestedState : public CANMsg {
    Msg_SetRequestedState(uint8_t axis_id, uint32_t state) {
        frame.can_id = 0x007 | axis_id;
        frame.can_dlc = 4;
        write_le<uint32_t>(frame.data, state);
    }
};

/***********************************************
 *  0x006 – Set Axis Node ID
 ***********************************************/
struct Msg_SetAxisNodeID : public CANMsg {
    Msg_SetAxisNodeID(uint8_t axis_id, uint32_t new_id) {
        frame.can_id = 0x006 | axis_id;
        frame.can_dlc = 4;
        write_le<uint32_t>(frame.data, new_id);
    }
};

/***********************************************
 *  0x00B – Set Controller Modes
 *  control_mode (int32)
 *  input_mode   (int32)
 ***********************************************/
struct Msg_SetControllerModes : public CANMsg {
    Msg_SetControllerModes(uint8_t axis_id,
                           int32_t control_mode,
                           int32_t input_mode)
    {
        frame.can_id  = 0x00B | axis_id;
        frame.can_dlc = 8;

        write_le<int32_t>(frame.data + 0, control_mode);
        write_le<int32_t>(frame.data + 4, input_mode);
    }
};

/***********************************************
 *  0x00C – Set Input Position
 *  pos (float32)
 *  vel_ff (int16 * 0.001)
 *  torque_ff (int16 * 0.001)
 ***********************************************/
struct Msg_SetInputPos : public CANMsg {
    Msg_SetInputPos(uint8_t axis_id,
                    float position,
                    float vel_ff = 0.0f,
                    float torque_ff = 0.0f)
    {
        frame.can_id = 0x00C | axis_id;
        frame.can_dlc = 8;

        int16_t vel = (int16_t)(vel_ff * 1000.0f);
        int16_t tor = (int16_t)(torque_ff * 1000.0f);

        write_le<float>(frame.data + 0, position);
        write_le<int16_t>(frame.data + 4, vel);
        write_le<int16_t>(frame.data + 6, tor);
    }
};

/***********************************************
 *  0x00D – Set Input Velocity
 *  vel (float32)
 *  torque_ff (float32)
 ***********************************************/
struct Msg_SetInputVel : public CANMsg {
    Msg_SetInputVel(uint8_t axis_id,
                    float vel,
                    float torque_ff = 0.0)
    {
        frame.can_id = 0x00D | axis_id;
        frame.can_dlc = 8;

        write_le<float>(frame.data + 0, vel);
        write_le<float>(frame.data + 4, torque_ff);
    }
};

/***********************************************
 *  0x00E – Set Input Torque
 ***********************************************/
struct Msg_SetInputTorque : public CANMsg {
    Msg_SetInputTorque(uint8_t axis_id, float torque) {
        frame.can_id = 0x00E | axis_id;
        frame.can_dlc = 4;
        write_le<float>(frame.data, torque);
    }
};

/***********************************************
 *  0x00F – Set Limits
 *  vel_limit (float32)
 *  current_limit (float32)
 ***********************************************/
struct Msg_SetLimits : public CANMsg {
    Msg_SetLimits(uint8_t axis_id,
                  float vel_limit,
                  float current_limit)
    {
        frame.can_id = 0x00F | axis_id;
        frame.can_dlc = 8;
        write_le<float>(frame.data + 0, vel_limit);
        write_le<float>(frame.data + 4, current_limit);
    }
};

/***********************************************
 *  0x011 – Set Trajectory Velocity Limit
 ***********************************************/
struct Msg_SetTrajVelLimit : public CANMsg {
    Msg_SetTrajVelLimit(uint8_t axis_id, float value) {
        frame.can_id = 0x011 | axis_id;
        frame.can_dlc = 4;
        write_le<float>(frame.data, value);
    }
};

/***********************************************
 *  0x012 – Set Trajectory Accel + Decel Limits
 ***********************************************/
struct Msg_SetTrajAccelLimits : public CANMsg {
    Msg_SetTrajAccelLimits(uint8_t axis_id,
                           float accel,
                           float decel)
    {
        frame.can_id = 0x012 | axis_id;
        frame.can_dlc = 8;
        write_le<float>(frame.data + 0, accel);
        write_le<float>(frame.data + 4, decel);
    }
};

/***********************************************
 *  0x013 – Set Trajectory Inertia
 ***********************************************/
struct Msg_SetTrajInertia : public CANMsg {
    Msg_SetTrajInertia(uint8_t axis_id, float inertia) {
        frame.can_id = 0x013 | axis_id;
        frame.can_dlc = 4;
        write_le<float>(frame.data, inertia);
    }
};

/***********************************************
 *  0x01A – Set Position Gain
 ***********************************************/
struct Msg_SetPositionGain : public CANMsg {
    Msg_SetPositionGain(uint8_t axis_id, float gain) {
        frame.can_id = 0x01A | axis_id;
        frame.can_dlc = 4;
        write_le<float>(frame.data, gain);
    }
};

/***********************************************
 *  0x01B – Set Velocity Gains
 ***********************************************/
struct Msg_SetVelocityGains : public CANMsg {
    Msg_SetVelocityGains(uint8_t axis_id,
                         float vel_gain,
                         float vel_integrator_gain)
    {
        frame.can_id = 0x01B | axis_id;
        frame.can_dlc = 8;
        write_le<float>(frame.data + 0, vel_gain);
        write_le<float>(frame.data + 4, vel_integrator_gain);
    }
};

/***********************************************
 *  0x019 – Set Linear Count
 ***********************************************/
struct Msg_SetLinearCount : public CANMsg {
    Msg_SetLinearCount(uint8_t axis_id, int32_t pos_count) {
        frame.can_id = 0x019 | axis_id;
        frame.can_dlc = 4;
        write_le<int32_t>(frame.data, pos_count);
    }
};

/***********************************************
 *  0x010 – Start Anticogging
 ***********************************************/
struct Msg_StartAnticogging : public CANMsg {
    Msg_StartAnticogging(uint8_t axis_id) {
        frame.can_id = 0x010 | axis_id;
        frame.can_dlc = 0;
    }
};

/***********************************************
 *  0x016 – Reboot
 ***********************************************/
struct Msg_Reboot : public CANMsg {
    Msg_Reboot(uint8_t axis_id) {
        frame.can_id = 0x016 | axis_id;
        frame.can_dlc = 0;
    }
};

/***********************************************
 *  0x018 – Clear Errors
 ***********************************************/
struct Msg_ClearErrors : public CANMsg {
    Msg_ClearErrors(uint8_t axis_id) {
        frame.can_id = 0x018 | axis_id;
        frame.can_dlc = 0;
    }
};

/***********************************************
 *  Getter messages (no payload)
 ***********************************************/

enum MotorCommandID {
    HeartBeat = 0x001,
    GetMotorError = 0x003,
    GetEncoderError = 0x004,
    GetSensorlessError = 0x005,
    GetEncoderEst = 0x009,
    GetEncoderCount = 0x00A,
    GetIQ = 0x014,
    GetSensorlessEst = 0x015,
    GetBusVoltageCurrent = 0x017,
};


// 0x003 - Get Motor Error
struct Msg_GetMotorError : public CANMsg {
    uint64_t motor_error = 0;

    Msg_GetMotorError(const CANMsg& m) : CANMsg(m) {}

    Msg_GetMotorError(uint8_t axis_id) {
        frame.can_id = 0x003 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        motor_error = read_le<uint64_t>(recv_frame.data);
    }
};

// 0x004 - Get Encoder Error
struct Msg_GetEncoderError : public CANMsg {
    uint32_t encoder_error = 0;

    Msg_GetEncoderError(const CANMsg& m) : CANMsg(m) {}

    Msg_GetEncoderError(uint8_t axis_id) {
        frame.can_id = 0x004 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        encoder_error = read_le<uint32_t>(recv_frame.data);
    }
};

// 0x005 - Get Sensorless Error
struct Msg_GetSensorlessError : public CANMsg {
    uint32_t sensorless_error = 0;

    Msg_GetSensorlessError(const CANMsg& m) : CANMsg(m) {}

    Msg_GetSensorlessError(uint8_t axis_id) {
        frame.can_id = 0x005 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        sensorless_error = read_le<uint32_t>(recv_frame.data);
    }
};

// 0x009 - Get Encoder Estimates
struct Msg_GetEncoderEst : public CANMsg {
    float pos_estimate = 0;
    float vel_estimate = 0;

    Msg_GetEncoderEst(const CANMsg& m) : CANMsg(m) {}

    Msg_GetEncoderEst(uint8_t axis_id) {
        frame.can_id = 0x009 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        pos_estimate = read_le<float>(recv_frame.data);
        vel_estimate = read_le<float>(recv_frame.data + 4);
    }
};

// 0x00A - Get Encoder Count
struct Msg_GetEncoderCount : public CANMsg {
    int32_t shadow_count = 0;
    int32_t count_in_cpr = 0;

    Msg_GetEncoderCount(const CANMsg& m) : CANMsg(m) {}

    Msg_GetEncoderCount(uint8_t axis_id) {
        frame.can_id = 0x00A | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        shadow_count = read_le<int32_t>(recv_frame.data);
        count_in_cpr = read_le<int32_t>(recv_frame.data + 4);
    }
};

// 0x014 - Get IQ
struct Msg_GetIQ : public CANMsg {
    float iq_setpoint = 0;
    float iq_measured = 0;

    Msg_GetIQ(const CANMsg& m) : CANMsg(m) {}

    Msg_GetIQ(uint8_t axis_id) {
        frame.can_id = 0x014 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        iq_setpoint = read_le<float>(recv_frame.data);
        iq_measured = read_le<float>(recv_frame.data + 4);
    }
};

// 0x015 - Get Sensorless Estimates
struct Msg_GetSensorlessEst : public CANMsg {
    float pos_estimate = 0;
    float vel_estimate = 0;

    Msg_GetSensorlessEst(const CANMsg& m) : CANMsg(m) {}

    Msg_GetSensorlessEst(uint8_t axis_id) {
        frame.can_id = 0x015 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        pos_estimate = read_le<float>(recv_frame.data);
        vel_estimate = read_le<float>(recv_frame.data + 4);
    }
};

// 0x017 - Get Bus Voltage and Current
struct Msg_GetBusVoltageCurrent : public CANMsg {
    float bus_voltage = 0;
    float bus_current = 0;

    Msg_GetBusVoltageCurrent(const CANMsg& m) : CANMsg(m) {}

    Msg_GetBusVoltageCurrent(uint8_t axis_id) {
        frame.can_id = 0x017 | axis_id | CAN_RTR_FLAG;
        frame.can_dlc = 0;
    }

    void recv_callback(can_frame recv_frame) {
        bus_voltage = read_le<float>(recv_frame.data);
        bus_current = read_le<float>(recv_frame.data + 4);
    }
};
