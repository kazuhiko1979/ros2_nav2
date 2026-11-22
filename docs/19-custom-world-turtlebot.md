# 19. カスタムワールドで TurtleBot3 を動かす

確認日: 2026-11-16

## 講座からの読み替え

講座では ROS 2 Humble / Gazebo Classic の `turtlebot3_simulations` を複製し、`turtlebot3_gazebo` を overlay で上書きしてワールドを追加する。このフォルダはすでに ROS 2 Jazzy のワークスペースで、[カスタム起動ファイル](../launch/dogtrot_world.launch.py)が**インストール済みの TurtleBot3 Gazebo パッケージを利用して**家具付きワールドと Waffle を起動できる。

学習用の overlay は `src/ros2_nav2_custom_world` という**別名の ROS 2 パッケージ**にした。`turtlebot3_gazebo` 本体は `/opt/ros/jazzy` のまま使い、独自の launch と SDF をこのパッケージから呼び出す。元のパッケージを編集する必要はない。

```text
underlay  /opt/ros/jazzy                 turtlebot3_gazebo, ros_gz_sim, Nav2 など
overlay   このフォルダの install/          ros2_nav2_custom_world
source    このフォルダの src/ と launch/・worlds/
```

overlay は先に読み込んだ underlay の上に追加する作業領域。`ros2 pkg prefix turtlebot3_gazebo` は `/opt/ros/jazzy`、`ros2 pkg prefix ros2_nav2_custom_world` はこのフォルダの `install/ros2_nav2_custom_world` を返す。将来 upstream の `turtlebot3_gazebo` 自体を変更するときだけ、[ROBOTIS の Jazzy ブランチ](https://github.com/ROBOTIS-GIT/turtlebot3_simulations/tree/jazzy)を別途取り込む。講座の `humble-devel` はこの環境では使わない。

## ビルド

ビルド用の新しいターミナルでは、まず underlay のみ読み込んでビルドする。この PC では通常の Python 探索が `~/.local/bin/python3.12` を選んで `catkin_pkg` を見つけられなかったため、`/usr/bin/python3` を明示する。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src --packages-select ros2_nav2_custom_world --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
```

実行には**別の新しいターミナル**でこのフォルダの設定を読み込む。`setup.bash` は Jazzy の underlay と、ビルド済みの `install/local_setup.bash` を順番に読み込む。システム全体の `.bashrc` は変更しない。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 pkg prefix ros2_nav2_custom_world
ros2 pkg prefix turtlebot3_gazebo
```

## Gazebo と Waffle を起動する

ターミナル1:

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch ros2_nav2_custom_world dogtrot_world.launch.py
```

Waffle は中央通路の `(x=0, y=0)` に生成される。既定のワールドは家具付きの `dogtrot_furnished.sdf`。講座の `x_pose`・`y_pose` に相当する引数は、[起動ファイル](../launch/dogtrot_world.launch.py)で既定値 `0.0` として宣言し、TurtleBot3 の生成用 launch に渡している。

別の空き場所から始めたいときは、起動時に座標を指定する。例えば、このワールドのポーチ寄りの場所なら次のようにする。`x` はワールド原点から左右、`y` は前後の位置で、単位はメートル。講座の `(-1, -5)` は講座側のワールドの値なので、こちらでは障害物のない場所を選ぶ。

```bash
ros2 launch ros2_nav2_custom_world dogtrot_world.launch.py x_pose:=-1.0 y_pose:=-4.0
```

座標の変更は launch 引数だけで行えるため、再ビルドは不要。起動ファイルやワールド本体を編集した場合は、ビルド手順を実行してから新しいターミナルで試す。終了は起動したターミナルで **Ctrl+C**。

ターミナル2ではキーボード操作を試す。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 run turtlebot3_teleop teleop_keyboard
```

操作は **w/x** で前後の速度を増減、**a/d** で旋回、**s** またはスペースで停止。キー入力は teleop のターミナルを選択して行う。障害物と壁があるので、最初は低速で短く動かす。Jazzy のこの teleop は `geometry_msgs/msg/TwistStamped` を `/cmd_vel` に送り、Waffle の Gazebo ブリッジも同じ型を受け取る。

動作確認には別のターミナルで `ros2 topic echo /odom` や `ros2 topic echo /scan` を使える。LiDAR が `base_scan` で動作していること、オドメトリの位置が変わることを確かめる。次の地図作成では、この**カスタムワールド専用の地図**を SLAM で新たに保存する。World / House 用の既存地図は流用しない。

## 実測結果

- `colcon build` は `ros2_nav2_custom_world` 1パッケージを正常にビルドした。
- パッケージ名から launch を解決し、Gazebo 内で Waffle の `Entity creation successful` を確認した。
- 別の短時間試験で `/cmd_vel` に低速の `TwistStamped` を3秒間送り、`/odom` の位置が **0.053 m** 変化した。停止指令も送った。WSL 上のシミュレーション時間は壁時計と一致しないため、距離を速度×3秒とは比較しない。
- キーボードを人手で押したときの画面上の軌跡と、カスタムワールドの SLAM 地図作成は未確認。

## 参照

- [ROS 2 Jazzy: Creating a Workspace](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html)
- [ROBOTIS TurtleBot3 simulations: Jazzy branch](https://github.com/ROBOTIS-GIT/turtlebot3_simulations/tree/jazzy)
