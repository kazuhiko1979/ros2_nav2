#!/usr/bin/env python3
"""Patrol the TurtleBot3 House using the saved my_house map."""

import argparse

from set_maze_initial_pose import main as run_navigation


# Each tuple is map X, map Y, and arrival heading in degrees from +X.
# The saved SLAM map is anchored at the Gazebo spawn point.
HOUSE_START = (0.0, 0.0, 0.0)
HOUSE_ROUTE = (
    (2.95, -0.75, 90),
    (2.95, 0.75, 90),
    (1.4, 2.6, 180),
    (-2.6, 3.3, 180),
    (-4.0, 3.5, -90),
    (-4.3, 2.6, -90),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--set-initial-pose", action="store_true",
        help="Initialize AMCL from the House spawn pose before the first run",
    )
    args = parser.parse_args()

    x, y, yaw = HOUSE_START
    navigation_args = ["--x", str(x), "--y", str(y), "--yaw-deg", str(yaw)]
    if args.set_initial_pose:
        navigation_args.append("--set-initial-pose")
    for waypoint in HOUSE_ROUTE:
        navigation_args.extend(["--waypoint", *map(str, waypoint)])
    return run_navigation(navigation_args)


if __name__ == "__main__":
    raise SystemExit(main())
