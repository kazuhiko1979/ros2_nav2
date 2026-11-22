# 24. SLAM Toolbox と Nav2 の共通起動手順

講義 PDF の Section 7 を ROS 2 Jazzy と Gazebo Harmonic に合わせた。地図作成では SLAM Toolbox が `/scan` と TF を使って `/map` と `map → odom` を生成する。保存地図で走る段階では、Map Server が地図を読み込み、AMCL が `map → odom` を配信する。[Nav2 Jazzy の SLAM チュートリアル](https://docs.nav2.org/jazzy/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/)

各ターミナルで、ワークスペース直下で `source ./setup.bash` を実行しておく。

## 迷路ワールドを一括起動する

同じ迷路を使って SLAM と保存地図での走行を切り替えられる。地図作成中に Nav2 で目標を送る場合は `navigation:=true` を付ける。手動で地図を作る場合は別ターミナルでキーボード操作を起動し、下の手順で保存する。

| 目的 | 起動コマンド |
| --- | --- |
| SLAM と RViz を起動 | `ros2 launch launch/maze_slam.launch.py` |
| SLAM 中に Nav2 で走行 | `ros2 launch launch/maze_slam.launch.py navigation:=true` |
| 保存済み迷路地図で Nav2 を起動 | `ros2 launch launch/maze_navigation.launch.py` |

各 launch は `IncludeLaunchDescription` でロボットと各パッケージの起動ファイルをまとめ、`Node` で RViz を起動する。独自ロボットに応用するときは、ロボット側の launch と各設定ファイルを差し替える。地図作成と保存済み地図での走行は、片方を停止してから切り替える。

## 1. ロボットを起動する

```bash
ros2 launch launch/maze_world.launch.py
```

この例の Waffle は `/scan`（`sensor_msgs/msg/LaserScan`）、`/odom`、`odom → base_footprint → base_link → base_scan` を提供し、`/cmd_vel` に `TwistStamped` を受け取る。独自ロボットではこの起動コマンドを自分のドライバーやシミュレーションに替える。講義の `my_robot.urdf` の表示は、駆動とセンサーを追加する前の段階。[オドメトリ・センサー・車体制御](23-custom-robot-odometry-sensors-control.md)

## 2. SLAM Toolbox で地図を作って保存する

ロボットを起動したまま、別ターミナルで SLAM Toolbox を起動する。Jazzy 用の `ros-jazzy-slam-toolbox` はこの環境に導入済み。

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```

この環境の既定設定は `/scan` と `base_footprint` を使用する。独自ロボットのトピック名やフレームが違う場合は、設定ファイルの `scan_topic`、`base_frame`、`odom_frame` を合わせ、`slam_params_file:=/path/to/config.yaml` で渡す。[SLAM Toolbox Jazzy](https://github.com/SteveMacenski/slam_toolbox/tree/jazzy)

RViz とキーボード操作をそれぞれ別のターミナルで起動する。

```bash
rviz2 -d "$PWD/rviz/slam_toolbox_mapping.rviz" --ros-args -p use_sim_time:=true
```

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

手動で地図を作る場合は SLAM Toolbox だけで地図を生成できる。講義のように地図作成中も自律走行する場合は、手動操作の代わりに Nav2 のナビゲーション部分を起動し、次節の Nav2 用 RViz 設定で目標を送る。この段階では SLAM Toolbox が自己位置推定を担う。

```bash
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=true params_file:="$PWD/config/waffle_nav2.yaml"
```

必要な範囲を走ったら、SLAM Toolbox を停止する前に地図を保存する。出力名の `_slam` で、SDF 由来の迷路地図と区別する。

```bash
ros2 run nav2_map_server map_saver_cli -f "$PWD/maps/maze_5x5_slam" --fmt pgm
```

`maze_5x5_slam.pgm` と `maze_5x5_slam.yaml` が生成される。

## 3. 保存済み地図で走行する

前の手順で起動したノードを停止し、手順 1 でロボットを起動し直す。別ターミナルで Nav2 一式を起動する。以下は既存の SDF 由来の地図を使う例。SLAM で保存した地図を使う場合は `map:=` に `maps/maze_5x5_slam.yaml` のパスを指定する。

```bash
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=true slam:=False \
  map:="$PWD/maps/maze_5x5.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

別ターミナルで、地図・コストマップ・Nav2 パネルを設定済みの RViz を開く。

```bash
rviz2 -d /opt/ros/jazzy/share/nav2_bringup/rviz/nav2_default_view.rviz \
  --ros-args -p use_sim_time:=true
```

1. **2D Pose Estimate** でロボットの初期位置と向きを指定する。SDF 由来の迷路地図では `(0, -4.0)`、向きは北（`+Y`）。SLAM 地図では、地図上で出発点を確認する。
2. レーザースキャンと地図の壁が合うことを確認する。
3. **Nav2 Goal** で目標を指定する。

地図が表示されない場合は、**Fixed Frame** が `map`、Map の **Topic** が `/map`、**Durability Policy** が **Transient Local** か確認する。これで RViz を後から起動しても配信済みの地図を受け取れる。

実機で ROS 2 のシステム時刻を使う構成では、各ノードの `use_sim_time` を `false` にする。

## RViz の操作を ROS 2 から確認する

迷路の Nav2 を起動してから、別ターミナルでワークスペースの設定を読み込み、次を実行する。

```bash
ros2 topic info /initialpose
ros2 action list -t
ros2 action info /navigate_to_pose
ros2 action info /follow_waypoints
```

| RViz の操作 | ROS 2 の窓口 | Simple Commander のメソッド |
| --- | --- | --- |
| **2D Pose Estimate** | `/initialpose` トピック（`geometry_msgs/msg/PoseWithCovarianceStamped`）。AMCL が購読する | `setInitialPose(pose)` |
| **Nav2 Goal** | `/navigate_to_pose` アクション（`nav2_msgs/action/NavigateToPose`）。BT Navigator が処理する | `goToPose(pose)` |
| **Start Waypoint Following** | `/follow_waypoints` アクション（`nav2_msgs/action/FollowWaypoints`） | `followWaypoints(poses)` |

初期位置のメッセージを見るには `ros2 topic echo /initialpose --once` を実行してから、RViz で **2D Pose Estimate** を操作する。メッセージには座標フレーム `map`、時刻、位置、向き、推定の不確かさが入る。平面で旋回角が `yaw` ラジアンなら、向きのクォータニオンは `(x, y, z, w) = (0, 0, sin(yaw/2), cos(yaw/2))`。迷路の南入口で北を向く例では、位置は `(0, -4.0)`、向きはおよそ `(0, 0, 0.7071, 0.7071)`。

初期位置は「自分はここにいる」という推定値を渡す。走行目標は「ここまで走ってほしい」という依頼で、アクションから進捗や最終結果を受け取れる。迷路用の一括起動では、AMCL が起動時に設定から初期位置を取得するので、普段の操作では手入力を省ける。

Python の `BasicNavigator` は `PoseStamped` を受け取り、初期位置の配信やアクションクライアントの処理を担当する。シミュレーションで使う場合は Python 側の ROS ノードもシミュレーション時刻に合わせる。目標を送った後は `isTaskComplete()` で完了を確認し、`getResult()` で結果を取得する。[Nav2 Jazzy Simple Commander API](https://docs.nav2.org/jazzy/configuration_and_development/simple_commander_api/simple_commander_api/)

## Python から迷路の初期位置を設定する

一括起動の初期位置設定を無効にすると、Python で RViz の **2D Pose Estimate** に相当する操作を練習できる。ワークスペース直下で次を実行する。

```bash
source ./setup.bash
ros2 launch launch/maze_navigation.launch.py auto_initial_pose:=false
```

別ターミナルでワークスペース直下に移動し、次を実行する。

```bash
source ./setup.bash
/usr/bin/python3 scripts/set_maze_initial_pose.py
```

スクリプトはシミュレーション時刻で `PoseStamped` を作り、`map` 座標の `(0, -4.0)`、向きは `+Y`（`+X` から反時計回りに 90°）を `setInitialPose()` に渡す。平面上の向きは Python 標準の `math` でクォータニオンへ変換する。`waitUntilNav2Active()` は AMCL の位置推定と BT Navigator の有効化を待つ。[スクリプト](../scripts/set_maze_initial_pose.py) · [Nav2 Jazzy Simple Commander API](https://docs.nav2.org/jazzy/configuration_and_development/simple_commander_api/simple_commander_api/)

ロボットの出発位置を変更した場合は、実際の位置と向きに合わせてスクリプトに `--x`、`--y`、`--yaw-deg` を指定する。シミュレーション時刻が進むように Gazebo を再生状態にする。画面なしで試す場合は launch に `gui:=false rviz:=false` を追加する。

## Python から走行目標を送る

手動で初期化する実習では、前節と同じく `auto_initial_pose:=false` で迷路を起動する。別ターミナルで `source ./setup.bash` を実行し、初期位置の設定と最初の目標送信を行う。

```bash
/usr/bin/python3 scripts/set_maze_initial_pose.py --set-initial-pose --goal 0 -3 90
```

`--goal` の順序は地図上の X、Y（m）、到着時の向き（+X から反時計回りの度数）。この目標は南入口の約 1 m 先で、到着時は北向き。スクリプトは同じ `map` 座標系で初期位置と目標を作り、`goToPose()` で目標を送る。走行中は現在位置と経路の残り距離を表示し、`isTaskComplete()` が完了を返したあとに `getResult()` で `SUCCEEDED`、`FAILED`、`CANCELED` などを判定する。[Nav2 Jazzy Simple Commander API](https://docs.nav2.org/jazzy/configuration_and_development/simple_commander_api/simple_commander_api/)

同じシミュレーションで次の目標を送る場合は、`--set-initial-pose` を外す。AMCL が追跡した現在位置から走行する。通常の一括起動で初期位置が自動設定されている場合も、この形式で目標だけを送れる。

```bash
/usr/bin/python3 scripts/set_maze_initial_pose.py --goal 0 -2.2 90
```

走行中に `Ctrl+C` を押すと目標のキャンセルを要求する。`--goal` を省略すると、前節と同じく初期位置の設定だけを行う。

## Python から経由点を順番に送る

講義のテンプレートと同様に、位置と向きを作る処理は `make_pose()` にまとめている。迷路で使う座標は、スクリプトの `--waypoint X Y YAW_DEG` に順番に指定する。各点の単位は `--goal` と同じ。スクリプトは `PoseStamped` のリストを作り、`followWaypoints()` で一度に渡す。

前節と同様に `auto_initial_pose:=false` で迷路を新規起動した場合の例。

```bash
source ./setup.bash
/usr/bin/python3 scripts/set_maze_initial_pose.py --set-initial-pose \
  --waypoint 0 -3.45 90 --waypoint 0 -2.85 90 --waypoint 0 -2.2 90
```

初期位置がすでに設定されている場合は `--set-initial-pose` を外す。`--repeat 2` を付けると、1 回目の完了後に先頭の経由点から同じ順序でもう 1 回走る。

繰り返す経路を決めるときは、最後の経由点から最初の経由点へ戻る区間も考える。上の 3 点を繰り返す試験では、1 回目は全点に到達したが、2 回目の折り返しは試験の制限時間内に完了しなかった。

フィードバックは現在向かっている経由点の番号を表示する。Waffle の設定では未到達の経由点があっても Nav2 は次へ進めるため、最後にアクションの終了状態と未到達リストの両方を確認する。未到達があれば番号を表示して異常終了し、次の繰り返しは行わない。[Nav2 Jazzy Simple Commander API](https://docs.nav2.org/jazzy/configuration_and_development/simple_commander_api/simple_commander_api/)

## 独自ロボットで最初に確認する Nav2 設定

現在の [Waffle 用設定](../config/waffle_nav2.yaml) を出発点にする。表の値はこのリポジトリで使っている設定値。

| 確認項目 | Waffle 用設定と調整箇所 |
| --- | --- |
| 座標フレーム | AMCL は `map`、`odom`、`base_footprint`。コストマップは車体基準に `base_link` を使う。URDF と TF を見て、各ノードの設定を合わせる |
| 移動モデル | AMCL の `robot_model_type` は `nav2_amcl::DifferentialMotionModel`。駆動方式に合わせて選ぶ |
| 速度と加減速 | コントローラの上限は前進 0.3 m/s、旋回 1.0 rad/s。実機の制限に合わせ、速度平滑化や車体側の上限も確認する |
| 車体の大きさ | ローカル・グローバルのコストマップはどちらも `robot_radius: 0.15` m。円で近似できる車体は半径、形が重要な車体は多角形の `footprint` を実寸に合わせる |
| コストマップの解像度 | ローカル・グローバルとも `resolution: 0.05` m。狭い通路の表現と計算量を見ながら調整する |
| センサーと速度指令 | スキャン、オドメトリのトピック名と、`cmd_vel` のメッセージ型をロボット側とそろえる |

車体形状の設定例は Nav2 の公式ガイドも参照できる。[Nav2 Jazzy のフットプリント設定](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/footprint/setup_footprint/)

## この環境での確認結果

- SLAM Toolbox が迷路の入口付近の地図を配信し、`map_saver_cli` が試験用の PGM と YAML を一時フォルダに保存した。地図は 74×131 セル、解像度は 5 cm/セル。
- `bringup_launch.py` が既存の迷路地図を 184×184 セル、5 cm/セルで配信し、AMCL が有効になった。インストール済みの Jazzy 版では `slam:=False` の表記を使う。
- 一括起動の `navigation:=true` で、SLAM Toolbox が `/map` を配信し、Nav2 のノードが有効になった。
- 保存地図での一括起動では、AMCL が `/initialpose` を購読し、`/navigate_to_pose` と `/follow_waypoints` のアクションサーバーが要求を受け付けられることを確認した。
- 自動初期化と画面表示を無効にした試験では、Python から送った `(0, -4.0)`、yaw `1.571` rad を AMCL が受け取り、`waitUntilNav2Active()` が完了した。
- Gazebo で Python から初期位置を設定して `(0, -3.0)` へ走行し、続けて初期位置を再設定せず `(0, -2.2)` へ走行した。両方とも北向きの目標で `SUCCEEDED`。2 回目の開始位置は Nav2 のログで約 `(0, -3.24)` だった。成功判定には設定された到着許容差が適用される。
- Gazebo で `followWaypoints()` に 3 点を送り、順に全点へ到達することを確認した。入口近くの 1 点を `--repeat 2` で指定した試験では、2 回とも `SUCCEEDED` になった。
