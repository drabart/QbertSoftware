from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'qbert.urdf')

    # Read URDF file
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_path, 'config', 'display.rviz')]
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': False}]
    )
    
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    return LaunchDescription([rviz2_node, robot_state_publisher_node, joint_state_publisher_node])

