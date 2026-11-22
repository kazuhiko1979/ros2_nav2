#!/usr/bin/env python3
"""Set an initial pose or navigate to one or more poses in the Gazebo maze."""

import argparse
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import GetState
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.executors import ExternalShutdownException
from rclpy.parameter import Parameter
from rclpy.signals import SignalHandlerOptions


def make_pose(clock, x, y, yaw_deg):
    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = clock.now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    half_yaw = math.radians(yaw_deg) / 2
    pose.pose.orientation.z = math.sin(half_yaw)
    pose.pose.orientation.w = math.cos(half_yaw)
    return pose


def wait_for_active_navigator(navigator):
    """Wait for BT Navigator without publishing another initial pose."""
    client = navigator.create_client(GetState, "bt_navigator/get_state")
    try:
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if not client.wait_for_service(timeout_sec=0.5):
                continue
            future = client.call_async(GetState.Request())
            rclpy.spin_until_future_complete(
                navigator, future, timeout_sec=max(0.0, deadline - time.monotonic()),
            )
            if future.done() and future.result().current_state.id == State.PRIMARY_STATE_ACTIVE:
                return True
            time.sleep(0.25)
        navigator.error("Nav2 is not active. Check that AMCL has an initial pose.")
        return False
    finally:
        navigator.destroy_client(client)


def wait_for_task(navigator, describe_feedback, previous_feedback):
    next_report = time.monotonic()
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback is None or feedback is previous_feedback:
            continue
        if time.monotonic() >= next_report:
            navigator.info(describe_feedback(feedback))
            previous_feedback = feedback
            next_report = time.monotonic() + 2
    result = navigator.getResult()
    navigator.info(f"Navigation result: {result.name}")
    return result


def describe_goal_feedback(feedback):
    position = feedback.current_pose.pose.position
    return (
        f"Position ({position.x:.2f}, {position.y:.2f}); "
        f"path remaining {feedback.distance_remaining:.2f} m"
    )


def navigate_to_goal(navigator, goal):
    previous_feedback = navigator.getFeedback()
    if not navigator.goToPose(goal):
        navigator.error("Navigation goal was rejected.")
        return 1
    result = wait_for_task(navigator, describe_goal_feedback, previous_feedback)
    return 0 if result == TaskResult.SUCCEEDED else 1


def follow_waypoints(navigator, coordinates, repeat):
    clock = navigator.get_clock()
    for lap in range(1, repeat + 1):
        navigator.info(f"Waypoint run {lap}/{repeat}")
        poses = [make_pose(clock, *coordinate) for coordinate in coordinates]
        previous_feedback = navigator.getFeedback()
        if not navigator.followWaypoints(poses):
            navigator.error("Waypoint request was rejected.")
            return 1
        result = wait_for_task(
            navigator,
            lambda feedback: f"Waypoint {feedback.current_waypoint + 1}/{len(poses)}",
            previous_feedback,
        )
        # Jazzy's getResult() exposes the action status. The payload holds missed waypoints.
        response = navigator.result_future.result()
        missed = response.result.missed_waypoints if response is not None else []
        if missed:
            indices = ", ".join(str(waypoint.index + 1) for waypoint in missed)
            navigator.error(f"Missed waypoints: {indices}")
            return 1
        if result != TaskResult.SUCCEEDED:
            return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x", type=float, default=0.0, help="Initial map x in metres")
    parser.add_argument("--y", type=float, default=-4.0, help="Initial map y in metres")
    parser.add_argument("--yaw-deg", type=float, default=90.0, help="Initial heading from +X")
    commands = parser.add_mutually_exclusive_group()
    commands.add_argument("--goal", type=float, nargs=3, metavar=("X", "Y", "YAW_DEG"),
                          help="Navigate to a map pose (metres, metres, degrees from +X)")
    commands.add_argument("--waypoint", type=float, nargs=3, action="append",
                          metavar=("X", "Y", "YAW_DEG"),
                          help="Add a waypoint; repeat the option to specify the route")
    parser.add_argument("--repeat", type=int, help="Number of waypoint runs (default: 1)")
    parser.add_argument("--set-initial-pose", action="store_true",
                        help="Publish the initial pose before sending a goal")
    args = parser.parse_args(argv)
    if args.repeat is not None and (not args.waypoint or args.repeat < 1):
        parser.error("--repeat requires --waypoint and must be at least 1")
    target_poses = args.waypoint or ([args.goal] if args.goal else [])
    if not all(math.isfinite(value) for pose in [(args.x, args.y, args.yaw_deg), *target_poses]
               for value in pose):
        parser.error("Pose values must be finite")

    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    navigator = None
    try:
        navigator = BasicNavigator()
        navigator.set_parameters([Parameter("use_sim_time", value=True)])
        clock = navigator.get_clock()
        deadline = time.monotonic() + 15
        while clock.now().nanoseconds == 0:
            if time.monotonic() >= deadline:
                navigator.error("No advancing simulation clock. Start the maze and unpause Gazebo.")
                return 1
            rclpy.spin_once(navigator, timeout_sec=0.2)

        if not target_poses or args.set_initial_pose:
            navigator.setInitialPose(make_pose(clock, args.x, args.y, args.yaw_deg))
            navigator.waitUntilNav2Active()
        elif not wait_for_active_navigator(navigator):
            return 1

        if args.waypoint:
            return follow_waypoints(navigator, args.waypoint, args.repeat or 1)
        if args.goal:
            return navigate_to_goal(navigator, make_pose(clock, *args.goal))
        return 0
    except KeyboardInterrupt:
        if navigator is not None and navigator.result_future is not None:
            navigator.cancelTask()
        return 130
    except ExternalShutdownException:
        return 130
    finally:
        if navigator is not None:
            navigator.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
