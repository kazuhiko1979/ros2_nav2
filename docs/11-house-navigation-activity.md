# 11. House の地図で巡回する課題

確認日: 2026-11-12

## 課題

SLAM で保存した TurtleBot3 House の地図を使い、ロボットを室内の複数の部屋へ移動させる。最初は近い地点への単独の **Nav2 Goal** を試し、成功したら少し遠い地点へ進む。最後に **Waypoint Following** で複数の部屋を順番に巡回する。部屋の選び方と巡回順は、自分で地図を見て決める。

## 起動

前の World シミュレーションや Nav2 が動いていれば `Ctrl+C` で停止する。以下は**別々のターミナル**で、どちらも同じワークスペースを読み込む。

ターミナル 1（Gazebo Harmonic の House）:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

ロボットが生成されたら、ターミナル 2（保存済み House 地図、Nav2、RViz）:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True map:="$PWD/maps/my_house.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

`my_map.yaml` は World 用なので House では `my_house.yaml` を選ぶ。`setup.bash` は `TURTLEBOT3_MODEL` が未指定なら `waffle` にする。この実習では Waffle と保存済み House 地図の組み合わせで地図読み込みまで確認した。

## RViz で進める

1. 地図とレーザースキャンが表示されたら、**2D Pose Estimate** で Gazebo 内のロボットの現在位置と向きを指定する。既定のスポーン位置は約 `(-2.0, -0.5)`、向きは `+X`。壁とスキャンの重なりで位置を確かめる。
2. まず、近くの白い自由空間に **Nav2 Goal** を1つ置き、到着を確認する。次に、部屋の入口や廊下を経由して別の部屋へ進める。
3. 数か所の単独目標が成功したら、**Waypoint / Nav Through Poses Mode** に切り替え、通りたい部屋に順番に **Nav2 Goal** で地点を登録する。**Start Waypoint Following** で開始する。
4. ロボットが各地点を通ったか確認する。途中の地点に失敗しても次を試す設定なので、最後の表示だけでなく未到達地点も確認する。

目標は壁・家具・灰色の未観測領域から距離を取り、ドアの幅を考えて置く。通れない地点で目標が失敗した場合は、近い自由空間やドアの手前に置き直す。ナビゲーションを再起動した場合は、Gazebo 内の**現在位置**で初期位置を再指定する。

## この PC で確認した範囲

- Gazebo Harmonic の House で Waffle が起動し、`/scan` と `/odom` を受信した。
- `my_house.yaml` を Nav2 が読み込み、地図は **310 × 222 セル、0.05 m/セル**、原点は `(-5.76, -5.14)`。`map_server` と AMCL は active になった。
- 初期位置 `(-2.0, -0.5)` を渡すと `/amcl_pose` が発行され、`bt_navigator` と `waypoint_follower` は active になった。
- Gazebo は `Wood_Floor_Dark.jpg` と `Maple.jpg` のテクスチャ解決警告を出した。ロボット生成、センサー、地図読み込みは確認できた。

各部屋への目標走行と巡回の成否は、この課題の実施結果として未記録。地図画像の壁やドアの連続性もまだ目視評価していない。

## 参照

- [ROBOTIS TurtleBot3 シミュレーション](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/)
- [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
- [09. ウェイポイント追従](09-waypoints.md)
