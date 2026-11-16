# 05. 保存した地図の中身

確認日: 2026-11-10

## 2つのファイルの役割

このフォルダには `maps/my_map.pgm` と `maps/my_map.yaml` がある。`.pgm` は地図の画素データ、`.yaml` は画像の場所と地図としての解釈方法を記録する。YAML の `image: my_map.pgm` は YAML ファイルから見た相対パスなので、2つのファイルは一緒に保管する。

`my_map.pgm` は **P5 形式のバイナリ画像**。画像ビューアでは見られるが、テキストエディタで開くと読めない文字が並ぶ。

## この地図の実測値

| 項目 | 値 | 意味 |
| --- | --- | --- |
| 画像サイズ | 156 × 154 セル | 横156、縦154の格子 |
| `resolution` | 0.050 m/セル | 1セルが5 cm四方 |
| 地図全体の範囲 | 7.8 × 7.7 m | 画像サイズ × 解像度。未観測領域も含む |
| `origin` | `[-4.034, -2.887, 0]` | 地図座標系での左下の位置 x・y と回転角 yaw |
| `mode` | `trinary` | 空き・占有・不明の3値として読み込む |
| `negate` | `0` | 黒を占有、白を空きとして解釈する |
| `occupied_thresh` | `0.65` | 占有と判定するしきい値 |
| `free_thresh` | `0.196` | 空きと判定するしきい値 |

回転角が0なので、地図の座標範囲はおよそ x = -4.034〜3.766 m、y = -2.887〜4.813 m。`resolution` は**地図の格子幅**であり、ロボットの自己位置推定精度そのものではない。

この PGM の画素は3値だけで、黒 `0` が566セル（2.4%）、灰 `205` が15,417セル（64.2%）、白 `254` が8,041セル（33.5%）。灰は未観測を表し、壁の外側などにも広く残る。灰の割合だけでは地図の良し悪しは判断できない。

## 講義との読み替え

講義の「GM」は **PGM**、「Gerrit」はテキストエディタの **gedit**、「gray is a known」は **unknown（未観測）** の文字起こしと考えられる。講義例の 124×116セルや `free_thresh` 0.25 は、この地図の値ではない。

`occupied_thresh` と `free_thresh` は、画像の濃淡を読み込むときの判定しきい値。`trinary` モードでは、しきい値の間は不明として扱う。`negate: 1` は画像ファイルを書き換えるのではなく、読み込み時に白黒の意味を逆転させる。保存された `.pgm` は3値なので、画素ごとの細かな確率を保持しているわけではない。

Nav2 に渡すときは画像ではなく `maps/my_map.yaml` を指定し、YAML から対応する PGM を読み込ませる。

## 参照

- [Nav2 Map Server](https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_map_server/README.md)
- [Nav2 の地図モードとしきい値](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/general_tutorials/navigation2_with_keepout_filter/navigation2_with_keepout_filter.md)
