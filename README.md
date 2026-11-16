# ros2_nav2

## コンセプト

「Finally Understand the Nav2 Stack with ROS2 - SLAM, Mapping, Navigation, Gazebo Simulation, Python Code - Step by Step」の学習を、このフォルダで段階的に進める。Gazebo のシミュレーションを起点に、地図作成から自己位置推定、Nav2 による経路計画・走行、Python からの操作までを一つの流れとして理解する。

各段階では「何を動かしたか」「どのトピック・フレーム・設定が関わるか」「どう動作を確認したか」を記録し、手順を再現できる状態にする。

## 学習の流れ

1. ROS 2 と Gazebo の実行環境を確認する。
2. ロボットとセンサーをシミュレーションで動かす。
3. SLAM で地図を作成・保存する。
4. 保存した地図で自己位置を推定する。
5. Nav2 で目標地点まで走行し、経路計画と制御の役割を確認する。
6. Python から目標地点の送信や動作確認を行う。

この環境では Ubuntu 24.04 と ROS 2 Jazzy を使う。講座の Humble 向け手順を読み替える際の判断と導入セクションの要点は、[学習ノート](docs/01-setup.md)に記録する。
補助ツールの確認結果は [ツールの学習ノート](docs/02-tools.md)に記録する。
SLAM と地図作成の手順は [地図作成の学習ノート](docs/03-slam-map.md)に記録する。
TurtleBot3 の起動と操作の確認結果は [シミュレーションの学習ノート](docs/04-turtlebot3-simulation.md)に記録する。
保存した地図の値と形式は [地図形式の学習ノート](docs/05-map-format.md)に記録する。
House 地図作成の課題と解答は [House の学習ノート](docs/06-house-activity.md)に記録する。
ナビゲーション編の準備と講座の修正手順の確認結果は [ナビゲーション準備ノート](docs/07-navigation-prep.md)に記録する。
World の保存済み地図を使った起動・初期位置指定・目標走行は [ナビゲーション実習ノート](docs/08-navigation-world.md)に記録する。
複数地点の走行と Jazzy の Waffle 設定修正は [ウェイポイント実習ノート](docs/09-waypoints.md)に記録する。
走行中に現れる障害物の検出と Gazebo Harmonic での試し方は [動的障害物の学習ノート](docs/10-dynamic-obstacles.md)に記録する。
House の保存地図を使った部屋巡回の課題と確認結果は [House ナビゲーション課題ノート](docs/11-house-navigation-activity.md)に記録する。
Nav2 の全体経路、コストマップ、局所制御の役割は [Nav2 アーキテクチャの学習ノート](docs/12-nav2-architecture.md)に記録する。
コストマップの余裕、更新周期、到着判定を調べる手順は [Nav2 パラメータの学習ノート](docs/13-nav2-parameters.md)に記録する。
経路計算・追従が失敗したときの回復動作は [Nav2 回復動作の学習ノート](docs/14-nav2-recovery.md)に記録する。
地図・オドメトリ・機体・LiDAR の座標関係は [TF の学習ノート](docs/15-tf-frames.md)に記録する。
講座で示された3枚の構成図の要点は [Nav2 の図解まとめ](docs/16-nav2-three-diagrams.md)に記録する。
Gazebo Harmonic で間取り図から作る試作ワールドは [カスタムワールドの学習ノート](docs/17-custom-gazebo-world.md)に記録する。
そのワールドへの家具の配置と起動方法は [物体配置の学習ノート](docs/18-custom-world-objects.md)に記録する。

## このフォルダを ROS 2 ワークスペースとして使う

このフォルダの `src/` に ROS 2 パッケージを置く。新しいターミナルでは、フォルダに移動して環境を読み込む。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
echo "$ROS_DISTRO"  # jazzy
echo "$TURTLEBOT3_MODEL"  # waffle（TurtleBot3 の既定モデル）
```

パッケージを追加した後は、フォルダ直下でビルドする。

```bash
colcon build --symlink-install --base-paths src
source ./setup.bash
```

`setup.bash` は Jazzy と、ビルド済みならこのワークスペースの `install/local_setup.bash` を読み込む。TurtleBot3 のモデルが未指定なら `waffle` を設定する。`build/`、`install/`、`log/` は生成物として Git の追跡対象から除外している。
ROS のログもこのフォルダの `log/ros/` に保存する。
