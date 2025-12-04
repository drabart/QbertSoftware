#pragma once
#include <iostream>
#include <cstring>
#include <cstdint>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

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

/***********************************************
 *  Base CAN message
 ***********************************************/
struct ODriveCANMsg {
    uint32_t id;
    uint8_t dlc;
    uint8_t data[8];
    struct can_frame frame;

    struct can_frame* toFrame() {
        this->frame.can_id = id;
        this->frame.can_dlc = dlc;
        std::memcpy(this->frame.data, data, 8);
        return &this->frame;
    }

    int send(int sock) {
        struct can_frame* req = this->toFrame();
        CHECK_RET(::send(sock, req, sizeof(struct can_frame), 0), "send");

        return 0;
    }
    
    int send_and_recv(int sock, can_frame* resp) {
        this->send(sock);
        std::cout << "sent" << std::endl;
        
        while (true) {
            int n = recv(sock, resp, sizeof(resp), 0);
            CHECK_RET(n, "recv");
            uint32_t clean = resp->can_id & CAN_EFF_MASK;
            uint32_t expected = this->frame.can_id & CAN_EFF_MASK;

            std::cout << "received" << std::endl;

            if (clean == expected && !(resp->can_id & CAN_RTR_FLAG)) {
                std::cout << "Got response DLC=" << (int)resp->can_dlc << "\n";
                for (int i = 0; i < resp->can_dlc; i++)
                    std::cout << "0x" << std::hex << (int)resp->data[i] << " ";
                std::cout << std::dec << "\n";
                return 0;
            }
        }

        return -1;
    }
};

/***********************************************
 *  0x007 – Set Axis Requested State
 ***********************************************/
struct Msg_SetRequestedState : public ODriveCANMsg {
    Msg_SetRequestedState(uint8_t axis_id, uint32_t state) {
        id = 0x007 | axis_id;
        dlc = 4;
        write_le<uint32_t>(data, state);
    }
};

/***********************************************
 *  0x006 – Set Axis Node ID
 ***********************************************/
struct Msg_SetAxisNodeID : public ODriveCANMsg {
    Msg_SetAxisNodeID(uint8_t axis_id, uint32_t new_id) {
        id = 0x006 | axis_id;
        dlc = 4;
        write_le<uint32_t>(data, new_id);
    }
};

/***********************************************
 *  0x00C – Set Input Position
 *  pos (float32)
 *  vel_ff (int16 * 0.001)
 *  torque_ff (int16 * 0.001)
 ***********************************************/
struct Msg_SetInputPos : public ODriveCANMsg {
    Msg_SetInputPos(uint8_t axis_id,
                    float position,
                    float vel_ff = 0.0f,
                    float torque_ff = 0.0f)
    {
        id = 0x00C | axis_id;
        dlc = 8;

        int16_t vel = (int16_t)(vel_ff * 1000.0f);
        int16_t tor = (int16_t)(torque_ff * 1000.0f);

        write_le<float>(data + 0, position);
        write_le<int16_t>(data + 4, vel);
        write_le<int16_t>(data + 6, tor);
    }
};

/***********************************************
 *  0x00D – Set Input Velocity
 *  vel (float32)
 *  torque_ff (float32)
 ***********************************************/
struct Msg_SetInputVel : public ODriveCANMsg {
    Msg_SetInputVel(uint8_t axis_id,
                    float vel,
                    float torque_ff)
    {
        id = 0x00D | axis_id;
        dlc = 8;

        write_le<float>(data + 0, vel);
        write_le<float>(data + 4, torque_ff);
    }
};

/***********************************************
 *  0x00E – Set Input Torque
 ***********************************************/
struct Msg_SetInputTorque : public ODriveCANMsg {
    Msg_SetInputTorque(uint8_t axis_id, float torque) {
        id = 0x00E | axis_id;
        dlc = 4;
        write_le<float>(data, torque);
    }
};

/***********************************************
 *  0x00F – Set Limits
 *  vel_limit (float32)
 *  current_limit (float32)
 ***********************************************/
struct Msg_SetLimits : public ODriveCANMsg {
    Msg_SetLimits(uint8_t axis_id,
                  float vel_limit,
                  float current_limit)
    {
        id = 0x00F | axis_id;
        dlc = 8;
        write_le<float>(data + 0, vel_limit);
        write_le<float>(data + 4, current_limit);
    }
};

/***********************************************
 *  0x011 – Set Trajectory Velocity Limit
 ***********************************************/
struct Msg_SetTrajVelLimit : public ODriveCANMsg {
    Msg_SetTrajVelLimit(uint8_t axis_id, float value) {
        id = 0x011 | axis_id;
        dlc = 4;
        write_le<float>(data, value);
    }
};

/***********************************************
 *  0x012 – Set Trajectory Accel + Decel Limits
 ***********************************************/
struct Msg_SetTrajAccelLimits : public ODriveCANMsg {
    Msg_SetTrajAccelLimits(uint8_t axis_id,
                           float accel,
                           float decel)
    {
        id = 0x012 | axis_id;
        dlc = 8;
        write_le<float>(data + 0, accel);
        write_le<float>(data + 4, decel);
    }
};

/***********************************************
 *  0x013 – Set Trajectory Inertia
 ***********************************************/
struct Msg_SetTrajInertia : public ODriveCANMsg {
    Msg_SetTrajInertia(uint8_t axis_id, float inertia) {
        id = 0x013 | axis_id;
        dlc = 4;
        write_le<float>(data, inertia);
    }
};

/***********************************************
 *  0x01A – Set Position Gain
 ***********************************************/
struct Msg_SetPositionGain : public ODriveCANMsg {
    Msg_SetPositionGain(uint8_t axis_id, float gain) {
        id = 0x01A | axis_id;
        dlc = 4;
        write_le<float>(data, gain);
    }
};

/***********************************************
 *  0x01B – Set Velocity Gains
 ***********************************************/
struct Msg_SetVelocityGains : public ODriveCANMsg {
    Msg_SetVelocityGains(uint8_t axis_id,
                         float vel_gain,
                         float vel_integrator_gain)
    {
        id = 0x01B | axis_id;
        dlc = 8;
        write_le<float>(data + 0, vel_gain);
        write_le<float>(data + 4, vel_integrator_gain);
    }
};

/***********************************************
 *  0x019 – Set Linear Count
 ***********************************************/
struct Msg_SetLinearCount : public ODriveCANMsg {
    Msg_SetLinearCount(uint8_t axis_id, int32_t pos_count) {
        id = 0x019 | axis_id;
        dlc = 4;
        write_le<int32_t>(data, pos_count);
    }
};

/***********************************************
 *  0x010 – Start Anticogging
 ***********************************************/
struct Msg_StartAnticogging : public ODriveCANMsg {
    Msg_StartAnticogging(uint8_t axis_id) {
        id = 0x010 | axis_id;
        dlc = 0;
    }
};

/***********************************************
 *  0x016 – Reboot
 ***********************************************/
struct Msg_Reboot : public ODriveCANMsg {
    Msg_Reboot(uint8_t axis_id) {
        id = 0x016 | axis_id;
        dlc = 0;
    }
};

/***********************************************
 *  0x018 – Clear Errors
 ***********************************************/
struct Msg_ClearErrors : public ODriveCANMsg {
    Msg_ClearErrors(uint8_t axis_id) {
        id = 0x018 | axis_id;
        dlc = 0;
    }
};

/***********************************************
 *  Getter messages (no payload)
 ***********************************************/
struct Msg_GetEncoderEst : public ODriveCANMsg {
    Msg_GetEncoderEst(uint8_t axis_id) {
        id = 0x009 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetEncoderCount : public ODriveCANMsg {
    Msg_GetEncoderCount(uint8_t axis_id) {
        id = 0x00A | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetMotorError : public ODriveCANMsg {
    Msg_GetMotorError(uint8_t axis_id) {
        id = 0x003 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetEncoderError : public ODriveCANMsg {
    Msg_GetEncoderError(uint8_t axis_id) {
        id = 0x004 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetSensorlessError : public ODriveCANMsg {
    Msg_GetSensorlessError(uint8_t axis_id) {
        id = 0x005 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetIQ : public ODriveCANMsg {
    Msg_GetIQ(uint8_t axis_id) {
        id = 0x014 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetSensorlessEst : public ODriveCANMsg {
    Msg_GetSensorlessEst(uint8_t axis_id) {
        id = 0x015 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetBusVoltageCurrent : public ODriveCANMsg {
    Msg_GetBusVoltageCurrent(uint8_t axis_id) {
        id = 0x017 | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetADCVoltage : public ODriveCANMsg {
    Msg_GetADCVoltage(uint8_t axis_id) {
        id = 0x01C | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};

struct Msg_GetControllerError : public ODriveCANMsg {
    Msg_GetControllerError(uint8_t axis_id) {
        id = 0x01D | axis_id | CAN_RTR_FLAG;
        dlc = 0;
    }
};
