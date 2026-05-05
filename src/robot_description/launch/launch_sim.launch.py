import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
import xacro
from launch_ros.actions import Node
# Gazebo related imports
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    xacro_file = os.path.join(pkg_path, "description", "robot.urdf.xacro")
    robot_description_config = xacro.process_file(xacro_file).toxml()
    rviz_config_path = os.path.join(pkg_path, 'config', 'saved_config.rviz')
    gazebo_world_path = os.path.join(pkg_path, 'worlds', 'final_world')
    gazebo_world_path_minimal = os.path.join(pkg_path, 'worlds', 'minimal_world')
    slam_toolbox_config = os.path.join(pkg_path, 'config', 'mapper_params_online_async.yaml')
    map_file_path = os.path.join(pkg_path, 'maps', 'map_save.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')


    # print(gazebo_world_path)
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
    # Spawns the bot in empty world
    gazebo_minimal=IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={
            'extra_gazebo_args': '--ros-args -- --no-audio',
            'world': gazebo_world_path_minimal
        }.items()
    )
    spawn_entity=Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', 
                   '-entity', 'diff_drive_robot_at_origin', 
                   '-x', '0', 
                   '-y', '0',
                   '-z', '0.2'
                   ],
        output='screen'
    )
    joint_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['joint_broad'],
    )
    diff_drive_spawner=Node(
        package="controller_manager",
        executable="spawner",
        arguments=['diff_cont']
    )
    
    # ros2 run teleop_twist_keyboard teleop_twist_keyboard
    teleop_node=Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        name="teleop_node",
        prefix="xterm -e", 
        parameters=[{
            'stamped':True,
            'frame_id':'base_link',
            'speed': 0.3,
            'turn':0.5,
            'repeat_rate':10.0
        }],
        remappings=[('/cmd_vel', '/diff_cont/cmd_vel')]
    )
    gazebo_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={
            'extra_gazebo_args': '--ros-args -- --no-audio',
            'world': gazebo_world_path
            }.items() 
    )
    slam_toolbox_node = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
    ]),
    launch_arguments={
        'slam_params_file': slam_toolbox_config,
        'use_sim_time': use_sim_time
    }.items()
    )

# pkill -9 gzserver && pkill -9 gzclient && pkill -9 rviz2
# ros2 run nav2_map_server map_server --ros-args -p yaml_filename:map_save.yaml -p use_sim_time:=true
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map_server',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['map_server']}
        ]
    )
    # ros2 run nav2_util lifecycle_bringup map_server
    map_server_node= Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'yaml_filename': map_file_path}]
        )
    return LaunchDescription([
        robot_state_publisher,
        rviz_node,
        # joint_state_publisher,
        # joint_state_publisher_gui,
        # gazebo_minimal,
        spawn_entity,
        joint_broadcaster_spawner,
        diff_drive_spawner,
        teleop_node,
        gazebo_world,
        slam_toolbox_node,
        lifecycle_manager_node,
        map_server_node
    ])