#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

#include "odesc_msgs.hpp"
#include "qbert_msgs/msg/can_frame.hpp"

#include "qbert_msgs/srv/motor.hpp"
#include "qbert_msgs/srv/setup_drive.hpp"
#include "qbert_msgs/srv/move_with_vel.hpp"

#include "qbert_msgs/action/move_to_pos.hpp"

using namespace std::chrono_literals;

enum AxisState {
    IDLE = 1,
    CLOSED_LOOP_CONTROL = 8,
    HOMING = 11,
};

enum InputMode {
    INACTIVE = 0,
    PASSTROUGH = 1,
    TRAP_TRAJ = 5,
};

enum ControlMode {
    VELOCITY_CONTROL = 2,
    POSITION_CONTROL = 3,
};

struct MotorData {
    double position_estimate;
    int32_t current_state;
    bool error;
};

class ODescNode : public rclcpp::Node
{
private:
    using MoveToPos = qbert_msgs::action::MoveToPos;
    using MotorService = qbert_msgs::srv::Motor;
    using SetupDrive = qbert_msgs::srv::SetupDrive;
    using MoveWithVel = qbert_msgs::srv::MoveWithVel;
    using CanFrame = qbert_msgs::msg::CanFrame;

    rclcpp::Publisher<CanFrame>::SharedPtr can_pub_;
    rclcpp::Subscription<CanFrame>::SharedPtr can_sub_;
    
    rclcpp::Service<MotorService>::SharedPtr reboot_srv_;
    rclcpp::Service<MotorService>::SharedPtr clear_error_srv_;
    rclcpp::Service<MotorService>::SharedPtr home_srv_;
    rclcpp::Service<MotorService>::SharedPtr motor_ready_srv_;
    rclcpp::Service<SetupDrive>::SharedPtr setup_srv_;
    rclcpp::Service<MoveWithVel>::SharedPtr move_with_vel_srv_;
    
    rclcpp_action::Server<MoveToPos>::SharedPtr move_to_pos_action_;

    using CommandID = int;
    using DeviceID = int;

    std::unordered_map<CommandID, std::function<void(CANMsg)>> command_callbacks_;
    std::unordered_map<DeviceID, MotorData> motor_data_;

public:
    ODescNode() : Node("odesc_node") {
        using namespace std::placeholders;

        can_pub_ = this->create_publisher<CanFrame>(
            "/can_tx", 10);
        can_sub_ = this->create_subscription<CanFrame>(
            "/can_rx", 10, bind(&ODescNode::can_message_received_callback, this, std::placeholders::_1));

        this->move_to_pos_action_ = rclcpp_action::create_server<MoveToPos>(
            this,
            "/move_to_pos",
            std::bind(&ODescNode::handle_move_to_pos_goal, this, std::placeholders::_1, std::placeholders::_2),
            std::bind(&ODescNode::handle_move_to_pos_cancel, this, std::placeholders::_1),
            std::bind(&ODescNode::handle_move_to_pos_accepted, this, std::placeholders::_1));

        // Initialize services
        reboot_srv_ = this->create_service<MotorService>(
            "/reboot_motor", std::bind(&ODescNode::reboot_callback, this, _1, _2));

        clear_error_srv_ = this->create_service<MotorService>(
            "/clear_motor_error", std::bind(&ODescNode::clear_error_callback, this, _1, _2));

        home_srv_ = this->create_service<MotorService>(
            "/home_motor", std::bind(&ODescNode::home_callback, this, _1, _2));

        setup_srv_ = this->create_service<SetupDrive>(
            "/setup_drive", std::bind(&ODescNode::setup_callback, this, _1, _2));

        move_with_vel_srv_ = this->create_service<MoveWithVel>(
            "/move_with_velocity", std::bind(&ODescNode::move_with_vel_callback, this, _1, _2));

        motor_ready_srv_ = this->create_service<MotorService>(
            "/motor_ready", std::bind(&ODescNode::motor_ready_callback, this, _1, _2));
        
        // Setup can message listeners
        command_callbacks_[MotorCommandID::GetEncoderEst] = [this](CANMsg msg) {position_received(msg); };
        command_callbacks_[MotorCommandID::HeartBeat] = [this](CANMsg msg) {heartbeat_received(msg); };

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

        motor_data_.at(device_id).position_estimate = est.pos_estimate;
    }

    void heartbeat_received(CANMsg msg) {
        Msg_HeartBeat heart_beat = msg;
        heart_beat.recv_callback(msg.frame);

        DeviceID device_id = (msg.frame.can_id & 0x7E0) >> 5;
        if (motor_data_.find(device_id) == motor_data_.end()) {
            motor_data_.insert({device_id, MotorData{}});
        }

        auto &motor_data = motor_data_.at(device_id);
        motor_data.current_state = heart_beat.axis_current_state;
        motor_data.error = heart_beat.axis_error | heart_beat.controller_error | heart_beat.encoder_error | heart_beat.motor_error;
    }

    bool device_active(DeviceID device_id) {
        if (motor_data_.find(device_id) == motor_data_.end()) {
            return false;
        }

        return !motor_data.error;
    }

    void send_position_est_request(DeviceID motor_id) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_GetEncoderEst(motor_id);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_position_target(DeviceID motor_id, float target) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_SetInputPos(motor_id, target);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_velocity_target(DeviceID motor_id, float target) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_SetInputVel(motor_id, target);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_reboot_request(DeviceID motor_id) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_Reboot(motor_id);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_clear_errors_request(DeviceID motor_id) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_ClearErrors(motor_id);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_axis_state_request(DeviceID motor_id, AxisState state) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_SetRequestedState(motor_id, state);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    void send_control_state_request(DeviceID motor_id, int32_t input_mode, int32_t control_mode) {
        motor_id = motor_id << 5;
        CANMsg msg = Msg_SetControllerModes(motor_id, control_mode, input_mode);
        CanFrame ros_msg = msg.to_ros_msg();
        can_pub_->publish(ros_msg);
    }

    // Services callbacks
    void reboot_callback(
        const std::shared_ptr<MotorService::Request> request,
        std::shared_ptr<MotorService::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Reboot service called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        send_reboot_request(motor_id);
        response->success = true;
    }

    void clear_error_callback(
        const std::shared_ptr<MotorService::Request> request,
        std::shared_ptr<MotorService::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Clear error service called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        send_clear_errors_request(motor_id);
        response->success = true;
    }

    void home_callback(
        const std::shared_ptr<MotorService::Request> request,
        std::shared_ptr<MotorService::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Home service called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        send_axis_state_request(motor_id, AxisState::HOMING);
        response->success = true;
    }

    void motor_ready_callback(
        const std::shared_ptr<MotorService::Request> request,
        std::shared_ptr<MotorService::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Motor ready called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        send_axis_state_request(motor_id, AxisState::CLOSED_LOOP_CONTROL);
        response->success = true;
    }

    bool request_state(DeviceID device_id, uint8_t mode) {
        switch (mode) {
            case SetupDrive::Request::MODE_IDLE:
                send_control_state_request(device_id, InputMode::INACTIVE, ControlMode::POSITION_CONTROL);
                break;
            case SetupDrive::Request::MODE_POSITION:
                send_control_state_request(device_id, InputMode::TRAP_TRAJ, ControlMode::POSITION_CONTROL);
                break;
            case SetupDrive::Request::MODE_VELOCITY:
                send_control_state_request(device_id, InputMode::PASSTROUGH, ControlMode::VELOCITY_CONTROL);
                break;
            default:
                return false;
        }
        return true;
    }

    void setup_callback(
        const std::shared_ptr<SetupDrive::Request> request,
        std::shared_ptr<SetupDrive::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Setup drive service called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        response->success = request_state(motor_id, request.get()->mode);
    }

    void move_with_vel_callback(
        const std::shared_ptr<MoveWithVel::Request> request,
        std::shared_ptr<MoveWithVel::Response> response)
    {
        RCLCPP_INFO(this->get_logger(), "Move with velocity service called");

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            response->success = false;
            return;
        }

        send_velocity_target(motor_id, request.get()->vel);
        response->success = true;
    }

    // move to pos action
    rclcpp_action::GoalResponse handle_move_to_pos_goal(
        const rclcpp_action::GoalUUID & uuid,
        std::shared_ptr<const MoveToPos::Goal> goal) {
        
        RCLCPP_INFO(this->get_logger(), "Received goal for motor: %d of pos: %.2f", goal->motor, goal->target_position);
        (void)uuid;

        DeviceID motor_id = request.get()->motor;
        if (!device_active(motor_id)) {
            return rclcpp_action::GoalResponse::REJECT;
        }

        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_move_to_pos_cancel(
        const std::shared_ptr<rclcpp_action::ServerGoalHandle<MoveToPos>> goal_handle) {

        const auto goal = goal_handle->get_goal();
        request_state(goal->motor, SetupDrive::Request::MODE_IDLE);

        RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");

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

            if (rclcpp::ok() && motor_data_.at(motor_id).error) {
                result->position_achieved = current_position;
                result->success = false;
                goal_handle->abort(result);
                RCLCPP_WARN(this->get_logger(), "Motor failed");
                return;
            }

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
