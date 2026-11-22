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

1. 地図とレーザースキャンが表示されたら、**2D Pose Estimate** でロボットの現在位置と向きを地図上で指定する。既定のスポーン位置は Gazebo のワールド座標で `(-2.0, -0.5)`、保存地図の座標では `(0, 0)`。向きは `+X`。壁とスキャンの重なりで位置を確かめる。
2. まず、近くの白い自由空間に **Nav2 Goal** を1つ置き、到着を確認する。次に、部屋の入口や廊下を経由して別の部屋へ進める。
3. 数か所の単独目標が成功したら、**Waypoint / Nav Through Poses Mode** に切り替え、通りたい部屋に順番に **Nav2 Goal** で地点を登録する。**Start Waypoint Following** で開始する。
4. ロボットが各地点を通ったか確認する。途中の地点に失敗しても次を試す設定なので、最後の表示だけでなく未到達地点も確認する。

目標は壁・家具・灰色の未観測領域から距離を取り、ドアの幅を考えて置く。通れない地点で目標が失敗した場合は、近い自由空間やドアの手前に置き直す。ナビゲーションを再起動した場合は、Gazebo 内の**現在位置**で初期位置を再指定する。

## Python で巡回する

上の手順で House と Nav2 を起動する。RViz は地図・経路・ロボットの位置を見るために使い、目標は Python から送る。ワークスペース直下の別ターミナルで実行する。

```bash
source ./setup.bash
/usr/bin/python3 scripts/patrol_house.py --set-initial-pose
```

このコードは、保存地図での初期位置 `(0, 0)` と向き `+X` を AMCL に渡してから、`followWaypoints()` で経由点を順に送る。経由点は保存済みの `my_house.pgm` に合わせて配置した。座標はスクリプトの `HOUSE_ROUTE` に `(X, Y, 到着時の向き［度］)` の順で記載している。[House 巡回スクリプト](../scripts/patrol_house.py)

初期位置が設定済みなら `--set-initial-pose` を外すと現在位置から実行できる。途中で未到達になった点は、終了時に経由点番号で表示する。

入口を通って中央側の室内を進み、北寄りの通路から西側の部屋へ入る。角と部屋の入口にも経由点を置いた。繰り返し巡回にする場合は、最後の部屋から出発側へ戻る経由点もルートに加える。

## この PC で確認した範囲

- Gazebo Harmonic の House で Waffle が起動し、`/scan` と `/odom` を受信した。
- `my_house.yaml` を Nav2 が読み込み、地図は **310 × 222 セル、0.05 m/セル**、原点は `(-5.76, -5.14)`。`map_server` と AMCL は active になった。
- AMCL が初期位置を受け付け、`bt_navigator` と `waypoint_follower` が active になることを確認した。初期位置には保存地図での座標を使う。
- Gazebo は `Wood_Floor_Dark.jpg` と `Maple.jpg` のテクスチャ解決警告を出した。ロボット生成、センサー、地図読み込みは確認できた。

- Python による House 巡回は、入口前後、中央側の室内、北側通路、西側の部屋を経由する全 6 点で `SUCCEEDED`。未到達は 0 点だった。
- この走行確認では、検証用の Gazebo でカメラ描画を省き、物理の更新刻みを 3 ms に調整した。通常の House 起動設定はそのまま使える。

## 参照

- [ROBOTIS TurtleBot3 シミュレーション](https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/)
- [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
- [09. ウェイポイント追従](09-waypoints.md)
