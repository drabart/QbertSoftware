from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_can = get_package_share_directory('qbert_can')
    pkg_flexbe_onboard = get_package_share_directory('flexbe_onboard')
    pkg_flexbe_webui = get_package_share_directory('flexbe_webui')

    # Paths to sub-launch files
    can_launch = os.path.join(pkg_can, 'launch', 'can.launch.py')
    flexbe_onboard_launch = os.path.join(pkg_flexbe_onboard, 'behavior_onboard.launch.py')
    flexbe_webui_launch = os.path.join(pkg_flexbe_webui, 'launch', 'flexbe_ocs.launch.py')

    include_can = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(can_launch)
    )
    include_flexbe_onboard = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(flexbe_onboard_launch)
    )
    include_flexbe_webui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(flexbe_webui_launch)
    )
    include_qbert_gui = Node(
        package='qbert_gui',
        executable='gui',
        name='qbert_gui',
        output='screen',
    )

    return LaunchDescription([
        include_can,
        include_flexbe_onboard,
        include_flexbe_webui,
        include_qbert_gui,
    ])
