"""Start the Waffle maze simulation, saved-map navigation, and RViz."""

from pathlib import Path
import math

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def start_maze_navigation(context):
    root = Path(__file__).resolve().parents[1]
    nav2_launch = Path(get_package_share_directory("nav2_bringup")) / "launch"
    use_sim_time = "true"
    spawn_pose = {}
    for name in ("x_pose", "y_pose", "yaw"):
        value = float(LaunchConfiguration(name).perform(context))
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        spawn_pose[name] = f"{value:.16f}"
    params = RewrittenYaml(
        source_file=str(root / "config" / "waffle_nav2.yaml"),
        param_rewrites={
            "amcl.ros__parameters.set_initial_pose": LaunchConfiguration("auto_initial_pose"),
            "amcl.ros__parameters.initial_pose.x": spawn_pose["x_pose"],
            "amcl.ros__parameters.initial_pose.y": spawn_pose["y_pose"],
            "amcl.ros__parameters.initial_pose.yaw": spawn_pose["yaw"],
        },
        convert_types=True,
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(root / "launch" / "maze_world.launch.py")),
            launch_arguments={
                **spawn_pose,
                "gui": LaunchConfiguration("gui"),
                "use_sim_time": use_sim_time,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(nav2_launch / "bringup_launch.py")),
            launch_arguments={
                "map": str(root / "maps" / "maze_5x5.yaml"),
                "params_file": params,
                "slam": "False",
                "use_sim_time": use_sim_time,
            }.items(),
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", str(root / "rviz" / "maze_navigation.rviz")],
            parameters=[{"use_sim_time": True}],
            condition=IfCondition(LaunchConfiguration("rviz")),
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Show Gazebo GUI"),
        DeclareLaunchArgument("rviz", default_value="true", description="Show RViz"),
        DeclareLaunchArgument(
            "auto_initial_pose", default_value="true",
            description="Initialize AMCL from the Waffle spawn pose",
        ),
        DeclareLaunchArgument("x_pose", default_value="0.0"),
        DeclareLaunchArgument("y_pose", default_value="-4.0"),
        DeclareLaunchArgument("yaw", default_value=str(math.pi / 2)),
        OpaqueFunction(function=start_maze_navigation),
    ])
