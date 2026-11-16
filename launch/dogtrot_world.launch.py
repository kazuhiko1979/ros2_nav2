"""Launch a dogtrot floor plan world and TurtleBot3 Waffle in Harmonic."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    project_root = Path(__file__).resolve().parents[1]
    default_world = project_root / "worlds" / "dogtrot_furnished.sdf"
    turtlebot_share = Path(get_package_share_directory("turtlebot3_gazebo"))
    gazebo_share = Path(get_package_share_directory("ros_gz_sim"))
    turtlebot_launch = turtlebot_share / "launch"
    gazebo_launch = gazebo_share / "launch" / "gz_sim.launch.py"

    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")
    use_sim_time = LaunchConfiguration("use_sim_time")
    world_file = LaunchConfiguration("world_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument("x_pose", default_value="0.0"),
            DeclareLaunchArgument("y_pose", default_value="0.0"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("world_file", default_value=str(default_world)),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", str(turtlebot_share / "models")),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(gazebo_launch)),
                launch_arguments={"gz_args": ["-r -s -v 2 ", world_file], "on_exit_shutdown": "true"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(gazebo_launch)),
                launch_arguments={"gz_args": "-g -v 2", "on_exit_shutdown": "true"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(turtlebot_launch / "robot_state_publisher.launch.py")),
                launch_arguments={"use_sim_time": use_sim_time}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(turtlebot_launch / "spawn_turtlebot3.launch.py")),
                launch_arguments={"x_pose": x_pose, "y_pose": y_pose}.items(),
            ),
        ]
    )
