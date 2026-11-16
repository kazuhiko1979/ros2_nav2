# 13. Nav2 のパラメータを観察・変更する

確認日: 2026-11-13

## このレッスンでしていること

Nav2 が障害物からどのくらい距離を取るか、周囲の地図を何回更新するか、目的地にどこまで近づけば到着とみなすかを調べる。講座の数値は Humble の例。このフォルダでは **ROS 2 Jazzy / TurtleBot3 Waffle** の [設定ファイル](../config/waffle_nav2.yaml) を基準にする。

| 項目 | このフォルダの設定 | 意味 |
| --- | --- | --- |
| グローバル `inflation_layer.inflation_radius` | `0.5 m` | 壁・障害物からコストを広げる距離 |
| ローカル `inflation_layer.inflation_radius` | `0.5 m` | 近くの障害物からコストを広げる距離 |
| 両コストマップの `robot_radius` | `0.15 m` | 衝突判定に使うロボット半径 |
| 両コストマップの `resolution` | `0.05 m/セル` | 1 マスが 5 cm |
| グローバルの更新／公開 | `1 Hz`／`1 Hz` | 内部更新と ROS トピック配信の周期 |
| ローカルの更新／公開 | `5 Hz`／`2 Hz` | 内部更新と ROS トピック配信の周期 |
| `controller_frequency` | `10 Hz` | 走行速度を計算する目標周期 |
| `goal_checker.xy_goal_tolerance` | `0.25 m` | 到着とみなす位置の許容差 |
| `goal_checker.yaw_goal_tolerance` | `0.25 rad` | 到着とみなす向きの許容差（約 14°） |

`inflation_radius` は範囲内すべてを通行禁止にする値ではない。障害物から離れるほどコストが下がる領域の広さを決める。小さくすると狭い通路にも経路が出やすくなるが、障害物に近づきやすい。**`robot_radius` は講座の 0.22 m に合わせて変更しない。** 衝突判定の形を変えてしまうため、実機・モデル寸法と整合させる必要がある。

`publish_frequency` はコストマップを RViz などに送る頻度、`update_frequency` は内部で再計算する頻度。経路を作り直す頻度ともコントローラーの速度計算頻度とも別。`controller_frequency` の 10 Hz も、負荷の高い WSL 上で常に実測 10 Hz という保証ではない。

## 画面で確認する

[World ナビゲーション手順](08-navigation-world.md)で Gazebo と Nav2 を起動し、RViz で **2D Pose Estimate** を指定する。別のターミナルで次を実行する。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
rqt
```

講座の **Plugins → Configuration → Dynamic Reconfigure** で使う `ros-jazzy-rqt-reconfigure` は導入済み。2026-11-13 に `dpkg-query` と `ros2 pkg executables rqt_reconfigure` で確認した。`rqt` のメニューに見当たらない場合は、`rqt` を開き直す。プラグインだけを起動する場合は次を実行する。

```bash
ros2 run rqt_reconfigure rqt_reconfigure
```

`global_costmap/global_costmap` または `local_costmap/local_costmap` を選び、`inflation_layer` を開く。RViz で **Global Costmap** と **Local Costmap** をそれぞれ表示し、値を変えたときのコスト領域を見る。走行中の急な変更を避け、ロボットを停止して実験する。

## コマンドでの確認・一時変更

Nav2 起動中なら `rqt` プラグインがなくても ROS 2 標準コマンドで試せる。まず現在値を読む。

```bash
ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius
ros2 param get /local_costmap/local_costmap inflation_layer.inflation_radius
ros2 param get /controller_server controller_frequency
ros2 param get /controller_server goal_checker.xy_goal_tolerance
```

例としてグローバルのみ `0.5` → `0.35 m` にし、RViz の変化を観察したら元に戻す。

```bash
ros2 param set /global_costmap/global_costmap inflation_layer.inflation_radius 0.35
ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius
ros2 param set /global_costmap/global_costmap inflation_layer.inflation_radius 0.5
```

ローカルも比較したいときは、`/local_costmap/local_costmap` に対して同じ操作をする。`ros2 param set` が拒否された場合はエラーを確認し、必要なら設定ファイルで変更して Nav2 を再起動する。実行時の一時変更は設定ファイルへ保存されない。継続したい値だけ [このフォルダの設定ファイル](../config/waffle_nav2.yaml) に反映して再起動する。

到着判定は `goal_checker.xy_goal_tolerance` と `goal_checker.yaw_goal_tolerance` を確認する。`FollowPath.xy_goal_tolerance: 0.05` は DWB コントローラー内の別設定なので、到着判定の `0.25 m` と混同しない。

## 確認範囲

設定ファイルの値、`rqt` の実行ファイル、`ros-jazzy-rqt-reconfigure` の導入状態、ROS 2 からの実行可能ファイルを確認した。GUI 画面表示と、Nav2 を動かしてのパラメータ一時変更・RViz の見た目の変化は、今回まだ実測していない。

## 参照

- [Nav2 Jazzy Inflation Layer](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/costmap_2d/costmap_plugins/inflation/)
- [Nav2 Jazzy Controller Server](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/controller_server/)
- [Nav2 Jazzy Costmap 2D](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/costmap_2d/)
- [ROS Index: rqt_reconfigure](https://index.ros.org/p/rqt_reconfigure/)
