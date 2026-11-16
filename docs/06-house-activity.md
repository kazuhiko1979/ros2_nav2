# 06. TurtleBot3 House の地図作成課題

確認日: 2026-11-11

## 課題と解答の要点

前回の TurtleBot3 World と同じ流れで、House の**室内**を SLAM で地図にする。屋外まで広く探索する必要はない。解答動画では、壁を黒く連続して描けているかを重視する。壁に穴があると、次のナビゲーションで通り抜け可能な場所と誤認するおそれがある。家具の周辺などに多少の灰色（未観測）が残ってもよい。

この環境には `turtlebot3_house.launch.py` と House のワールドファイルがあり、必要な TurtleBot3・Cartographer・地図保存パッケージも設定済み。`setup.bash` はモデル未指定なら講義で使っている `waffle` を選ぶ。

## 解答動画の実行順

各コマンドは**別のターミナル**で、このリポジトリ直下に移動して `source ./setup.bash` を実行してから使う。

1. House ワールド: `ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py`
2. SLAM と RViz: `ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True`
3. キーボード操作: `ros2 run turtlebot3_teleop teleop_keyboard`
4. 地図保存: `ros2 run nav2_map_server map_saver_cli -f maps/my_house`

**停止前に** `maps/my_house.pgm` と `maps/my_house.yaml` が生成されたことを確認する。既存の `maps/my_map.*` は TurtleBot3 World の地図として残す。最初の House 起動は読み込みに時間がかかる場合がある。

## 現在の状態

2026-11-11 に `maps/my_house.pgm` と `maps/my_house.yaml` があることを確認した。PGM は P5 形式の 310 × 222 セルで、画像データの長さはセル数と一致する。YAML はその画像を参照し、解像度は 0.05 m/セル。画像の構造は確認済みだが、壁の連続性など地図の品質はまだ目視評価していない。

## 参照

- [ROBOTIS TurtleBot3 SLAM Simulation](https://emanual.robotis.com/docs/en/platform/turtlebot3/slam_simulation/)
- [前回のSLAM手順](03-slam-map.md)
