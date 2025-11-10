import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('qbert_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': PathJoinSubstitution([pkg_gazebo, 'worlds', 'qbert_world.sdf'])}.items(),
    )

    gazebo_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_gazebo, 'config', 'ros_gz_bridge.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local'
        }],
        output='screen'
    )

    gazebo_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-entity', 'qbert', '-topic', 'robot_description', '-x', '0', '-y', '0', '-z', '0'],
        output='screen'
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
    )

    tf2_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'Origin'],
    )

    return LaunchDescription([
        gz_sim, 
        gazebo_bridge_node, 
        gazebo_spawn_entity,
        joint_state_publisher,
        tf2_node,
    ])
