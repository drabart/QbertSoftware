#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"
#include "odesc_msgs.hpp"
#include "qbert_msgs/msg/can_frame.hpp"

using namespace std::chrono_literals;

class ODescNode : public rclcpp::Node
{
private:
    rclcpp::Publisher<qbert_msgs::msg::CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<qbert_msgs::msg::CanFrame>::SharedPtr sub_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr reboot_srv_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr clear_error_srv_;

public:
  ODescNode() : Node("odesc_node")
  {
    pub_ = this->create_publisher<qbert_msgs::msg::CanFrame>(
        "/can_tx", 10);
    sub_ = this->create_subscription<qbert_msgs::msg::CanFrame>(
        "/can_rx", 10, bind(&ODescNode::can_message_received_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "ODescNode ready");
  }

private:
    void can_message_received_callback(const qbert_msgs::msg::CanFrame& msg) const {

    }
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ODescNode>());
  rclcpp::shutdown();
  return 0;
}
