# !/bin/bash

export GZ_VERSION=harmonic
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$(pwd)/install/qbert_description/share"

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

colcon build --symlink-install
source install/setup.bash

ros2 launch qbert_bringup full.launch.py
