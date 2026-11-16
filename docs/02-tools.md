# 02. 学習で使う補助ツール

確認日: 2026-11-09

## 講義の要点

文字起こしの「Qualcomm」「cons of Qualcomm」は、ROS 2 のビルドツール **colcon** を指す。講義では `python3-colcon-common-extensions`、Git、Terminator を Ubuntu に導入し、エディタとして Visual Studio Code を紹介している。VS Code と拡張機能は講師が使用する選択肢であり、ROS 2 のビルド自体には必須ではない。

## この PC で確認した状態

| ツール | 状態 | この学習での用途 |
| --- | --- | --- |
| `python3-colcon-common-extensions` | `ii`（設定済み） | `src/` 内の ROS 2 パッケージをビルドする |
| Git | `ii`（設定済み） | 教材などのリポジトリを取得する |
| Terminator | `ii`（設定済み） | 複数のターミナルを並べて使う。任意 |
| VS Code | `code` コマンドあり（VS Code Remote CLI） | コード編集。任意 |
| `twxs.cmake` | VS Code Server 側にあり | 講師が紹介した CMake の記述支援。任意 |
| `ms-iot.vscode-ros` | VS Code Server 側では未確認 | 講師が紹介した ROS 拡張。任意 |
| `nonanonno.vscode-ros2` | VS Code Server 側にあり | 既存の ROS 2 拡張 |

必須ツールの追加インストールは不要。VS Code の拡張機能は、実際にコードを書く段階で必要な機能を確認してから選ぶ。講師の環境と完全に揃える必要がある場合は、[Microsoft の ROS 拡張](https://marketplace.visualstudio.com/items?itemName=ms-iot.vscode-ros)を追加できる。講義のもう一つの拡張は [CMake (`twxs.cmake`)](https://marketplace.visualstudio.com/items?itemName=twxs.cmake) で、既に入っている。

このフォルダのビルド手順は [README](../README.md) に記載した。[ROS 2 の colcon チュートリアル](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html)も参照する。
