#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

#include "std_srvs/srv/trigger.hpp"

#include "odesc_msgs.hpp"
#include "qbert_msgs/msg/can_frame.hpp"
#include "qbert_msgs/srv/home.hpp"
#include "qbert_msgs/srv/move_with_vel.hpp"
#include "qbert_msgs/srv/setup_drive.hpp"
#include "qbert_msgs/action/move_to_pos.hpp"

using namespace std::chrono_literals;

struct MotorData {
    double position_estimate;
};

class ODescNode : public rclcpp::Node
{
private:
    using MoveToPos = qbert_msgs::action::MoveToPos;
    using TriggerService = std_srvs::srv::Trigger;
    using CanFrame = qbert_msgs::msg::CanFrame;

    rclcpp::Publisher<CanFrame>::SharedPtr pub_;
    rclcpp::Subscription<CanFrame>::SharedPtr sub_;
    rclcpp::Service<TriggerService>::SharedPtr reboot_srv_;
    rclcpp::Service<TriggerService>::SharedPtr clear_error_srv_;
    rclcpp_action::Server<MoveToPos>::SharedPtr move_to_pos_action_;

    using CommandID = int;
    using DeviceID = int;

    std::unordered_map<CommandID, std::function<void(CANMsg)>> command_callbacks_;
    std::unordered_map<DeviceID, MotorData> motor_data_;

public:
    ODescNode() : Node("odesc_node")
    {
        pub_ = this->create_publisher<CanFrame>(
            "/can_tx", 10);
        sub_ = this->create_subscription<CanFrame>(
            "/can_rx", 10, bind(&ODescNode::can_message_received_callback, this, std::placeholders::_1));

        this->move_to_pos_action_ = rclcpp_action::create_server<MoveToPos>(
            this,
            "/move_to_pos",
            std::bind(&ODescNode::handle_move_to_pos_goal, this, std::placeholders::_1, std::placeholders::_2),
            std::bind(&ODescNode::handle_move_to_pos_cancel, this, std::placeholders::_1),
            std::bind(&ODescNode::handle_move_to_pos_accepted, this, std::placeholders::_1));

        command_callbacks_[MotorCommandID::GetEncoderEst] = [this](CANMsg msg) {position_received(msg); };

        RCLCPP_INFO(this->get_logger(), "ODescNode ready");
    }

private:
    /// @brief Callback for receiving CAN frames, needs to filter only the relevant ones
    /// @param msg 
    void can_message_received_callback(const qbert_msgs::msg::CanFrame& ros_msg) const {
        CANMsg msg{};
        msg.from_ros_msg(ros_msg);

        CommandID command_id = msg.frame.can_id & 0x01F;
        if (command_callbacks_.find(command_id) != command_callbacks_.end()) {
            std::invoke(command_callbacks_.at(command_id), msg);
        }
    }

    void position_received(CANMsg msg) {
        Msg_GetEncoderEst est = msg;
        est.recv_callback(msg.frame);

        DeviceID device_id = (msg.frame.can_id & 0x7E0) >> 5;
        if (motor_data_.find(device_id) == motor_data_.end()) {
            motor_data_.insert({device_id, MotorData{}});
        }

        motor_data_.at(device_id).position_estimate = est.pos_estimate;
    }

    // TODO heartbeat

    void send_position_est_request(DeviceID motor_id) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_GetEncoderEst(motor_id);
        CanFrame ros_msg = msg.to_ros_msg();
        pub_->publish(ros_msg);
    }

    void send_position_target(DeviceID motor_id, float target) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_SetInputPos(motor_id, target);
        CanFrame ros_msg = msg.to_ros_msg();
        pub_->publish(ros_msg);
    }

    rclcpp_action::GoalResponse handle_move_to_pos_goal(
        const rclcpp_action::GoalUUID & uuid,
        std::shared_ptr<const MoveToPos::Goal> goal) {
        
        RCLCPP_INFO(this->get_logger(), "Received goal for motor: %d of pos: %.2f", goal->motor, goal->target_position);
        (void)uuid;
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_move_to_pos_cancel(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle) {

        RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");
        (void)goal_handle;

        // TODO add stopping motor here
        return rclcpp_action::CancelResponse::ACCEPT;
    }

    void handle_move_to_pos_accepted(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle) {

        std::thread{std::bind(&ODescNode::move_to_pos_execute, this, std::placeholders::_1), goal_handle}.detach();
    }

    /// @brief goal function to adjust the precision we expect from the motor
    /// @param current_pos current motor position
    /// @param goal the goal position
    /// @return true if current pos is close enough to the goal
    bool goal_achieved(double current_pos, double goal) {
        return goal - 0.1 < current_pos && current_pos < goal + 0.1;
    }

    void move_to_pos_execute(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle) {

        RCLCPP_INFO(this->get_logger(), "Executing goal");
        rclcpp::Rate loop_rate(1);
        const auto goal = goal_handle->get_goal();
        auto feedback = std::make_shared<MoveToPos::Feedback>();
        auto & current_position = feedback->current_position;
        auto result = std::make_shared<MoveToPos::Result>();

        DeviceID motor_id = goal.get()->motor;
        if (motor_data_.find(motor_id) == motor_data_.end()) {
            motor_data_[motor_id] = MotorData{};
        }

        send_position_target(motor_id, goal.get()->target_position);

        while(true) {
            // Check if there is a cancel request
            if (goal_handle->is_canceling()) {
                result->position_achieved = current_position;
                result->success = false;
                
                goal_handle->canceled(result);
                RCLCPP_INFO(this->get_logger(), "Goal canceled");
                return;
            }

            // Update sequence
            current_position = motor_data_[motor_id].position_estimate;
            send_position_est_request(motor_id);
            // Publish feedback
            goal_handle->publish_feedback(feedback);
            RCLCPP_INFO(this->get_logger(), "Publish feedback");

            if (goal_achieved(current_position, goal.get()->target_position)) {
                break;
            }

            loop_rate.sleep();
        }

        // Check if goal is done
        if (rclcpp::ok()) {
            result->position_achieved = current_position;
            result->success = true;
            goal_handle->succeed(result);
            RCLCPP_INFO(this->get_logger(), "Goal succeeded");
        }
    }
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ODescNode>());
    rclcpp::shutdown();
    return 0;
}
