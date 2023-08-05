# 文字列セットの比較処理
- 特定の文字列セット2種類を比較し、頻出単語の傾向を比較する為のプログラムです。

# 環境構築
## 事前準備
### MeCabのインストール
- MeCabを使用する為、ホストマシンに事前にインストール
```
$ brew install mecab
$ brew install mecab-ipadic
```

### ライブラリインストール
- venvなど仮想環境を使用するのを推奨
```
$ pip3 install -r requirements.txt
```

### 辞書情報のインストール
- 日本語の辞書として `neologd` を使用します
- 直下で下記コマンドを実行してインストール
```
git clone https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd
./bin/install-mecab-ipadic-neologd -n
```

# 使い方
- `data` フォルダに演算対象とするCSVファイルを格納後、後述するコマンドを叩いて使用します
- 演算した結果は `output` フォルダに出力されます

## 実行コマンド
```sh
$ python3 main.py [options]
```

## オプション一覧
| オプション | 内容 |
| ---- | ---- |
| --file-base (-fb) | 基準とするCSVファイル |
| --file-compare (-fc) | 比較対象とするCSVファイル |
| --column-name (-c) | CSVの読み込み対象とするカラム名 |
| --output (-o) | 出力ファイル名 |
| --output-csv | 形態素解析および比率を割り出したCSVファイルを出力 |

## 参考
- https://biosciencedbc.jp/blog/20181220-01.html