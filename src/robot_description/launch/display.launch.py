from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command, PathJoinSubstitution


def generate_launch_description():
    pkg_path = FindPackageShare('robot_description')
    xacro_path = PathJoinSubstitution([pkg_path, 'urdf', 'qbert.xacro'])

    # Use xacro command to expand the file into URDF text
    robot_description = Command(['xacro ', xacro_path])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }],
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', PathJoinSubstitution([pkg_path, 'config', 'display.rviz'])]
    )
    
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    return LaunchDescription([
        rviz2_node, 
        robot_state_publisher_node, 
        joint_state_publisher_node
    ])

