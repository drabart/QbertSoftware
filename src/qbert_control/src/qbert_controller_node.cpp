#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <chrono>

using namespace std::chrono_literals;

class QbertNode : public rclcpp::Node
{
public:
    QbertNode() : Node("qbert_node")
    {
        // List of service names
        std::vector<std::string> services = {
            "extend_rollers",
            "retract_rollers",
            "extend_grippers",
            "retract_grippers",
            "extend_compressors",
            "retract_compressors",
            "tool_disc_set_start",
            "split_section",
            "go_to_next_section"
        };

        // Initialize clients for each service
        for (const auto &name : services)
        {
            auto client = this->create_client<std_srvs::srv::Trigger>("/" + name);
            clients_[name] = client;

            // Wait for service to be available
            while (!client->wait_for_service(std::chrono::seconds(1)))
            {
                RCLCPP_INFO(this->get_logger(), "Waiting for service: %s", name.c_str());
            }

            RCLCPP_INFO(this->get_logger(), "Service ready: %s", name.c_str());
        }

        pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/gantry_controller/commands", 10
        );

        // Services to trigger actions
        qbert_srv_ = this->create_service<std_srvs::srv::Trigger>(
            "split_cable",
            std::bind(&QbertNode::split_cable_callback, this, std::placeholders::_1, std::placeholders::_2)
        );
    }

private:
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_;
    std::map<std::string, rclcpp::Client<std_srvs::srv::Trigger>::SharedPtr> clients_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr qbert_srv_;

    bool send_and_await_request(rclcpp::Client<std_srvs::srv::Trigger>::SharedPtr client)
    {
        auto request = std::make_shared<std_srvs::srv::Trigger::Request>();
        auto future_result = client->async_send_request(request);

        RCLCPP_INFO(this->get_logger(), "Sending request");

        rclcpp::sleep_for(5s);

        return true;
    }

    void move_gantry_to(double j1)
    {
        std_msgs::msg::Float64MultiArray msg;
        msg.data = {j1};
        pub_->publish(msg);
    }

    void split_cable_callback(
        const std::shared_ptr<std_srvs::srv::Trigger::Request>,
        std::shared_ptr<std_srvs::srv::Trigger::Response> res)
    {
        bool success;

        success = send_and_await_request(clients_["extend_rollers"]);
        if (!success) goto service_failed;

        success = send_and_await_request(clients_["tool_disc_set_start"]);
        if (!success) goto service_failed;

        move_gantry_to(-0.19);

        success = send_and_await_request(clients_["extend_grippers"]);
        if (!success) goto service_failed;

        for (int i = 0; i < 6; i++)
        {
            success = send_and_await_request(clients_["split_section"]);
            if (!success) goto service_failed;

            success = send_and_await_request(clients_["go_to_next_section"]);
            if (!success) goto service_failed;
        }

        success = send_and_await_request(clients_["retract_grippers"]);
        if (!success) goto service_failed;

        move_gantry_to(0.08);

        success = send_and_await_request(clients_["extend_grippers"]);
        if (!success) goto service_failed;

        success = send_and_await_request(clients_["extend_compressors"]);
        if (!success) goto service_failed;

        success = send_and_await_request(clients_["retract_compressors"]);
        if (!success) goto service_failed;

        success = send_and_await_request(clients_["retract_grippers"]);
        if (!success) goto service_failed;

        move_gantry_to(0.27);

        success = send_and_await_request(clients_["retract_rollers"]);
        if (!success) goto service_failed;

        res->success = true;
        res->message = "Split the cable";
        return;

service_failed:
        res->success = false;
        res->message = "Failed to split";
    }
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<QbertNode>());
    rclcpp::shutdown();
    return 0;
}
