# !/bin/bash

export GZ_VERSION=harmonic
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$(pwd)/install/qbert_description/share"
export PYTHONPATH="$PYTHONPATH:$(pwd)/.venv/lib/python3.12/site-packages"

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

colcon build
source install/local_setup.bash

ros2 launch qbert_bringup full.launch.py
