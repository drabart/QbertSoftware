# QbertSoftware

This project contains software used to operate Qbert - a robot developed by CavoLab - a student team from TU Delft for Robotics Minor.

![Photo of the robot](docs/QbertPhoto.jpg)

The robot was ordered by Prysmian - a high voltage cable manufacturer. 
The robot's aim is to prepare the conductor for welding it with another end of a cable to install a joint.

## Software Architecture

The software in this repository is split into 2:
 - src - ROS2 packages used for high level control and computer vision
 - qbert_esp - ESPIDF repository with code for the ESP device handling low level functionalities

The overview of the system can be seen here:
![System Diagram](docs/DataSystemDiagram.drawio.png)

### FlexBE State Machine

Main logic of the actions performed by the robot is created using FlexBE - a ROS2 module for creating state machines.

To run FlexBE it requires 2 ros launch files:
 - FlexBE OCS - starts FlexBE GUI where the state machine can be modified and started
 - FlexBE onboard - starts FlexBE state machine executor

![State Diagram](docs/FlexbeStates.png)

To implement functionality for the robot we also created 3 additional packages interacting with different hardware.

### Qbert GUI

A GUI written with PyQt6 implementing basic utilities to safely run the robot.
To communicate with the executor via ROS2 it also starts an internal ROS node with publishers and subscribers.

To make the communication easy to use with FlexBE, it happens over ROS topics using standard message types:
 - Empty (homing, start, cancel)
 - Bool (confirm)
 - Float64 (offset)

### Qbert CAN

A node used for communicating with the robot's hardware components. To do this CAN Bus was chosen (see Design Report for reasoning).
This package uses SocketCAN to allow for easy interaction with the CAN, which is facilitated by a USB to CAN adapter connected to the PC running the executor.

As because of budget constraint we chose a cheaper alternative for motor controllers (ODesc), we had to create a basic interface for their CAN protocol (CAN Simple) for handling receiving and sending messages in the expected format. 

Due to time constraints our implementation does not cover the entire [ODrive CAN protocol](https://docs.odriverobotics.com/v/0.5.6/can-protocol.html), but only the most essential parts.

This package also contains our code for handling communication with the ESP32.
We decided to slightly extend CAN Simple for this use. We reserved the highest bit of the device ID for differentiating between ODesc and ESP32 devices. Otherwise the protocol implements the messages:
 - 0x01 - heartbeat
 - 0x02 - setPosAxe
 - 0x03 - setGripState
 - 0x04 - getPosAxe
 - 0x05 - getGripState

For all relevant messages we also implemented higher level services and actions.
For example the `/odesc/move_to_pos` action or `/esp/gripper_state` service.
For further development the topics should probably be slightly refactored to follow some convention such as REST.

### Qbert Camera

This is a package responsible for the computer vision part of the project.
It starts a node reading data from RealSense camera.
The computer vision can then be started by calling the appropriate action.

## Dependencies

- Python >= 3
- Python packages specified in `requirements.txt`
- [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/Installation.html)
- [LibRealSense 2](https://github.com/realsenseai/librealsense) - Matching version for realsense-ros package
- [ESP IDF](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/index.html) >= 5.5.0

## Building

### Building ROS packages
1. `source PATH_TO_ROS_JAZZY/setup.bash`
2. If python packages were installed in a venv source it: `source .venv/bin/activate`
3. `colcon build` (Note: do not use --symlink-install as it breaks some packages)

### Building ESP code
1. `cd qbert_esp`
2. `. PATH_TO_ESP_IDF/export.sh`
3. `idf.py build` or `idf.py flash` depending on what is needed

## Running

For running the software in default configuration running the `run.sh` script should be enough.

To explain its contents:
 - For running FlexBE adding the python venv to the PYTHONPATH is necessary (as it cannot find the required packages otherwise), and can be done with `export PYTHONPATH="$PYTHONPATH:$(pwd)/.venv/lib/CORRECT_PYTHON_VERSION/site-packages`
 - After plugging in the USB to CAN adapter the network needs to be set up. It can be done on linux with `sudo ip link set can0 up type can bitrate 250000` command.
 - The packages can then be started with `ros2 launch qbert_bringup full.launch.py`, which launches the 5 packages described above.
