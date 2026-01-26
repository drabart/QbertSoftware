# QbertSoftware

This project contains software used to operate Qbert - a robot developed by CavoLab - a student team from TU Delft for Robotics Minor. The robot was ordered by Prysmian - a high voltage cable manufacturer. 
The robot's aim is to prepare the conductor for welding it with another end of a cable to install a joint.

## Software Architecture

The software in this repository is split into 2:
 - src - ROS2 packages used for high level control and computer vision
 - qbert_esp - ESPIDF repository with code for the ESP device handling low level functionalities

The overview of the system can be seen here:
![](DataSystemDiagram.drawio.png)

Main logic of the actions performed by the robot is created using FlexBE - a ROS2 module for creating state machines.

To run FlexBE it requires 2 ros launch files:
 - FlexBE OCS - starts FlexBE GUI where the state machine can be modified and started
 - FlexBE onboard - starts FlexBE state machine executor

To implement functionality for the robot we also created 3 additional packages interacting with different hardware.

### Qbert GUI

A GUI written with PyQt6 implementing basic utilities to safely run the robot. To communicate with the executor via ROS2 it also starts an internal ROS node with publishers and subscribers.

To make the communication easy to use with FlexBE, it happens over ROS topics using standard message types:
 - Empty (homing, start, cancel)
 - Bool (confirm)
 - Float64 (offset)

### Qbert CAN

A node used for communicating with robot's hardware components. To do this we chose to use CAN Bus (for the reasoning see Design Report). This package uses SocketCAN to allow for easy interaction with the CAN, which is facilitated by a USB to CAN adapter connected to the PC running the executor.

As because of budget constraint we chose a cheaper alternative for motor controllers (ODesc), we had to create a basic interface for their CAN protocol (CAN Simple) for handling receiving and sending messages in the expected format. 

Due to time constraints our implementation does not cover the entire CAN Simple, but only the most essential parts. There also is a dbc file covering the protocol, but we did not find a good tool to decode it in C++, for any further development switching the motor controllers to the more expensive version - ODrive - or putting more time into figuring out the .dbc integration would be good to ensure more robustness.

This package also contains our code for handling communication with the ESP32. We decided to slightly extend CAN Simple for this use. We reserved the highest bit of the device ID for differentiating between ODesc and ESP32 devices. Otherwise the protocol implements the messages:
 - 0x01 - heartbeat
 - 0x02 - setPosAxe
 - 0x03 - setGripState
 - 0x04 - getPosAxe
 - 0x05 - getGripState

For all relevant messages we also implemented higher level services and actions. For example the `/odesc/move_to_pos` action or `/esp/gripper_state` service. For further development the topics should probably be slightly refactored to follow some convention such as REST.

### Qbert Camera

This is a package responsible for the computer vision part of the project. It starts a node reading data from RealSense camera. The computer vision can then be started by calling an appropriate actions.

## Building

First install and source ROS2 Jazzy. It is strongly recommended to do this on Ubuntu 24 LTS. Then source it, and the venv with `source /opt/ros/jazzy/setup.bash` and `source .venv/bin/activate`.

The ROS2 part of the project is compiled using `colcon build` and then needs to be sourced with `source install/local_setup.bash`. Important note is that the `--symlink-install` does not seem to work with some of the packages, so it should be compiled without it.

## Running

For running the software in default configuration running the `run.sh` script should be enough.

To explain its contents:
 - For running FlexBE adding the python venv to the PYTHONPATH is necessary (as it seems that it cannot find it's packages otherwise), and can be done with `export PYTHONPATH="$PYTHONPATH:$(pwd)/.venv/lib/python3.12/site-packages"`
 - After plugging in the USB to CAN adapter the network needs to be set up. It can be done on linux with `sudo ip link set can0 up type can bitrate 250000` command.
 - The packages can then be started with `ros2 launch qbert_bringup full.launch.py`, which launches the 5 packages described above.

## Further Development Recommendations

TODO


