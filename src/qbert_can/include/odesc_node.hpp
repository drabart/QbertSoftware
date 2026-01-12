#pragma once

#include "can_msgs/msg/frame.hpp"

#include <rclcpp_action/create_server.hpp>
#include <rclcpp_action/server.hpp>

#include "qbert_msgs/action/move_to_pos.hpp"
#include "qbert_msgs/srv/motor.hpp"
#include "qbert_msgs/srv/move_with_vel.hpp"
#include "qbert_msgs/srv/setup_drive.hpp"

#include "can_node.hpp"
#include "odesc_msgs.hpp"

using CanFrame = can_msgs::msg::Frame;
using Motor = qbert_msgs::srv::Motor;
using SetupDrive = qbert_msgs::srv::SetupDrive;
using MoveWithVel = qbert_msgs::srv::MoveWithVel;
using MoveToPos = qbert_msgs::action::MoveToPos;

class ODescNode : public CanNode {
public:
    explicit ODescNode() : CanNode("ODesc_Node") {
        using namespace std::placeholders;

        reboot_srv_ = create_service<Motor>(
            "/odesc/reboot",
            std::bind(&ODescNode::reboot, this, _1, _2)
        );

        clear_error_srv_ = create_service<Motor>(
            "/odesc/clear_error",
            std::bind(&ODescNode::clear_error, this, _1, _2)
        );

        home_srv_ = create_service<Motor>(
            "/odesc/home",
            std::bind(&ODescNode::home, this, _1, _2)
        );

        setup_srv_ = create_service<SetupDrive>(
            "/odesc/setup",
            std::bind(&ODescNode::setup, this, _1, _2)
        );

        move_with_vel_srv_ = create_service<MoveWithVel>(
            "/odesc/move_with_velocity",
            std::bind(&ODescNode::move_with_vel, this, _1, _2)
        );

        motor_ready_srv_ = this->create_service<Motor>(
            "/odesc/ready",
            std::bind(&ODescNode::motor_ready, this, _1, _2)
        );

        move_to_pos_action_ = rclcpp_action::create_server<MoveToPos>(
            this,
            "/odesc/move_to_pos",
            std::bind(&ODescNode::move_to_pos_goal, this, _1, _2),
            std::bind(&ODescNode::move_to_pos_cancel, this, _1),
            std::bind(&ODescNode::move_to_pos_accepted, this, _1)
        );

        callbacks_.emplace(HeartBeat, [this](CanFrame frame) { heartbeat(frame); });
        callbacks_.emplace(GetEncoderEst, [this](CanFrame frame) { encoder_est(frame); });
    }

    enum AxisState {
        IDLE = 1,
        CLOSED_LOOP_CONTROL = 8,
        HOMING = 11,
    };

    enum InputMode {
        INACTIVE = 0,
        PASSTROUGH = 1,
        TRAP_TRAJ = 5,
    };

    enum ControlMode {
        VELOCITY_CONTROL = 2,
        POSITION_CONTROL = 3,
    };

private:
    // Member fields
    rclcpp::Service<Motor>::SharedPtr reboot_srv_;
    rclcpp::Service<Motor>::SharedPtr clear_error_srv_;
    rclcpp::Service<Motor>::SharedPtr home_srv_;
    rclcpp::Service<Motor>::SharedPtr motor_ready_srv_;
    rclcpp::Service<SetupDrive>::SharedPtr setup_srv_;
    rclcpp::Service<MoveWithVel>::SharedPtr move_with_vel_srv_;

    rclcpp_action::Server<MoveToPos>::SharedPtr move_to_pos_action_;

    struct MotorState {
        double pos_est;
        AxisState axis_state;
        bool error;
    };

    std::unordered_map<uint8_t, MotorState> motors_;
    std::unordered_map<ODescCommand, std::function<void (const CanFrame&)>> callbacks_;

    // Member fields
    //
    // Helper functions

    void CAN_recv(const CanFrame& frame) override;

    bool is_active(uint8_t motor_id) const override;

    // Helper functions
    // 
    // Receive callbacks

    void heartbeat(const CanFrame& frame);

    void encoder_est(const CanFrame& frame);

    // Receive callbacks
    //
    // Services

    void reboot(
        const std::shared_ptr<Motor::Request> req,
        std::shared_ptr<Motor::Response> res
    ) const;

    void clear_error(
        const std::shared_ptr<Motor::Request> req,
        std::shared_ptr<Motor::Response> res
    ) const;

    void home(
        const std::shared_ptr<Motor::Request> req,
        std::shared_ptr<Motor::Response> res
    ) const;

    void motor_ready(
        const std::shared_ptr<Motor::Request> req,
        std::shared_ptr<Motor::Response> res
    ) const;

    bool request_state(
        uint8_t motor_id,
        uint8_t mode
    ) const;

    void setup(
        const std::shared_ptr<SetupDrive::Request> req,
        std::shared_ptr<SetupDrive::Response> res
    ) const;

    void move_with_vel(
        const std::shared_ptr<MoveWithVel::Request> req,
        std::shared_ptr<MoveWithVel::Response> res
    ) const;

    // Services
    //
    // Actions

    rclcpp_action::GoalResponse move_to_pos_goal(
        const rclcpp_action::GoalUUID & uuid,
        std::shared_ptr<const MoveToPos::Goal> goal
    ) const;

    rclcpp_action::CancelResponse move_to_pos_cancel(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
    ) const;

    void move_to_pos_accepted(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
    );

    void move_to_pos_execute(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
    );

    // Actions
    //
    // Send requests

    void send_position_est_req(uint8_t motor_id) const;

    void send_position_target_req(
        uint8_t motor_id,
        float target
    ) const;

    void send_velocity_target_req(
        uint8_t motor_id,
        float target
    ) const;

    void send_reboot_req(uint8_t motor_id) const;

    void send_clear_errors_req(uint8_t motor_id) const;

    void send_axis_state_req(
        uint8_t motor_id,
        AxisState state
    ) const;

    void send_control_state_req(
        uint8_t motor_id,
        InputMode input,
        ControlMode control
    ) const;

    // send requests
};
