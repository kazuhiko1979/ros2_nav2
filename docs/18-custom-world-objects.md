# 18. カスタムワールドへ物体を置く

確認日: 2026-11-16

## 講座の内容と Harmonic での操作

講座の `gazebo`、左側の **Insert**、**File → Save World As** は Gazebo Classic の画面。Gazebo Harmonic では `gz sim` を使う。GUI のプラグイン一覧から **Resource Spawner** を開くと、Fuel のモデルを検索・ダウンロードして配置できる。基本的な箱などは画面上部の形状ボタンから置ける。選択した物体は **T** で移動、**R** で回転できる。ファイルメニューからワールドの保存も可能。

Gazebo Harmonic の SDF ワールドは `.sdf` でも `.world` でも XML の SDF 形式。拡張子より中身と起動コマンドを確認する。Fuel のモデルはネットワークやモデルの配布状態に左右されるため、このフォルダでは**最初から SDF に入れた簡単な物体**を使い、同じ配置で再起動できるようにした。

## 今回追加した物体

[生成スクリプト](../scripts/generate_dogtrot_world.py)は家具なしの `dogtrot_floorplan.sdf` と、家具付きの [dogtrot_furnished.sdf](../worlds/dogtrot_furnished.sdf) を両方生成する。家具付き版には次の6点を追加した。座標はワールドの中央通路付近を `(0, 0)` としたメートル単位。

| モデル名 | 場所 | 座標 (x, y) |
| --- | --- | --- |
| `bookshelf_left_shed` | 左上の部屋 | `(-5.7, 4.4)` |
| `bookshelf_right_shed` | 右上の部屋 | `(5.7, 4.4)` |
| `low_table_left_primary` | 左下の部屋 | `(-4.4, -0.3)` |
| `crate_left_primary` | 左下の部屋 | `(-5.4, -1.7)` |
| `crate_right_primary` | 右下の部屋 | `(4.9, -1.2)` |
| `pallet_porch` | 手前のポーチ | `(3.0, -4.1)` |

いずれも**静的な箱形の試作**で、見た目と当たり判定を同じ寸法にした。棚の段板やテーブルの脚までは再現していない。扉と中央通路をふさがない位置に置いた。低い物体は LiDAR の高さ・視野によって検出しにくいことがあるので、後のナビゲーション実習では RViz のレーザー表示とコストマップで確認する。

## 再生成と起動

```bash
cd /home/kazuh/project/workspaces/ros2_nav2
source ./setup.bash
python3 scripts/generate_dogtrot_world.py
gz sdf -k worlds/dogtrot_furnished.sdf
ros2 launch launch/dogtrot_world.launch.py
```

既定の起動ファイルは**家具付き版**を選ぶ。家具なしと比べたいときは次を使う。

```bash
ros2 launch launch/dogtrot_world.launch.py world_file:=$PWD/worlds/dogtrot_floorplan.sdf
```

位置や寸法を変えるときは、生成スクリプトの `FURNITURE` を編集して再生成する。GUI で試し置きした物体を永続化したい場合は、ワールドを別名で保存するか、その配置をスクリプトへ反映する。**Waffle を配置したまま GUI で保存するとロボットまでワールドに含まれる可能性がある**ため、そのファイルをこの起動ファイルで再度使う前にモデル一覧を確認する。

## 確認結果

- 家具なし・家具付きの両 SDF は `gz sdf -k` で `Valid.`。
- 家具付きワールドを起動し、Gazebo のモデル一覧で床、壁、家具6点、Waffle を確認した。
- Waffle の生成成功と `/scan` の `frame_id: base_scan` を確認した。短時間の最初の受信確認では `/scan` がまだ見えなかったが、起動待ちを延ばすと受信できた。
- GUI 上での家具の見た目、手動での移動・保存、実際の走行・SLAM は未確認。

## 参照

- [Gazebo Harmonic: Model Insertion from Fuel](https://gazebosim.org/docs/harmonic/fuel_insert/)
- [Gazebo Harmonic: Manipulating Models](https://gazebosim.org/docs/harmonic/manipulating_models/)
- [Gazebo Harmonic: Understanding the GUI](https://gazebosim.org/docs/harmonic/gui/)
- [Gazebo Harmonic: SDF worlds](https://gazebosim.org/docs/harmonic/sdf_worlds/)
