from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    camera = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node'
    )

    cable_detect = Node(
        package='qbert_cam',
        executable='cable_detector_node'
    )

    return LaunchDescription([
        camera,
        cable_detect,
    ])
