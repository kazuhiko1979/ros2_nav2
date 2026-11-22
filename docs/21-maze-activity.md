# 21. 5×5迷路を作ってナビゲーション

講座の迷路課題を、ROS 2 Jazzy / Gazebo Harmonic 用に用意した。maze generator の参考 PNG を [assets/5_by_5_maze.png](../assets/5_by_5_maze.png) に保存し、壁の配置を同じにした。迷路は 5×5区画、通路の有効幅は 1.2 m。南側に入口、北側に出口があり、外側を回り込めないように外周を閉じた。Waffle は南の前室から入口へ向けて生成される。

**今回の地図は SDF から生成する。** Waffle を迷路内で走行させて SLAM 地図を作る方法は時間がかかるため、今回は行わない。この地図は Gazebo の衝突形状を写した基準地図であり、センサー観測から作った SLAM 地図ではない。

## 迷路を生成する

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
python3 scripts/generate_maze_world.py
gz sdf -k worlds/maze_5x5.sdf
```

ワールドは `worlds/maze_5x5.sdf` に出力される。別の迷路にする場合はスクリプト内の `OPEN_EW` と `OPEN_NS` の通路配置を変更して再生成する。

## Waffle を入口に配置する

ワークスペースの環境を読み込んで、迷路用 launch を使う。既定位置は `(x=0, y=-4.0)`、向きは北（`+Y`）。

```bash
source ./setup.bash
ros2 launch ros2_nav2_custom_world maze_world.launch.py
```

位置や向きを変える場合は `x_pose:=... y_pose:=... yaw:=...` を指定できる。描画を減らす場合は `gui:=false` を付ける。

## SDF から地図を作る

ワークスペースのルートで実行する。壁や家具の衝突形状を占有セルにし、指定した迷路内を空きセルとして occupancy grid を生成する。

```bash
python3 scripts/sdf_to_occupancy_map.py worlds/maze_5x5.sdf \
  -f maps/maze_5x5 --free-bounds -3.52 -4.34 3.52 4.34
```

`maps/maze_5x5.pgm` と `maps/maze_5x5.yaml` ができる。地図の解像度は 0.05 m/セル、サイズは 184×184セル、原点は `(-4.6, -4.6)`。別の maze SDF に使う場合は `--free-bounds` をそのワールドの自由領域に合わせる。

SLAM を練習するときは、別途 Cartographer と teleop を起動して Waffle を実際に走らせ、`map_saver_cli` で別名の地図を保存する。

## Nav2 で走る

ワークスペース直下から次のコマンドを実行すると、Gazebo、Waffle、保存済み迷路地図を使う Nav2、RViz がまとめて起動する。

```bash
source ./setup.bash
ros2 launch launch/maze_navigation.launch.py
```

RViz は地図、LiDAR、TF、ロボットモデルを表示する。AMCL の初期位置には Waffle の出発位置と向きが自動で設定される。地図とスキャンがそろったら、**Nav2 Goal** で目標を送る。Gazebo のウィンドウを省く場合は `gui:=false` を付ける。

### 個別に起動する場合

Gazebo と Waffle を入口に再配置し、別ターミナルで保存した YAML 地図を Nav2 に渡す。

```bash
source ./setup.bash
ros2 launch ros2_nav2_custom_world maze_world.launch.py
```

```bash
source ./setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:="$PWD/maps/maze_5x5.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

RViz で **2D Pose Estimate** を使い、地図上の入口にいるロボットの位置と向きを指定する。次に **Nav2 Goal** を迷路の奥に置く。曲がり角や U 字の折り返しで計画が難しいときは、角の手前と後ろに waypoint を追加し **Start Waypoint Following** を使う。

## 確認状況

- Gazebo で迷路 SDF の読み込みと Waffle の生成を確認済み。
- `map_server` で作成した地図を読み込み、184×184セル、0.05 m/セル、原点 `(-4.6, -4.6)` として配信することを確認済み。
- 一括起動で AMCL の初期位置、`map → base_scan` の TF、RViz による地図と LiDAR の購読を確認済み。
- 南入口付近の 2 目標への走行は、[Simple Commander の実習](24-generic-slam-and-navigation.md#python-から走行目標を送る)で成功を確認済み。

この SDF 由来地図はシミュレーションの基準用。実機や未知環境では、SLAM で作った地図を使う。
