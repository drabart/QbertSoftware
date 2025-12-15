# !/bin/bash

# Start HFSM executor
ros2 launch flexbe_onboard behavior_onboard.launch.py

# Starts the HFSM interface
ros2 launch flexbe_webui flexbe_ocs.launch.py
