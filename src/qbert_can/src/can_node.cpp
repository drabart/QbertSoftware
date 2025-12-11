#include <chrono>

#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <sys/socket.h>
#include <sys/ioctl.h>

#include "rclcpp/rclcpp.hpp"
#include "qbert_msgs/msg/can_frame.hpp"

using namespace std::chrono_literals;

class CanNode : public rclcpp::Node
{
private:
    rclcpp::Publisher<qbert_msgs::msg::CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<qbert_msgs::msg::CanFrame>::SharedPtr sub_;

public:
    CanNode() : Node("can_node")
    {
        sub_ = this->create_subscription<qbert_msgs::msg::CanFrame>(
            "/can_tx", 10, std::bind(&CanNode::send_request, this, std::placeholders::_1));
        pub_ = this->create_publisher<qbert_msgs::msg::CanFrame>("/can_rx", 10);

        int sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (sock < 0) {
            throw std::runtime_error("CAN device not found");
        }

        struct ifreq ifr{};
        std::strcpy(ifr.ifr_name, "can0");
        if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
            throw std::runtime_error("ioctl error");
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
            throw std::runtime_error("socket bind error");
        }

        RCLCPP_INFO(this->get_logger(), "can_node ready");
    }

private:
    // --- Service callbacks ---
    void send_request(const qbert_msgs::msg::CanFrame& msg) const {
        
    }
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CanNode>());
    rclcpp::shutdown();
    return 0;
}
