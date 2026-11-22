"""Publish a URDF and its joint states for inspection in RViz."""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def start_publishers(context):
    model = Path(LaunchConfiguration("model").perform(context)).expanduser()
    rviz_config = Path(__file__).resolve().parents[1] / "rviz" / "inspect_urdf.rviz"
    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{
                "robot_description": ParameterValue(model.read_text(encoding="utf-8"), value_type=str),
            }],
        ),
        Node(package="joint_state_publisher", executable="joint_state_publisher"),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", str(rviz_config), "-f", LaunchConfiguration("fixed_frame")],
            condition=IfCondition(LaunchConfiguration("rviz")),
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("model", description="Path to a plain URDF file"),
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("fixed_frame", default_value="base_footprint",
                              description="RViz fixed frame for the model"),
        OpaqueFunction(function=start_publishers),
    ])
