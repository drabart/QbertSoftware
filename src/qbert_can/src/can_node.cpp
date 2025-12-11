#include <chrono>

#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <sys/socket.h>
#include <sys/ioctl.h>

#include "rclcpp/rclcpp.hpp"
#include "can_msg.hpp"
#include "qbert_msgs/msg/can_frame.hpp"

using namespace std::chrono_literals;

class CanNode : public rclcpp::Node
{
private:
    rclcpp::Publisher<qbert_msgs::msg::CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<qbert_msgs::msg::CanFrame>::SharedPtr sub_;
    int sock_;
    std::thread recv_thread_;
    std::atomic<bool> running_{true};

public:
    CanNode() : Node("can_node")
    {
        sub_ = this->create_subscription<qbert_msgs::msg::CanFrame>(
            "/can_tx", 10, std::bind(&CanNode::send_request, this, std::placeholders::_1));
        pub_ = this->create_publisher<qbert_msgs::msg::CanFrame>("/can_rx", 10);

        // init CAN bus socket
        sock_ = socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (sock_ < 0) {
            throw std::runtime_error("CAN device not found");
        }

        struct ifreq ifr{};
        std::strcpy(ifr.ifr_name, "can0");
        if (ioctl(sock_, SIOCGIFINDEX, &ifr) < 0) {
            throw std::runtime_error("ioctl error");
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (bind(sock_, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
            throw std::runtime_error("socket bind error");
        }

        RCLCPP_INFO(this->get_logger(), "can_node ready");

        // start receive thread
        recv_thread_ = std::thread([this]() { receive_loop(); });
    }

    ~CanNode() {
        running_ = false;
        if (recv_thread_.joinable()) recv_thread_.join();
        close(sock_);
    }

private:
    void send_request(const qbert_msgs::msg::CanFrame& msg) const {
        CANMsg can_msg{};

        can_msg.frame.can_id = msg.id;
        can_msg.frame.can_dlc = msg.dlc;
        
        memcpy(can_msg.frame.data, msg.data.data(), msg.dlc);

        can_msg.send(sock_);
    }

    void receive_loop() {
        struct can_frame frame{};
        while (running_) {
            int nbytes = read(sock_, &frame, sizeof(frame));
            if (nbytes > 0) {
                qbert_msgs::msg::CanFrame msg;
                msg.id = frame.can_id;
                msg.dlc = frame.can_dlc;
                for (int i = 0; i < frame.can_dlc; i++)
                {
                    msg.data[i] = frame.data[i];
                }

                pub_->publish(msg);
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
        }
    }
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CanNode>());
    rclcpp::shutdown();
    return 0;
}
