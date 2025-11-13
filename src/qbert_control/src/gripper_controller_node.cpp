#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <std_srvs/srv/trigger.hpp>

class GripperNode : public rclcpp::Node
{
public:
  GripperNode() : Node("gripper_node")
  {
    pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
        "/gripper_controller/commands", 10);

    // Services to trigger actions
    extend_srv_ = this->create_service<std_srvs::srv::Trigger>(
        "extend_grippers",
        std::bind(&GripperNode::extend_callback, this, std::placeholders::_1, std::placeholders::_2));

    retract_srv_ = this->create_service<std_srvs::srv::Trigger>(
        "retract_grippers",
        std::bind(&GripperNode::retract_callback, this, std::placeholders::_1, std::placeholders::_2));

    RCLCPP_INFO(this->get_logger(), "GripperNode ready");
  }

private:
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr extend_srv_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr retract_srv_;

  // --- Helper function ---
  void send_positions(double j1, double j2, double j3, double j4)
  {
    std_msgs::msg::Float64MultiArray msg;
    msg.data = {j1, j2, j3, j4};
    pub_->publish(msg);
  }

  // --- Service callbacks ---
  void extend_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request>,
      std::shared_ptr<std_srvs::srv::Trigger::Response> res)
  {
    send_positions(-0.04, -0.04, -0.04, -0.04);
    res->success = true;
    res->message = "Grippers extended";
  }

  void retract_callback(
      const std::shared_ptr<std_srvs::srv::Trigger::Request>,
      std::shared_ptr<std_srvs::srv::Trigger::Response> res)
  {
    send_positions(0.0, 0.0, 0.0, 0.0);
    res->success = true;
    res->message = "Grippers retracted";
  }
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GripperNode>());
  rclcpp::shutdown();
  return 0;
}
