from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_bringup = get_package_share_directory('qbert_bringup')
    pkg_description = get_package_share_directory('robot_description')
    pkg_gazebo = get_package_share_directory('qbert_gazebo')

    # Include robot description
    robot_desc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_description, 'launch', 'display.launch.py'))
    )

    # Include Gazebo simulation
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo, 'launch', 'sim.launch.py'))
    )

    nodes = [
        robot_desc_launch,
        gazebo_launch,
    ]

    return LaunchDescription(nodes)
