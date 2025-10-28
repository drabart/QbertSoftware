from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'qbert.urdf')

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'use_sim_time': False}],
        arguments=[urdf_path]
    )

    nodes = [
        rviz2_node,
        robot_state_publisher_node
    ]

    return LaunchDescription(nodes)
