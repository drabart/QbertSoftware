#!/bin/bash
# set -e

sudo ip link set can0 up type can bitrate 250000

source ./install/setup.bash

tmux new-session -d -s ros2
tmux split-window -h
tmux split-window -h
tmux select-layout even-horizontal

tmux select-pane -t 0
tmux send-keys 'ros2 launch qbert_can odesc.launch.py' C-m
tmux select-pane -t 1
tmux send-keys 'ros2 launch flexbe_onboard behavior_onboard.launch.py' C-m
tmux select-pane -t 2
tmux send-keys 'ros2 launch flexbe_webui flexbe_ocs.launch.py' C-m

tmux attach -t ros2
