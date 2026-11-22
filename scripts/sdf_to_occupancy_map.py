#!/usr/bin/env python3
"""Rasterize box collisions in this Gazebo SDF as a Nav2 occupancy map."""

import argparse
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def numbers(text, count=6):
    values = [float(v) for v in (text or '').split()]
    return (values + [0.0] * count)[:count]


def child_pose(element):
    pose = element.find('pose')
    return numbers(pose.text if pose is not None else None)


def compose(parent, local):
    px, py, pz, _, _, pa = parent
    lx, ly, lz, _, _, la = local
    c, s = math.cos(pa), math.sin(pa)
    return (px + c * lx - s * ly, py + s * lx + c * ly,
            pz + lz, 0.0, 0.0, pa + la)


def walk_models(parent, parent_pose):
    for model in parent.findall('model'):
        model_pose = compose(parent_pose, child_pose(model))
        yield from walk_models(model, model_pose)
        for link in model.findall('link'):
            link_pose = compose(model_pose, child_pose(link))
            for collision in link.findall('collision'):
                collision_pose = compose(link_pose, child_pose(collision))
                box = collision.find('geometry/box/size')
                if box is None:
                    raise ValueError(f"unsupported collision geometry in {model.get('name')}/{collision.get('name')}")
                sx, sy, sz = (float(v) for v in box.text.split())
                # Ignore floor-plane collisions. Keep low furniture because the robot body can hit it.
                if collision_pose[2] + sz / 2 > 0.06:
                    yield collision_pose, sx, sy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sdf', type=Path)
    parser.add_argument('-f', '--output', type=Path, required=True,
                        help='output filename prefix, without .pgm or .yaml')
    parser.add_argument('--resolution', type=float, default=0.05)
    parser.add_argument('--free-bounds', nargs=4, type=float,
                        metavar=('X_MIN', 'Y_MIN', 'X_MAX', 'Y_MAX'),
                        default=(-6.8588, -5.7338, 6.8588, 5.7113),
                        help='world-coordinate rectangle marked free before collision boxes are applied')
    args = parser.parse_args()

    root = ET.parse(args.sdf).getroot()
    world = root.find('world')
    if world is None:
        raise ValueError('SDF has no <world>')

    floor = next((c for m in world.findall('model') if m.get('name') == 'floor'
                  for l in m.findall('link') for c in l.findall('collision')
                  if c.find('geometry/box/size') is not None), None)
    if floor is None:
        raise ValueError('SDF has no floor box')
    floor_pose = child_pose(world.find("model[@name='floor']"))
    floor_collision_pose = compose(floor_pose, compose(child_pose(world.find("model[@name='floor']/link")), child_pose(floor)))
    floor_size = [float(v) for v in floor.find('geometry/box/size').text.split()]
    resolution = args.resolution
    width = round(floor_size[0] / resolution)
    height = round(floor_size[1] / resolution)
    xmin = floor_collision_pose[0] - floor_size[0] / 2
    ymin = floor_collision_pose[1] - floor_size[1] / 2
    xmax, ymax = xmin + width * resolution, ymin + height * resolution

    free_xmin, free_ymin, free_xmax, free_ymax = args.free_bounds
    grid = bytearray([205]) * (width * height)  # unknown outside the building
    for row in range(height):
        y = ymax - (row + 0.5) * resolution
        if free_ymin <= y <= free_ymax:
            start = max(0, math.ceil((free_xmin - xmin) / resolution - 0.5))
            end = min(width, math.floor((free_xmax - xmin) / resolution - 0.5) + 1)
            if start < end:
                offset = row * width
                grid[offset + start:offset + end] = bytes([254]) * (end - start)

    obstacles = list(walk_models(world, (0, 0, 0, 0, 0, 0)))
    for pose, sx, sy in obstacles:
        cx, cy, _, _, _, yaw = pose
        c, s = math.cos(yaw), math.sin(yaw)
        # Restrict pixel checks to the rotated box's axis-aligned bounds.
        rx = (abs(c) * sx + abs(s) * sy) / 2
        ry = (abs(s) * sx + abs(c) * sy) / 2
        col0 = max(0, math.floor((cx - rx - xmin) / resolution))
        col1 = min(width, math.ceil((cx + rx - xmin) / resolution))
        row0 = max(0, math.floor((ymax - (cy + ry)) / resolution))
        row1 = min(height, math.ceil((ymax - (cy - ry)) / resolution))
        for row in range(row0, row1):
            y = ymax - (row + 0.5) * resolution
            for col in range(col0, col1):
                x = xmin + (col + 0.5) * resolution
                dx, dy = x - cx, y - cy
                local_x, local_y = c * dx + s * dy, -s * dx + c * dy
                if abs(local_x) <= sx / 2 and abs(local_y) <= sy / 2:
                    grid[row * width + col] = 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image = args.output.with_suffix('.pgm')
    yaml = args.output.with_suffix('.yaml')
    with image.open('wb') as out:
        out.write(f'P5\n{width} {height}\n255\n'.encode())
        out.write(grid)
    yaml.write_text(
        f'image: {image.name}\nmode: trinary\nresolution: {resolution:.3f}\n'
        f'origin: [{xmin:.3f}, {ymin:.3f}, 0]\nnegate: 0\n'
        'occupied_thresh: 0.65\nfree_thresh: 0.1962\n', encoding='utf-8')
    print(f'Wrote {image} and {yaml}: {width}x{height} @ {resolution:g} m/px; '
          f'{len(obstacles)} collision boxes rasterized')


if __name__ == '__main__':
    main()
