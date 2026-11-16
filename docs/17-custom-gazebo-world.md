# 17. 間取り図から Gazebo Harmonic のワールドを作る

確認日: 2026-11-16

## 講座との違い

講座は **Gazebo Classic** の `gazebo` コマンド、`Edit → Building Editor`、間取り画像の **Import** を使う。この機能は現在の **Gazebo Harmonic / Gazebo Sim** にはない。この PC では `gz sim` 8.15.0 が使えるため、SDF で壁・床・扉の開口を記述する方法に読み替える。Gazebo の公式資料も Harmonic では SDF ワールドの作成を案内している。

講座の Building Editor が保存する `model.sdf` と `model.config` は**建物のモデル**のファイル。こちらの試作は、床・壁・光・シミュレーション設定をまとめた**ワールド** `worlds/dogtrot_floorplan.sdf` を作る。役割の違いを押さえる。

## 今回作成した試作

ユーザー提供の `floorplan_example.png` を参考に、左右の各2部屋、中央通路、手前のポーチを持つ間取りを SDF にした。

| 項目 | 今回の扱い |
| --- | --- |
| 縮尺 | 画像中の扉のすき間を約40 px、実寸を講座と同じ **0.90 m** と仮定。約 44.4 px/m |
| 全体 | 外壁の中心線で約 **13.8 m × 11.6 m** |
| 壁 | 20 本の静的な箱。高さ 2.0 m、厚み 0.12 m |
| 扉 | 壁を分割して通れる開口を作成。扉板や開閉機構は未作成 |
| 簡略化 | 空の `dogtrot_floorplan.sdf` では窓・煙突・柱・家具を省略。中央通路の奥とポーチの手前は、初回のナビゲーション実習用に壁で閉じた |
| ロボットの初期位置 | 中央通路の概ね中央、`x=0.0, y=0.0` |

縮尺は**画像からの推定**であり、実測寸法を保証しない。正確な寸法が分かったら [生成スクリプト](../scripts/generate_dogtrot_world.py) の `REFERENCE_DOOR_WIDTH_M` と `WALLS_PX` を更新して再生成する。元の画像ファイルは `/mnt/c/Users/kazuh/Downloads/floorplan_example.png` にあり、このリポジトリには複製していない。

## 生成と起動

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
python3 scripts/generate_dogtrot_world.py
gz sdf -k worlds/dogtrot_floorplan.sdf
```

Gazebo Harmonic と TurtleBot3 Waffle を一緒に起動する。現在は [家具付きワールド](18-custom-world-objects.md)が既定。

```bash
ros2 launch launch/dogtrot_world.launch.py
```

家具なしで起動する場合は、`world_file` を指定する。

```bash
ros2 launch launch/dogtrot_world.launch.py world_file:=$PWD/worlds/dogtrot_floorplan.sdf
```

Gazebo 単体で形だけ見る場合は次を使う。

```bash
gz sim -r worlds/dogtrot_floorplan.sdf
```

初回はロボットの出発位置を `x_pose:=... y_pose:=...` で変えられる。ロボットを走らせる前に、Gazebo の画面で壁・開口・出発位置を目視確認する。現時点では SLAM 地図はまだ作っていないため、既存の `maps/my_map.yaml` や `maps/my_house.yaml` はこのワールドには使わない。

## 確認結果

- `gz sdf -k worlds/dogtrot_floorplan.sdf` は `Valid.` を返した。
- `ros2 launch launch/dogtrot_world.launch.py --show-args` は成功し、`x_pose`、`y_pose`、`use_sim_time` を認識した。
- Gazebo サーバーを作成した SDF で15秒間起動できた。
- カスタム起動ファイルでは Gazebo と `robot_state_publisher` が起動し、TurtleBot3 Waffle の `Entity creation successful` を確認した。
- `/scan` の `frame_id` は `base_scan`、`/odom` の `child_frame_id` は `base_footprint` と確認した。GUI での間取りの目視、走行、SLAM は未確認。

## 参照

- [Gazebo Classic の Building Editor](https://classic.gazebosim.org/tutorials?tut=building_editor)
- [Gazebo Harmonic の機能比較](https://gazebosim.org/docs/harmonic/comparison/)
- [Gazebo Harmonic の SDF ワールド](https://gazebosim.org/docs/harmonic/sdf_worlds/)
