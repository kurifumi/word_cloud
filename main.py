import csv
import re
import argparse
import MeCab
import unicodedata
import wordcloud as wc
import matplotlib.pyplot as plt
from multiprocess import Pool

WORDCLOUD_FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
THRESHOLD_COUNT = 20

# Mecab
mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
mecab.parse("")


def read_csv(file_name: str, target_column: str = "name") -> [str]:
    base_path = "data/"
    with open(f"{base_path}{file_name}.csv", "r") as f:  # comma-separated
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append(row[target_column])
    return data


def tokenize_text(s: str) -> [str]:
    ########################
    # テキスト前処理
    ########################
    # 表記揺れの吸収
    s = s.lower()
    s = unicodedata.normalize("NFKC", s)
    # 7桁以上数値が連続する場合は識別番号などの特徴の低い情報の可能性が高いので削除
    s = re.sub(r"[0-9]{7,}", "", s)
    # カンマ入りの数値対策
    s = re.sub(r"[,]", "", s)
    s = s.strip()
    node = mecab.parseToNode(s)

    r = []
    while node:
        # 単語を取得
        if node.feature.split(",")[6] == "*":
            word = node.surface
        else:
            word = node.feature.split(",")[6]

        # 品詞を取得
        part = node.feature.split(",")[1]

        if part in ["名詞", "固有名詞"]:
            r.append(word)
        node = node.next
    return r


def tokenize_texts(strs: [str]) -> [str]:
    result = []
    with Pool(8) as pool:
        data = pool.map(tokenize_text, strs)
        for row in data:
            result.extend(row)
    return result


def convert_word_dict(words: [str]) -> object:
    w_dict = {}
    for w in words:
        w_dict[w] = w_dict.get(w, 0) + 1
    return w_dict


def plot_wordcloud(w_dict, title: str = "WordCloud", pngfile: str = None):
    # オブジェクト変換
    wc_obj = wc.WordCloud(
        font_path=WORDCLOUD_FONT_PATH,
        background_color="white",
        min_font_size=12,
        max_font_size=100,
        width=1000,
        height=800,
    ).generate_from_frequencies(w_dict)
    awc = wc_obj.to_array()

    fig = plt.figure()
    left, width = 0.01, 0.98
    bottom, height = 0.01, 0.90
    ax = plt.axes([left, bottom, width, height])

    ax.imshow(awc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title, fontsize=18)

    # png
    if pngfile:
        fig.savefig(f"output/{pngfile}.png")


def make_flags(w_dict1, w_dict2):
    f_dict = {}
    all_words = set(list(w_dict1.keys()) + list(w_dict2.keys()))
    sum1 = sum(w_dict1.values())
    sum2 = sum(w_dict2.values())
    for key in all_words:
        count1 = w_dict1.get(key, 0)
        count2 = w_dict2.get(key, 0)
        # 規定回数以下しか出ていない単語はノイズなので除外
        if count1 < THRESHOLD_COUNT and count2 < THRESHOLD_COUNT:
            continue
        freq1 = count1 / sum1
        freq2 = count2 / sum2
        if key != "":
            f_dict[key] = (freq1 - freq2) / ((freq1 + freq2) * 2)
    return f_dict


def write_csv_by_wdict(w_dict: object, file_name: str) -> None:
    with open(f"output/{file_name}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "score"])
        for k, v in w_dict.items():
            writer.writerow([k, v])


def hoge(w_dict, file_name):
    plot_wordcloud(w_dict, pngfile=file_name)
    write_csv_by_wdict(w_dict, file_name)


if __name__ == "__main__":
    psr = argparse.ArgumentParser()
    psr.add_argument(
        "-fb", "--file-base", required=True, help="比較元ファイル", default="base"
    )
    psr.add_argument("-fc", "--file-compare", required=False, help="比較対象ファイル")
    psr.add_argument(
        "-c", "--column-name", required=False, help="読み込み対象ファイルのカラム名", default="name"
    )
    psr.add_argument("-o", "--output", required=False, help="アウトプットの名前", default="out")
    args = psr.parse_args()
    file_base_name = args.file_base
    file_compare_name = args.file_compare
    file_output_name = args.output

    print("ベースファイル演算開始")
    w_dict1 = convert_word_dict(
        tokenize_texts(read_csv(file_base_name, args.column_name))
    )
    hoge(w_dict1, file_base_name)

    if file_compare_name:
        print("比較ファイル演算開始")
        w_dict2 = convert_word_dict(
            tokenize_texts(read_csv(file_compare_name, args.column_name))
        )
        hoge(w_dict2, file_compare_name)

        f_dict = make_flags(w_dict1, w_dict2)
        hoge(f_dict, file_output_name)
