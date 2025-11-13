#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <map>
#include <string>
#include <chrono>
#include <cmath>

using namespace std::chrono_literals;

class ToolDiscNode : public rclcpp::Node
{
public:
    ToolDiscNode() : Node("tool_disc_node")
    {
        pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/tool_disc_controller/commands", 10
        );

        joint_state_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states",
            10,
            std::bind(&ToolDiscNode::jointStateCallback, this, std::placeholders::_1)
        );

        // Services to trigger actions
        set_start_srv_ = this->create_service<std_srvs::srv::Trigger>(
            "tool_disc_set_start",
            std::bind(&ToolDiscNode::set_start_position_callback, this, std::placeholders::_1, std::placeholders::_2));

        split_section_srv_ = this->create_service<std_srvs::srv::Trigger>(
            "split_section",
            std::bind(&ToolDiscNode::split_section_callback, this, std::placeholders::_1, std::placeholders::_2));
        
        go_to_next_section_srv_ = this->create_service<std_srvs::srv::Trigger>(
            "go_to_next_section",
            std::bind(&ToolDiscNode::rotate_to_next_section_callback, this, std::placeholders::_1, std::placeholders::_2));

        RCLCPP_INFO(this->get_logger(), "ToolDiscNode ready");
    }

private:
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
    
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr set_start_srv_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr split_section_srv_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr go_to_next_section_srv_;
    std::map<std::string, double> joint_positions_;

    void jointStateCallback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        for (size_t i = 0; i < msg->name.size(); i++) {
            joint_positions_[msg->name[i]] = msg->position[i];
        }
    }

    // --- Helper function ---
    void send_positions(double j1, double j2)
    {
        std_msgs::msg::Float64MultiArray msg;
        msg.data = {j1, j2};
        pub_->publish(msg);
    }

    void set_start_position_callback(
        const std::shared_ptr<std_srvs::srv::Trigger::Request>,
        std::shared_ptr<std_srvs::srv::Trigger::Response> res)
    {
        send_positions(-0.2, -0.1);

        res->success = true;
        res->message = "Start position set";
    }

    void split_section_callback(
        const std::shared_ptr<std_srvs::srv::Trigger::Request>,
        std::shared_ptr<std_srvs::srv::Trigger::Response> res)
    {
        double J2_A_rotor_pos = joint_positions_["J2_A_rotor"];
        double joint_J3_A_tool_disc = joint_positions_["joint_J3_A_tool_disc"];

        send_positions(J2_A_rotor_pos + 0.22, joint_J3_A_tool_disc + 0.05);

        rclcpp::sleep_for(2s);

        send_positions(J2_A_rotor_pos, joint_J3_A_tool_disc);

        res->success = true;
        res->message = "Split section";
    }

    void rotate_to_next_section_callback(
        const std::shared_ptr<std_srvs::srv::Trigger::Request>,
        std::shared_ptr<std_srvs::srv::Trigger::Response> res)
    {
        double J2_A_rotor_pos = joint_positions_["J2_A_rotor"];
        double joint_J3_A_tool_disc = joint_positions_["joint_J3_A_tool_disc"];

        double next_rotor_pos = J2_A_rotor_pos + M_PI / 3;
        if (next_rotor_pos > M_PI)
        {
            next_rotor_pos -= 2 * M_PI;
        }

        send_positions(next_rotor_pos, joint_J3_A_tool_disc);

        res->success = true;
        res->message = "Got to next section";
    }
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ToolDiscNode>());
  rclcpp::shutdown();
  return 0;
}
