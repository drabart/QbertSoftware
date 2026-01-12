#pragma once

#include "can_msgs/msg/frame.hpp"
#include <rclcpp/service.hpp>
#include <rclcpp_action/create_server.hpp>
#include <rclcpp_action/server.hpp>

#include "esp_msgs.hpp"
#include "can_node.hpp"
#include "qbert_msgs/action/move_to_pos.hpp"
#include "qbert_msgs/srv/gripper_state.hpp"

using CanFrame = can_msgs::msg::Frame;
using GripperState = qbert_msgs::srv::GripperState;
using MoveToPos = qbert_msgs::action::MoveToPos;

class EspNode : public CanNode {
public:
    explicit EspNode() : CanNode("ESP_Node") {
        using namespace std::placeholders;

        gripper_state_srv_ = create_service<GripperState>(
            "/esp/gripper_state",
            std::bind(&EspNode::gripper_state_srv, this, _1, _2)
        );

        move_to_pos_action_ = rclcpp_action::create_server<MoveToPos>(
            this,
            "/esp/move_to_pos",
            std::bind(&EspNode::move_to_pos_goal, this, _1, _2),
            std::bind(&EspNode::move_to_pos_cancel, this, _1),
            std::bind(&EspNode::move_to_pos_accepted, this, _1)
        );

        callbacks_.emplace(HeartBeat, [this](CanFrame frame) { heartbeat(frame); });
        callbacks_.emplace(GetAxePos, [this](CanFrame frame) { axe_pos(frame); });
        callbacks_.emplace(GetGripperState, [this](CanFrame frame) { gripper_state(frame); });
    }

private:
    // Member fields
    rclcpp::Service<GripperState>::SharedPtr gripper_state_srv_;
    rclcpp_action::Server<MoveToPos>::SharedPtr move_to_pos_action_;

    struct EspState {
        float axe_pos_0;
        float axe_pos_1;
        bool grippers_extended;
        bool error;
    };

    std::unordered_map<uint8_t, EspState> devices_;
    std::unordered_map<EspCommand, std::function<void (const CanFrame&)>> callbacks_;

    // Member fields
    //
    // Helper functions

    void CAN_recv(const CanFrame& frame) override;

    bool is_active(uint8_t esp_id) const override;

    // Helper functions
    //
    // Receive callbacks

    void heartbeat(const CanFrame& frame);

    void axe_pos(const CanFrame& frame);

    void gripper_state(const CanFrame& frame);

    // Receive callbacks
    //
    // Services

    void gripper_state_srv(
        const std::shared_ptr<GripperState::Request> req,
        std::shared_ptr<GripperState::Response> res
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

    void send_set_axe_pos_req(
        uint8_t esp_id,
        float pos
    ) const;

    void send_set_gripper_state_req(
        uint8_t esp_id,
        bool extended
    ) const;

    void send_get_axe_pos_req(uint8_t esp_id) const;
    void send_get_gripper_state_req(uint8_t esp_id) const;
};
