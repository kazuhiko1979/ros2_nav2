"""Launch the 5x5 maze and spawn TurtleBot3 Waffle at its south entrance."""

from pathlib import Path
import math

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    root = Path(__file__).resolve().parents[1]
    default_world = root / "worlds" / "maze_5x5.sdf"
    turtlebot_share = Path(get_package_share_directory("turtlebot3_gazebo"))
    gazebo_share = Path(get_package_share_directory("ros_gz_sim"))
    turtlebot_launch = turtlebot_share / "launch"
    gazebo_launch = gazebo_share / "launch" / "gz_sim.launch.py"
    model_name = "waffle"
    model_file = turtlebot_share / "models" / "turtlebot3_waffle" / "model.sdf"
    bridge_file = turtlebot_share / "params" / "turtlebot3_waffle_bridge.yaml"

    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")
    yaw = LaunchConfiguration("yaw")
    use_sim_time = LaunchConfiguration("use_sim_time")
    gui = LaunchConfiguration("gui")
    world_file = LaunchConfiguration("world_file")

    return LaunchDescription([
        DeclareLaunchArgument("x_pose", default_value="0.0"),
        DeclareLaunchArgument("y_pose", default_value="-4.0"),
        DeclareLaunchArgument("yaw", default_value=str(math.pi / 2)),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("gui", default_value="true"),
        DeclareLaunchArgument("world_file", default_value=str(default_world)),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", str(turtlebot_share / "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(gazebo_launch)),
            launch_arguments={"gz_args": ["-r -s -v 2 ", world_file], "on_exit_shutdown": "true"}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(gazebo_launch)),
            launch_arguments={"gz_args": "-g -v 2", "on_exit_shutdown": "true"}.items(),
            condition=IfCondition(gui),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(turtlebot_launch / "robot_state_publisher.launch.py")),
            launch_arguments={"use_sim_time": use_sim_time}.items(),
        ),
        Node(
            package="ros_gz_sim", executable="create",
            arguments=["-name", model_name, "-file", str(model_file),
                       "-x", x_pose, "-y", y_pose, "-z", "0.01", "-Y", yaw],
            output="screen",
        ),
        Node(
            package="ros_gz_bridge", executable="parameter_bridge",
            arguments=["--ros-args", "-p", f"config_file:={bridge_file}"],
            output="screen",
        ),
        Node(package="ros_gz_image", executable="image_bridge",
             arguments=["/camera/image_raw"], output="screen"),
    ])
