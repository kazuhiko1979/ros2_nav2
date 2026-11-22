#!/usr/bin/env python3
"""Generate a Gazebo SDF matching the supplied 5x5 maze PNG."""

from pathlib import Path


N = 5
PASSAGE = 1.2
SCALE = PASSAGE / 14.0  # The clear path in the PNG is 14 px wide.
PITCH = 16.0 * SCALE
WALL = 2.0 * SCALE
GRID = [(pixel - 41) * SCALE for pixel in (1, 17, 33, 49, 65, 81)]
CENTERS = [(pixel - 41) * SCALE for pixel in (9, 25, 41, 57, 73)]
OUT = Path(__file__).resolve().parents[1] / 'worlds' / 'maze_5x5.sdf'

# True means the PNG has an opening between neighboring cells.
OPEN_EW = (
    (True, False, True, True),
    (False, True, False, False),
    (False, True, True, False),
    (True, False, True, False),
    (True, True, False, True),
)
OPEN_NS = (
    (True, True, True, True, True),
    (True, False, False, True, True),
    (False, True, False, False, True),
    (True, False, False, True, True),
)


def collision(name, x, y, sx, sy, height=2.0):
    return f'''      <collision name="{name}_collision"><pose>{x:.4f} {y:.4f} {height/2:.3f} 0 0 0</pose>
        <geometry><box><size>{sx:.4f} {sy:.4f} {height:.3f}</size></box></geometry></collision>
      <visual name="{name}_visual"><pose>{x:.4f} {y:.4f} {height/2:.3f} 0 0 0</pose>
        <geometry><box><size>{sx:.4f} {sy:.4f} {height:.3f}</size></box></geometry>
        <material><ambient>0.72 0.72 0.72 1</ambient><diffuse>0.72 0.72 0.72 1</diffuse></material></visual>'''


def main():
    walls = []

    # Outer boundary. The PNG has north and south openings in its middle column.
    for col in range(N):
        x0, x1 = GRID[col], GRID[col + 1]
        if col == 2:
            fragment = (PITCH - PASSAGE) / 2
            for side, x in enumerate((x0 + fragment/2, x1 - fragment/2)):
                walls.append(collision(f'outer_s_fragment_{side}', x, GRID[0], fragment, WALL))
                walls.append(collision(f'outer_n_fragment_{side}', x, GRID[-1], fragment, WALL))
        else:
            walls.append(collision(f'outer_s_{col}', (x0+x1)/2, GRID[0], PITCH, WALL))
            walls.append(collision(f'outer_n_{col}', (x0+x1)/2, GRID[-1], PITCH, WALL))

    for row in range(N):
        y0, y1 = GRID[row], GRID[row + 1]
        walls.append(collision(f'outer_w_{row}', GRID[0], (y0+y1)/2, WALL, PITCH))
        walls.append(collision(f'outer_e_{row}', GRID[-1], (y0+y1)/2, WALL, PITCH))

    # Interior walls reproduce the pixel layout: a solid segment blocks that cell edge.
    for row in range(N):
        y0, y1 = GRID[row], GRID[row + 1]
        for col in range(N - 1):
            if not OPEN_EW[row][col]:
                walls.append(collision(f'vert_{row}_{col}', GRID[col + 1], (y0+y1)/2, WALL, PITCH))
    for row in range(N - 1):
        for col in range(N):
            if not OPEN_NS[row][col]:
                x0, x1 = GRID[col], GRID[col + 1]
                walls.append(collision(f'horiz_{row}_{col}', (x0+x1)/2, GRID[row+1], PITCH, WALL))

    floor_size = 9.2
    floor = f'''    <model name="floor"><static>true</static><link name="link">
      <collision name="floor_collision"><pose>0 0 -0.025 0 0 0</pose><geometry><box><size>{floor_size} {floor_size} 0.05</size></box></geometry></collision>
      <visual name="floor_visual"><pose>0 0 -0.025 0 0 0</pose><geometry><box><size>{floor_size} {floor_size} 0.05</size></box></geometry>
        <material><ambient>0.8 0.8 0.78 1</ambient><diffuse>0.8 0.8 0.78 1</diffuse></material></visual>
    </link></model>'''
    wall_model = '    <model name="maze_walls"><static>true</static><link name="walls_link">\n' + '\n'.join(walls) + '\n    </link></model>'
    # An outer enclosure forms start/goal vestibules while sealing side bypasses.
    bounds = '    <model name="world_bounds"><static>true</static><link name="bounds_link">\n'
    side_extent, vestibule_extent, bound_thickness = 3.58, 4.4, 0.12
    poses = [(-side_extent, 0, bound_thickness, 2*vestibule_extent),
             (side_extent, 0, bound_thickness, 2*vestibule_extent)]
    opening_half = PASSAGE / 2
    for y in (-vestibule_extent, vestibule_extent):
        poses.extend(((-(side_extent+opening_half)/2, y, side_extent-opening_half, bound_thickness),
                      ((side_extent+opening_half)/2, y, side_extent-opening_half, bound_thickness)))
    for idx, pose in enumerate(poses):
        x, y, sx, sy = pose
        bounds += collision(f'bound_{idx}', x, y, sx, sy) + '\n'
    bounds += '    </link></model>'

    sdf = f'''<?xml version="1.0"?>
<sdf version="1.8"><world name="maze_5x5">
  <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
  <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
  <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
  <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
  <scene><ambient>0.75 0.75 0.75 1</ambient></scene>
  <light name="sun" type="directional"><pose>0 0 10 0 0 0</pose><direction>-0.3 -0.3 -1</direction></light>
{floor}
{wall_model}
{bounds}
</world></sdf>
'''
    OUT.write_text(sdf, encoding='utf-8')
    print(f'Wrote {OUT}; maze matches PNG, passage clear width {PASSAGE:.1f} m; cells={PITCH:.3f} m')


if __name__ == '__main__':
    main()
