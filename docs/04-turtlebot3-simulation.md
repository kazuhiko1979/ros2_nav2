# 04. TurtleBot3 をシミュレーションで動かす

確認日: 2026-11-09

## 講義の内容

SLAM の前提として、ROS 2 で移動でき、LiDAR の計測を出すロボットを用意する。この講義では TurtleBot3 Waffle を使う。2輪の差動駆動で動き、キーボード操作ノードの指令を `/cmd_vel` に送り、LiDAR のデータを `/scan` で確認できる。手動操作中は障害物に衝突しないよう、少しずつ動かして停止する。

## この環境での操作

ターミナル1:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

ターミナル2:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

操作キーは `w`（前進速度を上げる）、`x`（下げる）、`a` / `d`（回転）、`s` またはスペース（停止）。操作するターミナルを選択してキーを押す。終了時は操作ノードと Gazebo のターミナルでそれぞれ `Ctrl+C` を押す。

ターミナル3で構成を確認できる。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 topic list -t
ros2 topic info /cmd_vel -v
```

講義で紹介する単独起動コマンド `gazebo` は Gazebo Classic 用。Jazzy/Harmonic では `gz sim` を使用する。この学習では TurtleBot3 の起動ファイルを使うため、Gazebo を別途単独起動しない。
`TURTLEBOT3_MODEL` はターミナルごとに設定が必要。このワークスペースの `setup.bash` は、未指定なら `waffle` を設定する。別の作業ディレクトリからでも `source /home/kazuh/project/workspaces/ros2_nav2/setup.bash` とすればよい。

## 実測した結果

- Jazzy の `turtlebot3_world.launch.py` が Gazebo Harmonic の `ros_gz_sim` を起動し、Waffle の生成に成功した。
- `/scan`、`/odom`、`/cmd_vel`、`/clock` が発行された。
- `/cmd_vel` の型はこの環境では `geometry_msgs/msg/TwistStamped`。`teleop_keyboard` が発行し、`ros_gz_bridge` が購読していた。
- `w` を短時間押してから `s` で停止すると、`/odom` の x 座標が約 0.000 m から 0.010 m に変化した。
- Gazebo の統計で、起動後のある時点の実時間係数は約 0.98 だった。起動直後の処理は遅かった。
- 検証用の操作ノードと Gazebo は `Ctrl+C` で終了した。

Gazebo の画面を人が目視して確認する作業は未実施。次は SLAM を起動し、RViz で地図の生成を確認する。

## 参照

- [ROBOTIS TurtleBot3 Simulation](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/)
- [Gazebo Harmonic の基本操作](https://gazebosim.org/docs/harmonic/)
