# 01. Nav2 学習環境の準備

確認日: 2026-11-09

## 講座の説明を日本語で理解する

このセクションの目的は、次のセクションから Nav2 を使い始められるよう、ROS 2、Nav2 と補助ツールを準備すること。講師は **Ubuntu 22.04 + ROS 2 Humble** を前提にしており、同じ結果を得たい受講者にはその組み合わせを勧めている。ネイティブインストールを推奨し、仮想マシンの描画性能には注意を促している。

文字起こしの「Rust two」「roster」は **ROS 2**、「handle」は **Humble**、「Ubuntu 22.4」は **Ubuntu 22.04** と読む。

## このリポジトリで使う環境

| 項目 | 講座の前提 | 現在の PC（確認済み） |
| --- | --- | --- |
| OS | Ubuntu 22.04 | Ubuntu 24.04.4 LTS (x86_64) |
| ROS 2 | Humble | Jazzy |
| Gazebo | 講座の各手順で確認 | Gazebo Harmonic (`gz sim` 8.10.0) |
| Nav2 | インストール対象 | `navigation2`、`nav2_bringup` インストール・設定済み |
| SLAM | 後続セクションで使用 | `slam_toolbox` インストール済み |
| 可視化・連携 | 後続セクションで使用 | RViz 2、`ros_gz` インストール・設定済み |

**方針:** この PC に入っている Jazzy 環境で進める。Humble の講座を概念の学習に使い、コマンド・パッケージ名・Gazebo の操作は Jazzy 用の公式資料で照合してから実行する。講座と同一の動作が必要になった場合は、Ubuntu 22.04 + Humble の別環境を用意する。

Jazzy は Ubuntu 24.04 を主要対象とする LTS で、[Nav2 の Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)は Gazebo の新しい系統を使用する。[Gazebo の互換表](https://gazebosim.org/docs/harmonic/ros_installation/)では Jazzy と Harmonic が推奨の組み合わせ。講座中に Gazebo Classic のコマンドやプラグインが出た場合、名前だけを置き換えず、対応する Jazzy/Harmonic の手順を調べる。

## 次に確認すること

1. `source /opt/ros/jazzy/setup.bash` で環境を読み込む。
2. `printenv ROS_DISTRO` が `jazzy` と表示されることを確認する。
3. [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)に沿って、TurtleBot のシミュレーションを起動する。
4. RViz で初期位置と目標地点を指定し、移動を確認する。
5. 起動コマンド、見えたトピック、発生したエラーをこのフォルダに記録する。

Nav2・SLAM Toolbox・Gazebo 連携は導入済み。ソースからビルドする段階では、`rosdep` が利用できるか改めて確認する。

## Nav2 パッケージの講義との対応

講義の `ros-humble-navigation2` と `ros-humble-nav2-bringup` は、ここでは `ros-jazzy-navigation2` と `ros-jazzy-nav2-bringup` に対応する。Jazzy のシミュレーションには、[Nav2 公式 Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)が案内する `ros-jazzy-nav2-minimal-tb3-sim` を使用する。講義の `ros-humble-turtlebot3*` をそのまま実行する必要はない。

対象パッケージのファイルと `tb3_simulation_launch.py` は存在し、起動引数の読み込みも成功した。2026-11-09 にユーザーが `sudo dpkg --configure -a` を実行後、`navigation2`、`nav2_bringup`、`nav2_minimal_tb3_sim`、`ros_gz`、`turtlebot3_gazebo` がすべて `ii`（インストール・設定済み）になったことを確認した。システム全体でも `dpkg-query` の集計は 2602 パッケージが `ii`、未設定のパッケージは 0 件。

## 参照資料

- [ROS 2 Jazzy リリース案内](https://discourse.ros.org/t/ros-2-jazzy-jalisco-released/37862)
- [Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)
- [Nav2 の Gazebo セットアップガイド](https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/gazebo/)
- [Gazebo と ROS 2 の対応・インストール](https://gazebosim.org/docs/harmonic/ros_installation/)
