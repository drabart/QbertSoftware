from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', '$(find robot_description)/rviz/qbert_config.rviz'],
        output='screen'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'use_sim_time': False}],
        arguments=['$(find robot_description)/urdf/qbert.urdf']
    )

    nodes = [
        rviz2_node,
        robot_state_publisher_node
    ]

    return LaunchDescription(nodes)
