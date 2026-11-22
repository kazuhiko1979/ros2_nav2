# 23. 独自ロボットのオドメトリ・センサー・車体制御

Nav2 はセンサーと地図を使って進む方向を決め、車体へ速度を指示する。車体側では、その指示を左右の車輪の動きに変換し、実際の動きをエンコーダーで測る。

| 信号 | 内容 | Waffle の ROS 2 トピックと型 |
| --- | --- | --- |
| オドメトリ | 出発時を基準とする位置・向きと、現在の速度の推定値 | `/odom` · `nav_msgs/msg/Odometry` |
| LiDAR | レーザーの方向ごとに測った障害物までの距離 | `/scan` · `sensor_msgs/msg/LaserScan` |
| IMU | 角速度や加速度。センサー融合に使える | `/imu` · `sensor_msgs/msg/Imu` |
| 速度指令 | 差動二輪なら前後の速度 `linear.x`（m/s）と旋回速度 `angular.z`（rad/s） | `/cmd_vel` · `geometry_msgs/msg/TwistStamped` |

トピック名は設定で変更できる。速度指令の型は Nav2 と受け取る側でそろえる。講義では `Twist` が示されているが、このワークスペースの Jazzy 用 Waffle 設定と Gazebo ブリッジは `TwistStamped` を使う。

## オドメトリと TF

車輪の回転から移動量を足し合わせるのは、歩数と歩幅で歩いた距離を見積もるのに似ている。車輪が滑ると誤差が積み重なる。これがドリフト。短い時間の動きは `odom` で追跡し、保存地図を使う場合は AMCL がレーザーと地図を照合して `map → odom` を更新する。

この Waffle の TF は `map → odom → base_footprint → base_link → base_scan` の順でつながる。**`map` が `odom` の親**。Gazebo の差動駆動プラグインが出す `odom → base_footprint` と、URDF から出す固定変換を組み合わせて、地図上で LiDAR の測定点を扱える。LiDAR が配信する `header.frame_id` は TF にあるセンサー名に合わせる。別のロボットでは、URDF の構成に応じて `base_link` を `odom` の子にすることもできる。[Nav2 Jazzy の TF 設定ガイド](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/transformation/setup_transforms/)

`Odometry` の `header.frame_id` は位置・向きの基準、`child_frame_id` は速度の基準を表す。Waffle ではそれぞれ `odom`、`base_footprint`。メッセージを配信する処理と TF を配信する処理は別で、両方を用意する。[ROS 2 Jazzy の Odometry メッセージ定義](https://docs.ros.org/en/jazzy/p/nav_msgs/msg/Odometry.html)

## 速度指令を車輪に伝える

例えば、前進するときは左右の車輪を同じ速度で回し、曲がるときは左右に速度差をつける。実機では、エンコーダーで測った速度と目標速度の差を使ってモーター出力を調整する。これが閉ループ制御。

独自実装では、速度指令の受信、モーター制御、エンコーダーの読み取り、オドメトリと TF の配信を用意する。`ros2_control` を使う場合は、`diff_drive_controller` が車体の速度指令を左右の車輪の速度指令へ変換し、車輪のフィードバックからオドメトリを推定する。実機との通信とモーターの速度追従は、機器に応じてドライバーやモーターコントローラなどで用意する。`diff_drive_controller` を導入するだけで、モーターの PID 制御まで設定されるわけではない。[ros2_control Jazzy の差動駆動コントローラ](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)

車輪オドメトリと IMU の両方があれば、`robot_localization` の EKF で融合して `/odometry/filtered` を配信できる。EKF が車体への TF を配信する構成では、駆動側の同じ TF の配信を無効にする。例えば `diff_drive_controller` なら `enable_odom_tf: false` を指定する。Nav2 側のオドメトリ入力も使うトピック名とそろえる。[Nav2 Jazzy のセンサー融合設定](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/)

迷路の Waffle では、Gazebo の差動駆動プラグインと ROS–Gazebo ブリッジがこの役割を担う。講義の `my_robot.urdf` は車体とセンサーの取り付け位置を定義する段階で、駆動・センサーのデータは別途用意する。[前回の URDF と TF](22-custom-robot-urdf-tf.md)

迷路ワールドで Waffle を起動し、`/odom` の親が `odom`、子が `base_footprint` であること、`/scan` のフレームが `base_scan` であること、`/cmd_vel` の購読型が `TwistStamped` であることを確認した。
