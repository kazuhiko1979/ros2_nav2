"""Start the Waffle maze and map it with SLAM Toolbox."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import IfElseSubstitution, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    root = Path(__file__).resolve().parents[1]
    slam_share = Path(get_package_share_directory("slam_toolbox"))
    nav2_share = Path(get_package_share_directory("nav2_bringup"))
    navigation = LaunchConfiguration("navigation")
    use_sim_time = "true"
    rviz_config = IfElseSubstitution(
        navigation,
        if_value=str(root / "rviz" / "maze_navigation.rviz"),
        else_value=str(root / "rviz" / "slam_toolbox_mapping.rviz"),
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Show Gazebo GUI"),
        DeclareLaunchArgument("rviz", default_value="true", description="Show RViz"),
        DeclareLaunchArgument(
            "navigation", default_value="false", description="Enable Nav2 during mapping",
        ),
        DeclareLaunchArgument(
            "slam_params_file",
            default_value=str(slam_share / "config" / "mapper_params_online_async.yaml"),
            description="SLAM Toolbox parameters",
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(root / "launch" / "maze_world.launch.py")),
            launch_arguments={"gui": LaunchConfiguration("gui"), "use_sim_time": use_sim_time}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(slam_share / "launch" / "online_async_launch.py")),
            launch_arguments={
                "slam_params_file": LaunchConfiguration("slam_params_file"),
                "use_sim_time": use_sim_time,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(nav2_share / "launch" / "navigation_launch.py")),
            launch_arguments={
                "params_file": str(root / "config" / "waffle_nav2.yaml"),
                "use_sim_time": use_sim_time,
            }.items(),
            condition=IfCondition(navigation),
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time": True}],
            condition=IfCondition(LaunchConfiguration("rviz")),
        ),
    ])
