#pragma once

#include "can_msgs/msg/frame.hpp"
#include <rclcpp/node.hpp>

using CanFrame = can_msgs::msg::Frame;

class CanNode : public rclcpp::Node {
protected:
    explicit CanNode( const std::string& node_name): Node(node_name) {
        can_rx_group_ = this->create_callback_group(
            rclcpp::CallbackGroupType::Reentrant);

        srv_group_ = this->create_callback_group(
            rclcpp::CallbackGroupType::MutuallyExclusive);

        rclcpp::SubscriptionOptions sub_opts;
        sub_opts.callback_group = can_rx_group_;

        sub_ = this->create_subscription<CanFrame>(
            "/from_can_bus",
            10,
            std::bind(&CanNode::CAN_recv, this, std::placeholders::_1),
            sub_opts
        );
        pub_ = this->create_publisher<CanFrame>("/to_can_bus", 10);
    }

    uint8_t extract_id(uint32_t id) const { return (id >> 5) & 0b111111; }
    uint8_t extract_cmd(uint32_t id) const { return id & 0b11111; }

    uint32_t create_id(uint8_t can_id, uint8_t cmd) const {
        return ((can_id & 0b111111) << 5) | (cmd & 0b11111);
    }

    virtual void CAN_recv(const CanFrame& frame) = 0;
    virtual bool is_active(uint8_t _) const { return false; }

    rclcpp::Publisher<CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<CanFrame>::SharedPtr sub_;
    rclcpp::CallbackGroup::SharedPtr can_rx_group_;
    rclcpp::CallbackGroup::SharedPtr srv_group_;
};
