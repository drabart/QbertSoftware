from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_control = get_package_share_directory('qbert_control')
    ros2_control_path = os.path.join(pkg_control, 'config', 'qbert_controllers.yaml')

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--switch-timeout', '1000000',
        ],
        output='screen',
    )

    common_args = [
        '--param-file', ros2_control_path,
        '--switch-timeout', '1000000',
    ]

    position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['position_controller'] + common_args,
        output='screen',
    )

    unstrander_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['unstrander_controller'] + common_args,
        output='screen',
    )

    tool_disc_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['tool_disc_controller'] + common_args,
        output='screen',
    )

    compressor_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['compressor_controller'] + common_args,
        output='screen',
    )

    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller'] + common_args,
        output='screen',
    )

    roller_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['roller_controller'] + common_args,
        output='screen',
    )

    return LaunchDescription([
        joint_state_broadcaster_spawner,
        position_controller_spawner,
        # unstrander_controller_spawner,
        # tool_disc_controller_spawner,
        # compressor_controller_spawner,
        # gripper_controller_spawner,
        # roller_controller_spawner,
    ])
