# !/bin/bash

# exit the script on error 
set -e

# setup the can adapter as a serial device
sudo ip link set can0 up type can bitrate 250000

# Start the motor hardware node
ros2 launch qbert_can odesc.launch.py &
# Start HFSM executor
ros2 launch flexbe_onboard behavior_onboard.launch.py &
# Starts the HFSM interface
ros2 launch flexbe_webui flexbe_ocs.launch.py &
