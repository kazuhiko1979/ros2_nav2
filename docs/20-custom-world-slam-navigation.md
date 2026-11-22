# 20. カスタムワールドで SLAM と Nav2

確認日: 2026-11-16

## 講座の内容と、このワークスペースでの対応

講座は「ワールドを SLAM で地図にする → 保存した地図で Nav2 を動かす」という二段階。ここでは ROS 2 Jazzy / Gazebo Harmonic を使用する。講座の `turtlebot3_my_world.launch.py` の代わりに、このリポジトリの `ros2_nav2_custom_world dogtrot_world.launch.py` で家具付きの Dogtrot ワールドと Waffle を起動する。`my_map.yaml` と `my_house.yaml` は別ワールドの地図なので、ここでは使用しない。

このワールドは寸法が分かる SDF から作られているため、Nav2 学習用の地図は衝突形状から直接生成できる。スクリプトは壁・家具を占有セル、建物内を空きセル、外側を未知セルとして出力する。解像度は 5 cm/セル。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
python3 scripts/sdf_to_occupancy_map.py worlds/dogtrot_furnished.sdf -f maps/custom_map
```

これで `maps/custom_map.pgm` と `maps/custom_map.yaml` が作成される。衝突形状を変更した場合は再生成する。この地図は Gazebo の幾何形状を表し、実機のセンサー誤差や SLAM の推定結果は含まない。SLAM の実習には下記の走行手順を使う。

各コマンドは**別のターミナル**で実行する。各ターミナルで最初に以下を実行する。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
```

## SLAM でカスタムワールドの地図を学ぶ場合

ターミナル 1: Gazebo と Waffle を起動する。

```bash
ros2 launch ros2_nav2_custom_world dogtrot_world.launch.py
```

ターミナル 2: シミュレーション時刻を使って Cartographer と RViz を起動する。

```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

ターミナル 3: Waffle をゆっくり動かし、各部屋と通路を観測する。

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

RViz の地図で白は観測済みの空き領域、黒は壁や障害物、灰色は未観測領域。ドアや通路の壁に穴が残らないように、必要な場所で停止・旋回して確認する。家具の裏側などレーザーが届かない灰色部分を無理に埋める必要はない。衝突するとセンサーの姿勢が乱れるため、低速で走らせる。

ターミナル 4: **Gazebo と Cartographer が動いている間に**地図を保存する。`-f` には拡張子を付けない。

```bash
ros2 run nav2_map_server map_saver_cli -f maps/custom_map
ls -lh maps/custom_map.pgm maps/custom_map.yaml
```

画像の拡張子は既定では `.pgm`。保存時に `-f maps/custom_map.yaml` とすると名前に `.yaml` が重複する。二つのファイルができ、画像と YAML が開けることを確認してから、各ターミナルを **Ctrl+C** で止める。地図が空または大きく崩れていたら、保存だけを繰り返さず走行と SLAM をやり直す。

## 2. 保存した地図で Nav2 を起動する

新しいターミナルで Gazebo と Waffle を起動する。地図作成時と**同じワールド、同じ初期位置**を使う。既定の初期位置は `(x=0, y=0)`、向きは `+X`。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch ros2_nav2_custom_world dogtrot_world.launch.py
```

別の新しいターミナルで Nav2 と RViz を起動する。`map` は画像ではなく YAML の絶対パス。既存の Waffle 用 Jazzy 設定を使う。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:="$PWD/maps/custom_map.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

RViz で地図が表示されたら **2D Pose Estimate** で Gazebo 上の実際のロボット位置と向きを指定する。その後、白い空き領域で **Nav2 Goal** を設定する。最初は近い目標で確認し、次にドアを通る目標を試す。複数地点へ行くときは RViz の **Waypoint** モードで地点を追加し、**Start Waypoint Following** を使う。ドアの前後に地点を置くと経路を確認しやすい。

地図を作ったときと異なる初期位置でロボットを生成した場合は、`2D Pose Estimate` に**現在の位置**を指定する。地図とレーザースキャンの壁が一致しないときは初期位置を入れ直す。目標が通れない場所や障害物の中にあると、Nav2 は回復動作の後に失敗することがある。

## この時点の確認範囲

- カスタムワールドで Waffle の生成、`/scan` と `/odom`、短い速度指令による移動は [前節](19-custom-world-turtlebot.md)で確認済み。
- SDF から地図を生成。`maps/custom_map.pgm` は **296 × 250 セル**、解像度 **0.05 m/セル**。
- SLAM でも `/clock`、`/scan`、`/odom`、`/map` を確認し、走行中の地図保存と Nav2 による試験地図の読み込みを確認した。SLAM 走行だけでは建物全体を含む地図にならなかったため、学習用地図には SDF 由来のものを採用。
- Nav2 の経路計画、目標到達、ウェイポイント追従は未確認。

## 参照

- [Nav2: Navigating while Mapping](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/)
- [Nav2: Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
