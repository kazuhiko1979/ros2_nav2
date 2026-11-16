# 03. SLAM で地図を作る

## このセクションの目的

ロボットが移動できる空間の地図を作成し、次のナビゲーション学習で使える形で保存する。SLAM（Simultaneous Localization and Mapping）は、ロボットの位置を推定しながら周囲の地図を作る方法。Gazebo はロボットと環境のシミュレーション、Cartographer は SLAM、RViz は結果の表示を担当する。地図を作る段階ではキーボードでロボットを動かし、自律走行は次のセクションで扱う。

講座付属の「SLAM Steps (ROS2 Nav2 Course - Section 3)」PDFは、TurtleBot3 の起動、Cartographer、キーボード操作、地図保存の4手順を示す。この PC の ROS 2 Jazzy パッケージで、対応する起動ファイル・実行ファイルが存在し、起動引数を読み込めることを確認した。SLAM の起動と検証用地図の保存は確認済み。ワールドを広く走行して作る実習用地図は未作成。

## 実行手順

各手順を**別のターミナル**で実行する。最初に各ターミナルでワークスペースへ移動し、環境とモデルを設定する。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
export TURTLEBOT3_MODEL=waffle
```

1. Gazebo で TurtleBot3 World を起動する。

   ```bash
   ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
   ```

2. 別ターミナルで Cartographer と RViz を起動する。

   ```bash
   ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
   ```

3. 別ターミナルでロボットを操作し、地図に必要な範囲を走行する。

   ```bash
   ros2 run turtlebot3_teleop teleop_keyboard
   ```

4. RViz で地図ができたことを確認し、別ターミナルでこのリポジトリの `maps/` に保存する。Gazebo と Cartographer を終了する**前**に実行する。

   ```bash
   ros2 run nav2_map_server map_saver_cli -f maps/my_map
   ```

保存後に `maps/my_map.yaml` と画像ファイルができているか確認する。地図の内容と品質は、実際の走行後に評価する。

RViz で白は走行可能と推定された領域、黒は障害物、灰は未観測の領域を表す。外側など走行できない場所まで白にする必要はない。ロボットをゆっくり動かし、ときどきその場で回転して周囲を観測する。衝突や急旋回で地図が大きく崩れた場合は、Gazebo、Cartographer、操作ノードを停止して最初からやり直す。

保存でエラーが出た場合は、同じコマンドを繰り返す前に `ros2 topic list -t` で `/map` があるか確認する。地図がまだ発行されていなければ、シミュレーションと Cartographer の起動状態を確認して少し待つ。

## 動作確認結果（2026-11-10）

TurtleBot3 Waffle の Gazebo シミュレーションと Cartographer を起動し、`/scan` と `/map` の発行を確認した。`map_saver_cli` で検証用の地図を `/tmp/ros2_nav2_slam_smoke.pgm` と `.yaml` に保存できた。画像は 93 × 111 ピクセル、解像度は 0.05 m/ピクセル。ロボットを広く走らせていないため、この地図を実習の完成品とは扱わない。検証後は Gazebo と Cartographer を停止した。

## 参照

- 講座付属 PDF: `SLAM Steps (ROS2 Nav2 Course - Section 3)`（ローカル資料。リポジトリにはコピーしない）
- [ROBOTIS TurtleBot3 SLAM Simulation](https://emanual.robotis.com/docs/en/platform/turtlebot3/slam_simulation/)
- [Nav2 Jazzy: Navigating while Mapping](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/)
