# 08. 保存済み地図でナビゲーション

確認日: 2026-11-11

## TurtleBot3 World で実行

別々のターミナルで、どちらもこのフォルダの `setup.bash` を読み込む。World には World で作成した地図を使う。

ターミナル 1（Gazebo Harmonic）:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Gazebo でロボットが生成されてから、ターミナル 2（Nav2 と RViz）:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True map:="$PWD/maps/my_map.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

`map` には画像の `.pgm` ではなく `.yaml` を指定する。YAML 内の相対画像パスを地図サーバーが解決する。シミュレーション時刻は Gazebo、Nav2 の両方で使う。
`params_file` はこのフォルダの Waffle 用設定。Jazzy の TurtleBot3 パッケージにある `NavigateThroughPoses` 用の動作ツリー指定と、レーザーが無限遠を返したときの障害物消去設定を補正している。詳細は [09. ウェイポイント追従](09-waypoints.md) と [10. 新しく現れた障害物](10-dynamic-obstacles.md)。

## RViz で操作

1. 地図が表示されたら、Gazebo のロボット位置と向きを確認する。
2. RViz の **2D Pose Estimate** で、地図上のロボットの位置をクリックし、ドラッグした矢印をロボットの向きに合わせる。この操作で AMCL に初期位置を渡す。World の初期スポーン位置は `(-2.0, -0.5)`、向きは `+X`。
3. レーザースキャンと地図上の壁が重なることを確認する。位置がずれた場合は初期位置を入れ直す。
4. 白い走行可能領域で **Nav2 Goal** をクリックし、ドラッグして到着時の向きを指定する。ロボットの走行と、Nav2 の目標結果を確認する。

障害物や地図の外側を目標にすると、経路を作れず目標が失敗する場合がある。Nav2 だけを再起動した後は、Gazebo 内のロボットの**現在位置**を再度初期位置として指定する。

## この PC での確認結果

- Gazebo Harmonic で Waffle が生成され、`/clock` と `/scan` を受信した。
- Nav2 の `map_server` と `amcl` は `active`。`/map` の解像度は `0.05 m`、幅 `156` セル、高さ `154` セル、原点は `(-4.034, -2.887)` で、`maps/my_map.yaml` と一致した。
- 初期位置 `(-2.0, -0.5)` を `/initialpose` に送ると、`/amcl_pose` が発行された。
- シミュレーション上で近い自由空間 `(-1.5, -0.5)` に `NavigateToPose` 目標を送信し、結果は `SUCCEEDED`（`error_code: 0`）。講座の Humble 向け Cyclone DDS 設定や `/opt/ros` の編集は不要だった。

RViz のクリック操作自体は、この検証では実施していない。上記の走行確認は同等の ROS 2 トピックとアクションを使った。

## 参照

- [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
