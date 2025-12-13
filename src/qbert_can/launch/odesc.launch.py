from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    can_node = Node(
        package='qbert_can',
        executable='qbert_can_node'
    )

    odesc_node = Node(
        package='qbert_can',
        executable='qbert_odesc_node'
    )

    return LaunchDescription([
        can_node,
        odesc_node
    ])
