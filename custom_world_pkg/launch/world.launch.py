import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import PythonExpression
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    frame_prefix = LaunchConfiguration('frame_prefix', default='')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
    model_folder = 'turtlebot3_' + TURTLEBOT3_MODEL
    urdf_file_name = model_folder + '.urdf'
    urdf_path = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'urdf', urdf_file_name)
    with open(urdf_path, 'r') as urdf:
        robot_description = urdf.read()
        urdf.close()

    sdf_path = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'models', model_folder, 'model.sdf')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
        )
    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(get_package_share_directory('custom_worlds'), 'worlds', 'turtlebot3_world.world'),
        description='Full path to the world model file to load'
        )
    declare_x_cmd = DeclareLaunchArgument(
        'x_pose',
        default_value='0.0',
        description='Specify namespace of the robot'
        )

    declare_y_cmd = DeclareLaunchArgument(
        'y_pose',
        default_value='0.0',
        description='Specify namespace of the robot'
        )

    gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')
            ),
        launch_arguments=[
            ('world', LaunchConfiguration('world'))
        ]
    )

    gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')
        )
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description,
                'frame_prefix': PythonExpression(["'", frame_prefix, "/'"])
            }]
    )

    turtlebot3_spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', TURTLEBOT3_MODEL,
            '-file', sdf_path,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.0'
        ],
        output='screen',
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_world_cmd,
        declare_x_cmd,
        declare_y_cmd,
        gazebo_server_cmd,
        gazebo_client_cmd,
        robot_state_publisher_node,
        turtlebot3_spawn_node,
    ])
