from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    socketcan_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros2_socketcan'),
                'launch',
                'socket_can_bridge.launch.xml'
            )
        ),
        launch_arguments={
            'interface': 'can0',
            'receiver_interval_sec': '0.2',
        }.items(),
    )

    odesc_node = Node(
        package='qbert_can',
        executable='qbert_odesc_node'
    )

    esp_node = Node(
        package='qbert_can',
        executable='qbert_esp_node'
    )

    return LaunchDescription([
        socketcan_launch,
        odesc_node,
        esp_node
    ])

