#!/usr/bin/env python3
"""Create empty and furnished Gazebo Harmonic worlds from the floor plan.

Coordinates are approximate pixel positions measured from the course image.
The 40 px doorway between the left upper and lower rooms is assumed to be 0.9 m.
Edit the reference width or wall segments after obtaining real measurements.
"""

from math import atan2, hypot
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "worlds" / "dogtrot_floorplan.sdf"
FURNISHED_OUTPUT = ROOT / "worlds" / "dogtrot_furnished.sdf"
REFERENCE_DOOR_GAP_PX = 40.0
REFERENCE_DOOR_WIDTH_M = 0.90
METERS_PER_PIXEL = REFERENCE_DOOR_WIDTH_M / REFERENCE_DOOR_GAP_PX
IMAGE_CENTER_X = 403.5
IMAGE_CENTER_Y = 304.5
WALL_THICKNESS_M = 0.12
WALL_HEIGHT_M = 2.0

# Pixel coordinates in the supplied 808 x 610 floor plan. A wall segment ends
# before each doorway. The top corridor and front porch are closed for this
# first navigation exercise; window and chimney details are omitted.
WALLS_PX = [
    ("outer_top", 96, 48, 711, 48),
    ("outer_bottom", 96, 562, 711, 562),
    ("outer_left", 96, 48, 96, 562),
    ("outer_right", 711, 48, 711, 562),
    ("upper_left_partition_north", 330, 48, 330, 133),
    ("upper_left_partition_south", 330, 174, 330, 193),
    ("lower_left_partition_north", 330, 193, 330, 292),
    ("lower_left_partition_south", 330, 329, 330, 426),
    ("upper_right_partition_north", 474, 48, 474, 133),
    ("upper_right_partition_south", 474, 174, 474, 193),
    ("lower_right_partition_north", 474, 193, 474, 292),
    ("lower_right_partition_south", 474, 329, 474, 426),
    ("left_cross_west", 96, 193, 148, 193),
    ("left_cross_east", 188, 193, 330, 193),
    ("right_cross_west", 474, 193, 628, 193),
    ("right_cross_east", 668, 193, 711, 193),
    ("left_porch_west", 96, 426, 194, 426),
    ("left_porch_east", 235, 426, 330, 426),
    ("right_porch_west", 474, 426, 577, 426),
    ("right_porch_east", 618, 426, 711, 426),
]

# name, x, y, width, depth, height, visual color. These solid obstacles are
# deliberately placed away from the room doors and the central corridor.
FURNITURE = [
    ("bookshelf_left_shed", -5.7, 4.4, 0.4, 1.0, 1.5, "0.43 0.27 0.14 1"),
    ("bookshelf_right_shed", 5.7, 4.4, 0.4, 1.0, 1.5, "0.43 0.27 0.14 1"),
    ("low_table_left_primary", -4.4, -0.3, 0.9, 0.6, 0.5, "0.55 0.35 0.20 1"),
    ("crate_left_primary", -5.4, -1.7, 0.65, 0.65, 0.65, "0.65 0.43 0.22 1"),
    ("crate_right_primary", 4.9, -1.2, 0.7, 0.7, 0.7, "0.65 0.43 0.22 1"),
    ("pallet_porch", 3.0, -4.1, 1.0, 0.8, 0.2, "0.50 0.31 0.15 1"),
]


def add_text(parent: ET.Element, name: str, value: object) -> ET.Element:
    element = ET.SubElement(parent, name)
    element.text = str(value)
    return element


def add_box(
    parent: ET.Element,
    name: str,
    pose: str,
    size: str,
    color: str = "0.80 0.80 0.78 1",
) -> None:
    for component in ("collision", "visual"):
        element = ET.SubElement(parent, component, name=f"{name}_{component}")
        add_text(element, "pose", pose)
        geometry_box = ET.SubElement(ET.SubElement(element, "geometry"), "box")
        add_text(geometry_box, "size", size)
        if component == "visual":
            material = ET.SubElement(element, "material")
            add_text(material, "ambient", color)
            add_text(material, "diffuse", color)


def point(px: float, py: float) -> tuple[float, float]:
    return (
        (px - IMAGE_CENTER_X) * METERS_PER_PIXEL,
        (IMAGE_CENTER_Y - py) * METERS_PER_PIXEL,
    )


def make_world(with_furniture: bool = False) -> ET.ElementTree:
    sdf = ET.Element("sdf", version="1.8")
    world = ET.SubElement(sdf, "world", name="dogtrot_floorplan")
    for filename, name in (
        ("gz-sim-physics-system", "gz::sim::systems::Physics"),
        ("gz-sim-user-commands-system", "gz::sim::systems::UserCommands"),
        ("gz-sim-scene-broadcaster-system", "gz::sim::systems::SceneBroadcaster"),
        ("gz-sim-sensors-system", "gz::sim::systems::Sensors"),
        ("gz-sim-imu-system", "gz::sim::systems::Imu"),
    ):
        plugin = ET.SubElement(world, "plugin", filename=filename, name=name)
        if filename == "gz-sim-sensors-system":
            add_text(plugin, "render_engine", "ogre2")

    scene = ET.SubElement(world, "scene")
    add_text(scene, "ambient", "0.75 0.75 0.75 1")
    light = ET.SubElement(world, "light", name="sun", type="directional")
    add_text(light, "pose", "0 0 10 0 0 0")
    add_text(light, "direction", "-0.3 -0.3 -1")
    add_text(light, "diffuse", "0.8 0.8 0.8 1")
    add_text(light, "specular", "0.2 0.2 0.2 1")

    floor = ET.SubElement(world, "model", name="floor")
    add_text(floor, "static", "true")
    add_box(
        ET.SubElement(floor, "link", name="floor_link"),
        "floor_box",
        "0 0 -0.025 0 0 0",
        "14.8 12.5 0.05",
    )

    walls = ET.SubElement(world, "model", name="dogtrot_walls")
    add_text(walls, "static", "true")
    wall_link = ET.SubElement(walls, "link", name="wall_link")
    for name, px1, py1, px2, py2 in WALLS_PX:
        x1, y1 = point(px1, py1)
        x2, y2 = point(px2, py2)
        length = hypot(x2 - x1, y2 - y1)
        yaw = atan2(y2 - y1, x2 - x1)
        pose = f"{(x1 + x2) / 2:.4f} {(y1 + y2) / 2:.4f} {WALL_HEIGHT_M / 2:.4f} 0 0 {yaw:.6f}"
        size = f"{length:.4f} {WALL_THICKNESS_M:.4f} {WALL_HEIGHT_M:.4f}"
        add_box(wall_link, name, pose, size)

    if with_furniture:
        for name, x, y, width, depth, height, color in FURNITURE:
            model = ET.SubElement(world, "model", name=name)
            add_text(model, "static", "true")
            add_text(model, "pose", f"{x:.3f} {y:.3f} 0 0 0 0")
            link = ET.SubElement(model, "link", name="body")
            add_box(
                link,
                "body_box",
                f"0 0 {height / 2:.3f} 0 0 0",
                f"{width:.3f} {depth:.3f} {height:.3f}",
                color,
            )

    ET.indent(sdf, space="  ")
    return ET.ElementTree(sdf)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    for output, with_furniture in ((OUTPUT, False), (FURNISHED_OUTPUT, True)):
        tree = make_world(with_furniture)
        tree.write(output, encoding="utf-8", xml_declaration=True)
        print(
            f"Generated {output} with {len(WALLS_PX)} wall segments"
            f" and {len(FURNITURE) if with_furniture else 0} objects"
        )


if __name__ == "__main__":
    main()
