from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_description = get_package_share_directory('qbert_description')
    pkg_gazebo = get_package_share_directory('qbert_gazebo')
    pkg_control = get_package_share_directory('qbert_control')
    pkg_mock = get_package_share_directory('qbert_mock')

    # Paths to sub-launch files
    robot_desc_launch = os.path.join(pkg_description, 'launch', 'display.launch.py')
    gazebo_launch = os.path.join(pkg_gazebo, 'launch', 'sim.launch.py')
    mock_launch = os.path.join(pkg_mock, 'launch', 'mock.launch.py')
    control_launch = os.path.join(pkg_control, 'launch', 'control.launch.py')

    include_robot_desc = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(robot_desc_launch)
    )

    include_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )

    include_mock = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(mock_launch)
    )

    include_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(control_launch)
    )

    return LaunchDescription([
        include_robot_desc,
        include_gazebo,
        include_mock,
        include_control,
    ])
