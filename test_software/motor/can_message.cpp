#include <iostream>
#include <iomanip>
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

    int motor_id = 1 << 5;
    
    Msg_ClearErrors cle(motor_id);
    cle.send(sock);

    Msg_SetRequestedState state(motor_id, 8);
    state.send(sock);

    #define POSITION_CONTROL (3u)
    #define INPUT_MODE_TRAP_TRAJ (5u)
    Msg_SetControllerModes modes(motor_id, POSITION_CONTROL, INPUT_MODE_TRAP_TRAJ);
    modes.send(sock);

    // Example: move position first
    Msg_SetInputPos pos_0(motor_id, 0.0);
    Msg_SetInputPos pos_100(motor_id, 500.0);
    bool up = true;
    int res = pos_100.send(sock);
    if (res != 0) {
        std::cerr << "Failed to send input pos\n";
    }

    // Instantiate all getters
    Msg_GetEncoderEst est(motor_id);
    Msg_GetEncoderCount count(motor_id);
    Msg_GetIQ iq(motor_id);
    Msg_GetSensorlessEst senseless(motor_id);
    Msg_GetBusVoltageCurrent bus(motor_id);
    Msg_GetMotorError motor_err(motor_id);
    Msg_GetEncoderError encoder_err(motor_id);
    Msg_GetSensorlessError sensorless_err(motor_id);

    while (true) {
        // Encoder estimates
        est.send_and_recv(sock);
        std::cout << std::setprecision(3) << "[EncoderEst] pos=" << est.pos_estimate 
                << " vel=" << est.vel_estimate << "\n";

        // Encoder counts
        // count.send_and_recv(sock);
        // std::cout << "[EncoderCount] shadow=" << count.shadow_count
        //         << " count_in_cpr=" << count.count_in_cpr << "\n";

        // IQ
        // iq.send_and_recv(sock);
        // std::cout << "[IQ] setpoint=" << iq.iq_setpoint
        //         << " measured=" << iq.iq_measured << "\n";

        // // Sensorless estimates
        // senseless.send_and_recv(sock);
        // std::cout << "[Sensorless] pos=" << senseless.pos_estimate
        //         << " vel=" << senseless.vel_estimate << "\n";

        // Bus voltage/current
        // bus.send_and_recv(sock);
        // std::cout << "[Bus] voltage=" << bus.bus_voltage
        //         << " current=" << bus.bus_current << "\n";

        // // Motor error
        // motor_err.send_and_recv(sock);
        // std::cout << "[MotorError] " << motor_err.motor_error << "\n";

        // // Encoder error
        // encoder_err.send_and_recv(sock);
        // std::cout << "[EncoderError] " << encoder_err.encoder_error << "\n";

        // Sensorless error
        // sensorless_err.send_and_recv(sock);
        // std::cout << "[SensorlessError] " << sensorless_err.sensorless_error << "\n";

        // std::cout << "------------------------\n" << std::flush;

        // Exit condition
        if (up && est.pos_estimate > 499.5) {
            pos_0.send(sock);
            up = !up;
        }
        if (!up && est.pos_estimate < 0.5) {
            pos_100.send(sock);
            up = !up;
        }

        usleep(5'000);
    }


    close(sock);
    return 0;
}
