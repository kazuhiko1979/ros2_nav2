# 22. 独自ロボットを Nav2 につなぐための URDF と TF

講義の構成図では、Nav2 が地図・センサー・TF を使って経路を計画し、速度指令を出す。独自ロボット側では、センサーとオドメトリを配信し、速度指令を左右の車輪の動きに変換する。今回は車体と LiDAR の位置関係を URDF で定義し、TF として確認する。

| データ・変換 | 担当 |
| --- | --- |
| `map → odom` | 保存地図で走る場合は AMCL、地図作成中は TF を配信する設定の SLAM ノード |
| `odom → base_footprint` または `odom → base_link` | 車輪オドメトリを計算するドライバー、シミュレータ、またはセンサー融合ノード |
| `base_footprint → base_link → base_scan` | URDF の固定関節を読む `robot_state_publisher` |
| `/odom` | オドメトリを `nav_msgs/msg/Odometry` で配信するノード |
| `/scan` | LiDAR ドライバー。メッセージの `header.frame_id` は実際の LiDAR フレームに合わせる |
| `/cmd_vel` | Nav2 側からの速度指令を受ける車体コントローラ。図では `Twist`。このワークスペースの Waffle 設定では `TwistStamped` を使う |

TF がつながると、例えば LiDAR が「前方 1 m」と測った点を、Nav2 が地図上の座標へ変換できる。`base_scan` はこの例の名前。別名でもセンサーのメッセージと TF が一致していれば使える。[Nav2 Jazzy の TF 設定ガイド](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/transformation/setup_transforms/)

## 講義の URDF と Waffle の比較

`xyz` は親フレームから見た子フレームの位置（m）、`rpy` は X、Y、Z 軸周りの回転（rad）。どちらのモデルも次の固定関節の `rpy` はゼロ。

| 固定関節 | 講義の `my_robot.urdf` の `xyz` | Gazebo 用 Waffle の `xyz` |
| --- | --- | --- |
| `base_footprint → base_link` | `0 0 0.20` | `0 0 0.010` |
| `base_link → base_scan` | `0 0 0.13` | `-0.064 0 0.122` |

講義のファイルでは LiDAR が車体基準から 13 cm 上、床面基準から 33 cm 上にある。文字起こしの「0.30」より実ファイルの `0.13` を参照する。独自ロボットでは LiDAR 筐体の中心ではなく、スキャンの原点と軸が実際の取り付け位置・向きに合うように設定する。

固定関節の TF は `/tf_static` に出る。左右の車輪は `continuous` 関節なので、`/joint_states` の車輪角度に応じて `robot_state_publisher` が `/tf` を配信する。今回の表示では `joint_state_publisher` が確認用の角度を供給する。

## RViz で確認する

講義のロボットモデルは [urdf/my_robot.urdf](../urdf/my_robot.urdf) に保存している。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch launch/inspect_urdf.launch.py \
  model:="$PWD/urdf/my_robot.urdf"
```

起動時に **Fixed Frame** は `base_footprint`、**RobotModel** の参照先は `/robot_description` になり、**TF** も表示される。別の URDF を開く場合は `fixed_frame:=base_link` のように、そのモデルにあるフレームへ変更できる。

すでに開いている RViz に `Frame [map] does not exist` と出ている場合は、**Global Options → Fixed Frame** の `map` を `base_footprint` に変更する。URDF の表示にはロボット自身のフレームを使う。地図を使うナビゲーションでは、自己位置推定や SLAM が `map` と `odom` をつなぐ。

講義のファイルは表示用で、シミュレーションに必要な衝突形状、慣性、センサーや駆動の設定は後の作業で用意する。表示に使う ROS パッケージは `robot_state_publisher`、`joint_state_publisher`、`rviz2`。

Waffle を同じ手順で比較するときは、`model:=` に `/opt/ros/jazzy/share/turtlebot3_gazebo/urdf/turtlebot3_waffle.urdf` を指定する。

講義の URDF は `check_urdf` で読み込みを確認した。起動後、`tf2_echo base_footprint base_scan` では高さ 0.330 m、回転ゼロを取得し、`/tf` では左右の車輪フレームを受信した。
