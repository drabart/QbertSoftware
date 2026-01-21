#include "can_msgs/msg/frame.hpp"
#include <rclcpp/executors.hpp>

#include "esp_node.hpp"
#include "can_utils.hpp"
#include "esp_msgs.hpp"

using CanFrame = can_msgs::msg::Frame;

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<EspNode>());
    rclcpp::shutdown();
    return 0;
}

void EspNode::CAN_recv(const CanFrame& frame) {
    uint8_t cmd = extract_cmd(frame.id);
    if (frame.is_rtr) { return; }
    if (auto func = callbacks_.find(static_cast<EspCommand>(cmd)); func != callbacks_.end()) { func->second(frame); }
}

// Helper

bool EspNode::is_active(uint8_t esp_id) const {
    if (auto it = devices_.find(esp_id); it != devices_.end()) {
        return !it->second.error;
    }

    return false;
}

// Helper
//
// Receive callbacks

void EspNode::heartbeat(const CanFrame& frame) {
    Msg_HeartBeat _ = frame;

    uint8_t id = extract_id(frame.id);
    if (id < 0b100000) { return; }

    if (auto it = devices_.find(id); it == devices_.end()) {
        devices_.emplace(id, EspState {});
    }

    EspState& esp = devices_.at(id);
    esp.error = false;
}

void EspNode::axe_pos(const CanFrame& frame) {
    Msg_GetAxePos axe_pos = frame;
    uint8_t id = extract_id(frame.id);

    if (auto it = devices_.find(id); it == devices_.end()) {
        return;
    }

    EspState& esp = devices_.at(id);
    esp.axe_pos_0 = axe_pos.pos_0;
    esp.axe_pos_1 = axe_pos.pos_1;
}

void EspNode::gripper_state(const CanFrame& frame) {
    Msg_GetGripperState gripper_state = frame;
    uint8_t id = extract_id(frame.id);

    if (auto it = devices_.find(id); it == devices_.end()) {
        return;
    }

    EspState& esp = devices_.at(id);
    esp.grippers_extended = gripper_state.extended;
}

// Receive callbacks
//
// Services

void EspNode::gripper_state_srv(
    const std::shared_ptr<GripperState::Request> req,
    std::shared_ptr<GripperState::Response> res
) const {
    send_set_gripper_state_req(req->id, req->state);
    res->success = true;

    send_get_gripper_state_req(req->id);
}

// Services
//
// Actions

rclcpp_action::GoalResponse EspNode::move_to_pos_goal(
    const rclcpp_action::GoalUUID & _,
    std::shared_ptr<const MoveToPos::Goal> goal
) const {
    if (!is_active(goal->id)) { return rclcpp_action::GoalResponse::REJECT; }
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse EspNode::move_to_pos_cancel(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) const {
    const auto goal = goal_handle->get_goal();
    // TODO: figure out how to idle esp
    return rclcpp_action::CancelResponse::ACCEPT;
}

void EspNode::move_to_pos_accepted(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) {
    std::thread {
        std::bind(
            &EspNode::move_to_pos_execute,
            this,
            std::placeholders::_1
        ),
        goal_handle
    }.detach();
}

/// @brief goal function to adjust the precision we expect
/// @return true if current pos is close enough to the goal
bool goal_achieved(double current_pos, double goal) {
    return goal - 0.3 < current_pos && current_pos < goal + 0.3;
}

void EspNode::move_to_pos_execute(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle
) {
    rclcpp::Rate loop_rate(1);
    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<MoveToPos::Feedback>();
    auto& current_position = feedback->current_position;
    auto result = std::make_shared<MoveToPos::Result>();

    if (devices_.find(goal->id) == devices_.end()) {
        // TODO: is this really what we want, if no state in map then possibly dead motor?
        devices_.emplace(goal->id, EspState {});
    }
    auto& esp = devices_.at(goal->id);

    send_set_axe_pos_req(goal->id, goal->target_position);

    while(true) {
        // Check if there is a cancel request
        if (goal_handle->is_canceling()) {
            result->position_achieved = current_position;
            result->success = false;
            
            goal_handle->canceled(result);
            return;
        }

        // Update sequence
        current_position = (esp.axe_pos_0 + esp.axe_pos_1) / 2;
        send_get_axe_pos_req(goal->id);

        // Publish feedback
        goal_handle->publish_feedback(feedback);

        if (rclcpp::ok() && esp.error) {
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

void EspNode::send_set_axe_pos_req(uint8_t esp_id, float pos) const {
    CanFrame frame {};

    Array data {};
    write_le(data.data(), pos);

    frame.id = create_id(esp_id, SetAxePos);
    frame.dlc = 4;
    frame.data = data;

    pub_->publish(frame);
}

void EspNode::send_set_gripper_state_req(uint8_t esp_id, bool extended) const {
    CanFrame frame {};

    Array data {};
    write_le(data.data(), extended);

    frame.id = create_id(esp_id, SetGripperState);
    frame.dlc = 1;
    frame.data = data;

    pub_->publish(frame);
}

void EspNode::send_get_axe_pos_req(uint8_t esp_id) const {
    CanFrame frame {};

    frame.id = create_id(esp_id, GetAxePos);
    frame.is_rtr = true;

    pub_->publish(frame);
}

void EspNode::send_get_gripper_state_req(uint8_t esp_id) const {
    CanFrame frame {};

    frame.id = create_id(esp_id, GetGripperState);
    frame.is_rtr = true;

    pub_->publish(frame);
}

// Send requests
