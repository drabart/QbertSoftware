#include "can_msgs/msg/frame.hpp"
#include <rclcpp/node.hpp>

using CanFrame = can_msgs::msg::Frame;

class CanNode : public rclcpp::Node {
protected:
    explicit CanNode( const std::string& node_name): Node(node_name) {
        sub_ = this->create_subscription<CanFrame>(
            "/from_canbus",
            10,
            std::bind(&CanNode::CAN_recv, this, std::placeholders::_1)
        );
        pub_ = this->create_publisher<CanFrame>("/to_canbus", 10);
    }

    uint8_t extract_id(uint32_t id) const { return (id >> 5) & 0b111111; }
    uint8_t extract_cmd(uint32_t id) const { return id & 0b11111; }

    virtual void CAN_recv(const CanFrame& frame) const = 0;

    rclcpp::Publisher<CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<CanFrame>::SharedPtr sub_;
};
