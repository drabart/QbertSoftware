#include "can_msgs/msg/frame.hpp"
#include <rclcpp/executors.hpp>
#include <chrono>

#include "odesc_node.hpp"

using CanFrame = can_msgs::msg::Frame;
using namespace std::chrono_literals;

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<ODescNode>();

    rclcpp::executors::MultiThreadedExecutor exec;
    exec.add_node(node);
    exec.spin();

    rclcpp::shutdown();
    return 0;
}

void ODescNode::CAN_recv(const CanFrame& frame) {
    uint8_t cmd = extract_cmd(frame.id);
    if (frame.is_rtr) { return; }
    if (cmd != 1) {
        RCLCPP_INFO(get_logger(), "CAN: %d", cmd);
    }
    if (auto func = callbacks_.find(static_cast<ODescCommand>(cmd)); func != callbacks_.end()) { func->second(frame); }
}

// Helpers

bool ODescNode::is_active(uint8_t motor_id) const {
    if (auto it = motors_.find(motor_id); it != motors_.end()) {
        return !it->second.error;
    }
    return false;
}

// Helpers
// Receive callbacks

void ODescNode::heartbeat(const CanFrame& frame) {
    Msg_HeartBeat hb = frame;

    uint8_t id = extract_id(frame.id);
    if (id >= 0b100000) { return; }

    if (auto it = motors_.find(id); it == motors_.end()) {
        motors_.emplace(id, MotorState {});
    }

    MotorState& motor = motors_.at(id);

    motor.axis_state = static_cast<AxisState>(hb.axis_current_state);
    motor.error = hb.controller_error | hb.encoder_error | hb.axis_error | hb.motor_error;
}

void ODescNode::encoder_est(const CanFrame& frame) {
    Msg_GetEncoderEst est = frame;

    uint8_t id = extract_id(frame.id);
    if (id >= 0b100000) { return; }

    if (auto it = motors_.find(id); it == motors_.end()) {
        // TODO: if we get a response from this id, id should be alive
        return;
    }

    MotorState& motor = motors_.at(id);
    
    RCLCPP_INFO(get_logger(), "received position estimate %f", est.pos_estimate);
    motor.pos_est = est.pos_estimate;

    std::lock_guard lock(position_mutex);
    position_reply = motor.pos_est;

    RCLCPP_INFO(get_logger(), "In encoder_est: %f", motor.pos_est);

    position_received_flag.notify_one();
}

// Receive callbacks
//
// Services

void ODescNode::reboot(
    const std::shared_ptr<Motor::Request> req,
    std::shared_ptr<Motor::Response> res
) const {
    send_reboot_req(req->id);
    res->success = true;
}

void ODescNode::clear_error(
    const std::shared_ptr<Motor::Request> req,
    std::shared_ptr<Motor::Response> res
) const {
    send_clear_errors_req(req->id);
    res->success = true;
}

void ODescNode::home(
    const std::shared_ptr<Motor::Request> req,
    std::shared_ptr<Motor::Response> res
) const {
    if (!is_active(req->id)) {
        res->success = false;
        return;
    }

    send_axis_state_req(req->id, AxisState::HOMING);
    res->success = true;
}

bool ODescNode::request_state(
    uint8_t motor_id,
    uint8_t mode
) const {
    switch (mode) {

        case MotorSetup::Request::MODE_IDLE: {
            send_axis_state_req(
                motor_id,
                AxisState::IDLE
            );
        } break;

        case MotorSetup::Request::MODE_POSITION: {
            send_axis_state_req(
                motor_id,
                AxisState::CLOSED_LOOP_CONTROL
            );
            send_control_state_req(
                motor_id,
                InputMode::TRAP_TRAJ,
                ControlMode::POSITION_CONTROL
            );
        } break;

        case MotorSetup::Request::MODE_VELOCITY: {
            send_axis_state_req(
                motor_id,
                AxisState::CLOSED_LOOP_CONTROL
            );
            send_control_state_req(
                motor_id,
                InputMode::PASSTROUGH,
                ControlMode::VELOCITY_CONTROL
            );
        } break;

        default: {
            return false;
        };
    }

    return true;
}

void ODescNode::setup(
    const std::shared_ptr<MotorSetup::Request> req,
    std::shared_ptr<MotorSetup::Response> res
) const {
    if (!is_active(req->id)) {
        res->success = false;
        return;
    }

    res->success = request_state(req->id, req->mode);
}

void ODescNode::move_with_vel(
    const std::shared_ptr<MoveWithVel::Request> req,
    std::shared_ptr<MoveWithVel::Response> res
) const {
    if (!is_active(req->id)) {
        res->success = false;
        return;
    }

    send_velocity_target_req(req->id, req->vel);
    res->success = true;
}

void ODescNode::get_state(
    const std::shared_ptr<MotorGetState::Request> req,
    std::shared_ptr<MotorGetState::Response> res
) {
    if (!is_active(req->id)) {
        RCLCPP_WARN(this->get_logger(), "Device inactive");
        res->exists = false;
        return;
    }

    if (!send_position_est_req(req->id)) {
        RCLCPP_WARN(this->get_logger(), "Device missing position");
        res->exists = false;
        return;
    }

    MotorState& motor_data = motors_.at(req->id);
    RCLCPP_INFO(get_logger(), "In get_state: %f", motor_data.pos_est);

    res->state = motor_data.axis_state;
    res->error = motor_data.error;
    res->position = motor_data.pos_est;
    res->exists = true;
}

// Services
//
// Actions

rclcpp_action::GoalResponse ODescNode::move_to_pos_goal(
    const rclcpp_action::GoalUUID & _,
    std::shared_ptr<const MoveToPos::Goal> goal
) const {
    if (!is_active(goal->id)) { return rclcpp_action::GoalResponse::REJECT; }
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse ODescNode::move_to_pos_cancel(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) const {
    const auto goal = goal_handle->get_goal();
    request_state(goal->id, MotorSetup::Request::MODE_IDLE);
    return rclcpp_action::CancelResponse::ACCEPT;
}

void ODescNode::move_to_pos_accepted(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) {
    std::thread {
        std::bind(
            &ODescNode::move_to_pos_execute,
            this,
            std::placeholders::_1
        ),
        goal_handle
    }.detach();
}

/// @brief goal function to adjust the precision we expect from the motor
/// @param current_pos current motor position
/// @param goal the goal position
/// @return true if current pos is close enough to the goal
bool goal_achieved(double current_pos, double goal) {
    return goal - 0.1 < current_pos && current_pos < goal + 0.1;
}

void ODescNode::move_to_pos_execute(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) {
    rclcpp::Rate loop_rate(1);
    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<MoveToPos::Feedback>();
    auto& current_position = feedback->current_position;
    auto result = std::make_shared<MoveToPos::Result>();

    if (motors_.find(goal->id) == motors_.end()) {
        // TODO: is this really what we want, if no state in map then possibly dead motor?
        motors_.emplace(goal->id, MotorState {});
    }
    auto& motor = motors_.at(goal->id);

    send_position_target_req(goal->id, goal->target_position);

    while(true) {
        // Check if there is a cancel request
        if (goal_handle->is_canceling()) {
            result->position_achieved = current_position;
            result->success = false;
            
            goal_handle->canceled(result);
            return;
        }

        // Update sequence
        current_position = motor.pos_est;
        send_position_est_req(goal->id);

        // Publish feedback
        goal_handle->publish_feedback(feedback);

        if (rclcpp::ok() && motor.error) {
            result->position_achieved = current_position;
            result->success = false;
            goal_handle->abort(result);
            return;
        }

        if (goal_achieved(current_position, goal->target_position)) {
            break;
        }

        loop_rate.sleep();
    }

    // Check if goal is done
    if (rclcpp::ok()) {
        result->position_achieved = current_position;
        result->success = true;
        goal_handle->succeed(result);
    }
}

// Actions
// 
// Send requests

using Array = std::array<uint8_t, 8>;

bool ODescNode::send_position_est_req(uint8_t motor_id) {
    {
        std::lock_guard lock(position_mutex);
        position_reply.reset();
    }

    CanFrame frame {};

    frame.id = create_id(motor_id, GetEncoderEst);
    frame.is_rtr = true;

    pub_->publish(frame);

    std::unique_lock lock(position_mutex);
    // TODO: 50ms works for one motor on canbus, but might need to be revised if it fails with more devices on the bus
    if (!position_received_flag.wait_for(lock, 50ms, [&]{ return position_reply.has_value(); })) {
        return false; // timeout
    }

    RCLCPP_INFO(get_logger(), "In send_position_est_req: %f", motors_.at(motor_id).pos_est);

    return true;
}

void ODescNode::send_position_target_req(
    uint8_t motor_id,
    float target
) const {
    CanFrame frame {};

    Array data {};
    write_le(data.data(), target);

    frame.id = create_id(motor_id, SetInputPos);
    frame.dlc = 8;
    frame.data = data;

    pub_->publish(frame);
}

void ODescNode::send_velocity_target_req(
    uint8_t motor_id,
    float target
) const { 
    CanFrame frame {};

    Array data {};
    write_le(data.data(), target);

    frame.id = create_id(motor_id, SetInputVel);
    frame.dlc = 8;
    frame.data = data;

    pub_->publish(frame);
}

void ODescNode::send_reboot_req(uint8_t motor_id) const {
    CanFrame frame {};

    frame.id = create_id(motor_id, Reboot);
    frame.dlc = 0;

    pub_->publish(frame);
}

void ODescNode::send_clear_errors_req(uint8_t motor_id) const {
    CanFrame frame {};

    frame.id = create_id(motor_id, ClearErrors);
    frame.dlc = 0;

    pub_->publish(frame);
}

void ODescNode::send_axis_state_req(
    uint8_t motor_id,
    AxisState state
) const {
    CanFrame frame {};

    Array data {};
    write_le(data.data(), static_cast<uint32_t>(state));

    frame.id = create_id(motor_id, SetRequestedState);
    frame.dlc = 4;
    frame.data = data;

    pub_->publish(frame);
}

void ODescNode::send_control_state_req(
    uint8_t motor_id,
    InputMode input,
    ControlMode control
) const {
    CanFrame frame {};

    Array data {};
    write_le(data.data(), static_cast<uint32_t>(control));
    write_le(data.data() + 4, static_cast<uint32_t>(input));

    frame.id = create_id(motor_id, SetControlMode);
    frame.dlc = 8;
    frame.data = data;

    pub_->publish(frame);
}

// Send requests
