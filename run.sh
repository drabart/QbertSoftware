# !/bin/bash

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

colcon build --symlink-install
source install/setup.bash

ros2 launch robot_description display.launch.py
