from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('robot_description')
    pkg_gazebo = get_package_share_directory('qbert_gazebo')
    urdf_file = os.path.join(pkg_description, 'urdf', 'qbert.xacro')
    robot_desc = Command(['xacro ', urdf_file])

    # Include robot description
    robot_desc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_description, 'launch', 'display.launch.py'))
    )

    # Include Gazebo simulation
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo, 'launch', 'sim.launch.py'))
    )

    mock_limit_switches = Node(
        package='mock_sensors',
        executable='limit_switches',
        name='touch_sensor_node',
        output='screen',
        parameters=[
            {'robot_description': robot_desc}, 
            {'limit_switch_joints': ['J1_gantry', 'J2_A_rotor']} 
        ],
    )

    mock_distance_sensors = Node(
        package='mock_sensors',
        executable='distance_sensors',
        name='distance_sensor_node',
        output='screen',
        parameters=[
            {'distance_sensor_joints': ['joint_J3_A_tool_disc']} 
        ],
    )

    nodes = [
        robot_desc_launch,
        gazebo_launch,
        mock_limit_switches,
        mock_distance_sensors,
    ]

    return LaunchDescription(nodes)
