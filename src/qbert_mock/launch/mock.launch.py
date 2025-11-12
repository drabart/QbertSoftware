from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('qbert_description')
    urdf_file = os.path.join(pkg_description, 'urdf', 'qbert.xacro')
    robot_desc = Command(['xacro ', urdf_file])

    mock_limit_switches = Node(
        package='qbert_mock',
        executable='limit_switch_node.py',
        name='touch_sensor_node',
        output='screen',
        parameters=[
            {'robot_description': robot_desc},
            {'limit_switch_joints': ['J1_gantry', 'J2_A_rotor']}
        ],
    )

    mock_distance_sensors = Node(
        package='qbert_mock',
        executable='distance_sensor_node.py',
        name='distance_sensor_node',
        output='screen',
        parameters=[
            {'distance_sensor_joints': ['joint_J3_A_tool_disc']}
        ],
    )

    return LaunchDescription([
        mock_limit_switches,
        mock_distance_sensors,
    ])
