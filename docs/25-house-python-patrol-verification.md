# 25. TurtleBot3 House の Python 巡回を起動・確認する

ROS 2 Jazzy、Gazebo Harmonic、TurtleBot3 Waffle を使い、保存済みの House 地図で 6 点を順に巡回する。Python が Nav2 Simple Commander を通じて目標を送る。RViz では地図、LiDAR、ロボットの位置、経路を確認できる。

## 1. 起動する

以前の Gazebo や Nav2 が動いている場合は、起動したターミナルで `Ctrl+C` を押して終了する。以下の各ターミナルで共通の準備をする。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
export TURTLEBOT3_MODEL=waffle
```

**ターミナル 1** で House と Waffle を起動する。

```bash
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

**ターミナル 2** で Nav2 と RViz を起動する。ロボットが生成された後に実行する。

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:="$PWD/maps/my_house.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

**ターミナル 3** で、初期位置の設定と巡回を実行する。

```bash
/usr/bin/python3 scripts/patrol_house.py --set-initial-pose
```

既定の出発点は Gazebo のワールド座標で `(-2.0, -0.5)`。保存地図の `map` 座標では `(0, 0)` に対応し、向きは `+X`。同じシミュレーションで続けて実行する場合は `--set-initial-pose` を外し、AMCL が追跡している現在位置から始める。

## 2. 巡回を確認する

| 順番 | 地図上の座標 (X, Y)［m］ | 到着時の向き | 場所 |
| --- | --- | --- | --- |
| 1 | (2.95, -0.75) | 90° | 入口の手前 |
| 2 | (2.95, 0.75) | 90° | 入口の内側 |
| 3 | (1.4, 2.6) | 180° | 中央側の室内 |
| 4 | (-2.6, 3.3) | 180° | 北側の通路 |
| 5 | (-4.0, 3.5) | -90° | 西側の部屋へ入った地点 |
| 6 | (-4.3, 2.6) | -90° | 西側の部屋の奥 |

向きは `+X` を基準とし、反時計回りが正。座標を変更する場合は `HOUSE_ROUTE` を編集する。[巡回スクリプト](../scripts/patrol_house.py)

1. RViz で地図を表示し、初期位置設定後に LiDAR の点と地図上の壁が重なることを確認する。
2. ターミナル 3 の `Waypoint 1/6` から `Waypoint 6/6` までの表示で、現在の目標を確認する。この表示は向かっている点を示す。
3. ターミナル 2 の `Task execution at waypoint 0 succeeded` から `waypoint 5` までで、各点の完了を確認する。Nav2 のログでは経由点の番号が 0 から始まる。
4. ターミナル 3 で `Navigation result: SUCCEEDED` を確認し、巡回コマンドの直後に `echo $?` を実行する。終了コード `0` が全点成功。設定上、Nav2 は点を飛ばして走行を続けられるため、`Missed waypoints:` が出た場合は表示された地点を見直す。スクリプトは未到達があると終了コード `1` を返す。

準備状態を切り分けるときは、同じワークスペースを読み込んだ別ターミナルで確認できる。`bt_navigator` と `waypoint_follower` は、初期位置の設定後に `active` になることを確認する。

```bash
ros2 topic echo /amcl_pose --qos-durability transient_local --once
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /waypoint_follower
ros2 action info /follow_waypoints
```

## 前回の検証結果

保存済みの `my_house.yaml` を使い、全 6 点に順番に到達した。最終結果は `SUCCEEDED`、未到達は 0 点、終了コードは `0`。描画負荷を抑えるため、走行試験では画面とカメラ描画を省き、Gazebo の物理更新刻みを 3 ms にした。上記は通常の GUI 付き起動手順で、6 点の走行結果はこの軽量化した試験構成で確認した。

関連手順は [House 地図の実習](11-house-navigation-activity.md) と [Python から経由点を送る方法](24-generic-slam-and-navigation.md#python-から経由点を順番に送る) を参照。
