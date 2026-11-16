# 09. ウェイポイント追従

確認日: 2026-11-11

## 何をする機能か

複数の通過地点と、その地点での向きを順序付きで指定する。TurtleBot3 World の起動、地図読み込み、AMCL の初期位置指定は [08. 保存済み地図でナビゲーション](08-navigation-world.md) と同じ。

| RViz の実行ボタン | ROS 2 アクション | 動き方 |
| --- | --- | --- |
| Start Waypoint Following | `/follow_waypoints` | 各地点へ `NavigateToPose` を順番に実行。地点でタスクを実行できる。 |
| Start Nav Through Poses | `/navigate_through_poses` | 複数地点を1つの経路として計画し、連続して通過することを目指す。 |

講座の「2つ目は不安定」は動画内での観察であり、Nav2 全体に常に当てはまる性質ではない。地図、目標の位置、自己位置推定、動作ツリー設定で結果が変わる。

## RViz での操作

1. **2D Pose Estimate** で現在位置を指定する。
2. 左側の **Navigation 2** パネルで **Waypoint / Nav Through Poses Mode** に切り替える。
3. 上部の **Nav2 Goal** ツールで白い走行可能領域に順番に地点を置き、ドラッグで向きを決める。地図上に番号付きの矢印が表示される。
4. **Start Waypoint Following** または **Start Nav Through Poses** を押す。地点の登録をやめる場合は **Cancel Accumulation**。

最初は近い2～3地点で試し、結果と未到達地点を確認する。この PC の Waffle 設定では `waypoint_pause_duration: 200` なので Waypoint Following は到着地点で約 0.2 秒待つ。また `stop_on_failure: false` なので、途中の地点に失敗しても次を試す設定。アクション全体の成功表示だけで各地点に到達したと判断せず、`missed_waypoints` も確認する。

## この PC で見つけた設定の問題と修正

インストール済みの `/opt/ros/jazzy/share/turtlebot3_navigation2/param/waffle.yaml` では、`default_nav_through_poses_bt_xml` が誤って単一目標用の `navigate_to_pose_w_replanning_and_recovery.xml` を指していた。実際に2地点の `/navigate_through_poses` 目標を送ると、`compute_path_to_pose` が空のフレームを `map` に変換できず、`TF_ERROR (202)` で `ABORTED` になった。

このフォルダの [修正版 Waffle 設定](../config/waffle_nav2.yaml) は、インストール済み設定をコピーし、`default_nav_through_poses_bt_xml` を `navigate_through_poses_w_replanning_and_recovery.xml` に直したもの。後続の障害物実習では、消去用に `inf_is_valid` も追加した。`/opt/ros` は編集していない。起動時に次のように指定する。

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True map:="$PWD/maps/my_map.yaml" \
  params_file:="$PWD/config/waffle_nav2.yaml"
```

修正版を読み込んだ際、`/bt_navigator` のパラメータは正しい XML を指し、経路計画時の空フレームのエラーは消えた。連続通過目標でロボットが移動することも確認した。

## 動作確認

- `/follow_waypoints` に `(-1.7, -0.5)`、`(-1.4, -0.5)` を送った結果、`SUCCEEDED`、`missed_waypoints: []`。ログには各地点で 200 ms の待機が記録された。
- 未修正の `/navigate_through_poses` は `TF_ERROR (202)` で `ABORTED`。
- 修正後の `/navigate_through_poses` は経路計画と走行が始まった。WSL 上では実時間に対してシミュレーションが遅く、60 秒の観測時間内に完了結果は得られなかった。

## 参照

- [Nav2 Jazzy Waypoint Follower](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/waypoint_follower/)
- [Nav2 Jazzy の動作ツリー](https://docs.nav2.org/jazzy/getting_started/nav2_behavior_trees/)
