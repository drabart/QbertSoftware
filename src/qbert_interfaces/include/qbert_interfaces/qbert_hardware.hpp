#ifndef qbert_HARDWARE__qbert_HARDWARE_HPP_
#define qbert_HARDWARE__qbert_HARDWARE_HPP_

#include <memory>
#include <string>
#include <vector>
#include <termios.h> // Include for serial communication

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/clock.hpp"
#include "rclcpp/duration.hpp"
#include "rclcpp/macros.hpp"
#include "rclcpp/time.hpp"
#include "rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include <gpiod.h>
#include <iostream>
#include <unistd.h>

#include "odrive_comms.hpp"
#include "festo_comms.hpp"
#include "joints.hpp"

namespace qbert_hardware
{

  class QbertHardwareSystem : public hardware_interface::SystemInterface  // derived class of SystemInterface
  {

    struct Config
    {
      std::string joint_1_name = "";
      std::string joint_2_name = "";
      std::string joint_3_name = "";
      std::string joint_4_name = "";
      std::string joint_5_name = "";
      std::string joint_6_name = "";
      std::string device = "";
      int baud_rate = 0;
      int timeout_ms = 0;
      float loop_rate = 0.0;
    };

  public:
    RCLCPP_SHARED_PTR_DEFINITIONS(QbertHardwareSystem)

    hardware_interface::CallbackReturn on_init(
        const hardware_interface::HardwareInfo &info) override;

    hardware_interface::CallbackReturn on_configure(
        const rclcpp_lifecycle::State &previous_state) override;

    hardware_interface::CallbackReturn on_activate(
        const rclcpp_lifecycle::State &previous_state) override;

    hardware_interface::CallbackReturn on_deactivate(
        const rclcpp_lifecycle::State &previous_state) override;

    hardware_interface::CallbackReturn on_shutdown(
      const rclcpp_lifecycle::State &previous_state) override;
    
    hardware_interface::CallbackReturn on_cleanup(
      const rclcpp_lifecycle::State &previous_state) override;

    std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

    std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

    hardware_interface::return_type read(const rclcpp::Time &time, const rclcpp::Duration &period) override;

    hardware_interface::return_type write(const rclcpp::Time &time, const rclcpp::Duration &period) override;

    int activate_qbert(bool state) 
    {
      gpiod_chip *chip;
      gpiod_line *line;

      //For Raspberry Pi 5 use gpiochip4 (For Raspberry Pi 4 use gpiochip0)
      const char *chipname = "gpiochip4";
      const unsigned int line_offset = 17;
      
      chip = gpiod_chip_open_by_name(chipname);
      if (!chip) {
          std::cerr << "Could not open chip." << std::endl;
          return 1;
      }
  
      line = gpiod_chip_get_line(chip, line_offset);
      if (!line) {
          std::cerr << "Could not get line." << std::endl;
          gpiod_chip_close(chip);
          return 1;
      }
  
      if (gpiod_line_request_output(line, "blinktest", 0) < 0) {
          std::cerr << "Could not set line as output." << std::endl;
          gpiod_chip_close(chip);
          return 1;
      }
      
      if (state == true)
      {
        gpiod_line_set_value(line, 1);
      }

      else
      {
        gpiod_line_set_value(line, 0);
      }  
      gpiod_chip_close(chip);
      return 0;
    }

  private:
    esp32_Comms comms_;
    Config cfg_;
    // create an object for each joint
    OdJoint joint_1_(0);
    OdJoint joint_2_(1);
    FestoJoint joint_3_();
    FestoJoint joint_4_();
    FestoJoint joint_5_();
    FestoJoint joint_6_();

    std::thread update_thread_;
    std::atomic<bool> running_{false};
    
    double ret[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    double past_joint_angles[6]; 
    double joint_angles[6];
    double delta_angles[6];

    int SerialPort = -1;
    struct termios tty;

    int WriteToCan(const unsigned char* buf, int nBytes);
    int ReadCan(unsigned char* buf, int nBytes);
  };

}

#endif