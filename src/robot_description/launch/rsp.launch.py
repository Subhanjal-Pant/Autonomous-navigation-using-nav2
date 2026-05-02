import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
import xacro
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path=get_package_share_directory('robot_description')
    xacro_file=os.path.join(pkg_path, "description", "robot.urdf.xacro")
    robot_description_config=xacro.process_file(xacro_file).toxml()
    rviz_config_path=os.path.join(pkg_path, 'config', 'saved_config.rviz')

    robot_state_publisher=Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_config}]

    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2', 
        output='screen',
        arguments=['-d', rviz_config_path]

    )
    joint_state_publisher=Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    return LaunchDescription([
        robot_state_publisher,
        rviz_node,
        # joint_state_publisher,
        joint_state_publisher_gui
    ])