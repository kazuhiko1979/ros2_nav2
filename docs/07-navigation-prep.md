# 07. ナビゲーション編の準備

確認日: 2026-11-11

## これから学ぶ流れ

保存した地図を使い、Gazebo の TurtleBot3 が目的地まで移動する。次の実習では、ロボットとセンサーを起動し、Nav2 に地図を渡し、地図上で初期位置を合わせてから目標地点を指定する。Nav2 は地図と現在のセンサー情報を使って経路を計画し、障害物を避ける。目標地点への到達は、地図の品質、自己位置推定、センサー、経路の可否に左右される。

このフォルダには TurtleBot3 World の `maps/my_map.yaml` と TurtleBot3 House の `maps/my_house.yaml` がある。両方とも対応する PGM が存在する。次の操作では、起動したワールドと同じ地図を選ぶ。

## 講座の Humble 向け修正を Jazzy で確認

講座は、Humble 時代の地図読み込み問題に対して Cyclone DDS への切り替えと AMCL の移動モデル設定変更を案内する。現在の PC は **ROS 2 Jazzy** で、`RMW_IMPLEMENTATION` は未設定、Fast DDS のパッケージが導入済み。Cyclone DDS のパッケージは未導入。これまでの Gazebo・SLAM の通信では問題を観測していないため、DDS の全端末共通設定は変更していない。

`/opt/ros/jazzy/share/turtlebot3_navigation2/param/waffle.yaml` の `robot_model_type` は、講座が修正後として指定する `nav2_amcl::DifferentialMotionModel` に**既に設定済み**。`/opt/ros` 配下のファイルは編集していない。地図読み込みの問題が実際に出たら、起動ログと地図ファイルの指定を確認してから原因を切り分ける。

ナビゲーション本体の起動、地図読み込み、短距離の目標到達は [08. 保存済み地図でナビゲーション](08-navigation-world.md) で検証した。
後続のウェイポイント実習では、Jazzy の TurtleBot3 パラメータに別の誤設定を見つけた。`NavigateThroughPoses` 用の動作ツリーが単一目標用を指していたため、ワークスペース内に修正版を置いた。詳細は [09. ウェイポイント追従](09-waypoints.md)。

## 参照

- [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
- [Nav2 AMCL 設定](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/others/configuring_amcl/)
- [ROS 2 の RMW 実装切り替え](https://docs.ros.org/en/jazzy/Installation/RMW-Implementations/Working-with-multiple-RMW-implementations.html)
