import csv
import re
import sys
import argparse
import MeCab
import unicodedata
import wordcloud as wc
import matplotlib.pyplot as plt

WORDCLOUD_FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
THRESHOLD_COUNT = 20

def read_csv(file_name: str, target_column: str = 'name') -> [str]:
    base_path = 'data/'
    with open(f'{base_path}{file_name}.csv', 'r') as f: #comma-separated
        reader = csv.DictReader(f)
        data = []
        for row in reader: data.append(row[target_column])
    return data

def hoge(strs: [str]) -> [str]:
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    mecab.parse('')
    results = []
    for s in strs:
        r = []

        ########################
        # テキスト前処理
        ########################
        # 表記揺れの吸収
        s = s.lower()
        s = unicodedata.normalize('NFKC', s)
        # 7桁以上数値が連続する場合は案件番号などの特徴の低い情報の可能性が高いので削除
        s = re.sub(r'[0-9]{7,}', '', s)
        # カンマ入りの数値対策
        s = re.sub(r'[,]', '', s)
        s = s.strip()
        # Mecab
        node = mecab.parseToNode(s)
        while node:
            # 単語を取得
            if node.feature.split(",")[6] == '*':
                word = node.surface
            else:
                word = node.feature.split(",")[6]

            # 品詞を取得
            part = node.feature.split(",")[0]

            if part in ["名詞", "動詞"]:
                r.append(word)
            node = node.next
        results.extend(r)
    return results

def convert_word_dict(words: [str]) -> object:
    w_dict = {}
    for w in words:
        w_dict[w]=w_dict.get(w,0)+1
    return w_dict

def plot_wordcloud(w_dict, title:str = "WordCloud", pngfile:str = None):
    # オブジェクト変換
    wc_obj=wc.WordCloud(
        font_path=WORDCLOUD_FONT_PATH,
        background_color="white",
        min_font_size=12,
        max_font_size=100,
        width=1000,
        height=800
    ).generate_from_frequencies(w_dict)
    awc = wc_obj.to_array()

    fig=plt.figure()
    left, width = 0.01, 0.98
    bottom, height = 0.01, 0.90
    ax=plt.axes([left, bottom, width, height])

    ax.imshow(awc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title,fontsize=18)

    # png
    if pngfile:
        fig.savefig(f"output/{pngfile}.png")

def make_flags(w_dict1,w_dict2):
    f_dict={}
    all_words=set(list(w_dict1.keys())+list(w_dict2.keys()))
    sum1=sum(w_dict1.values())
    sum2=sum(w_dict2.values())
    for key in all_words:
        count1 = w_dict1.get(key, 0)
        count2 = w_dict2.get(key, 0)
        # 規定回数以下しか出ていない単語はノイズなので除外
        if count1 < THRESHOLD_COUNT and count2 < THRESHOLD_COUNT: continue
        freq1 = count1/sum1
        freq2 = count2/sum2
        if key!='':
            f_dict[key]=(freq1-freq2)/((freq1+freq2)*2)
    return f_dict

def write_csv_by_wdict(w_dict: object, file_name: str) -> None:
    with open(f'output/{file_name}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'score'])
        for k, v in w_dict.items():
            writer.writerow([k, v])


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-fb', '--file-base', required=False, help='比較元ファイル', default='base')
    psr.add_argument('-fc', '--file-compare', required=False, help='比較対象ファイル', default='compare')
    psr.add_argument('-c', '--column-name', required=False, help='読み込み対象ファイルのカラム名', default='name')
    psr.add_argument('-o', '--output', required=False, help='アウトプットの名前', default='out')
    psr.add_argument('--output-csv', action='store_true', help='CSVを出力するか')
    args = psr.parse_args()

    file_base_name = args.file_base
    file_compare_name = args.file_compare
    file_output_name = args.output

    print('データ解析処理')
    w_dict1 = convert_word_dict(hoge(read_csv(file_base_name, args.column_name)))
    w_dict2 = convert_word_dict(hoge(read_csv(file_compare_name, args.column_name)))
    f_dict = make_flags(w_dict1, w_dict2)

    print('WordCloud描画処理')
    plot_wordcloud(w_dict1, pngfile=file_base_name)
    plot_wordcloud(w_dict2, pngfile=file_compare_name)
    plot_wordcloud(f_dict, pngfile=file_output_name)

    if args.output_csv:
        print('CSV出力処理')
        write_csv_by_wdict(w_dict1, file_base_name)
        write_csv_by_wdict(w_dict2, file_compare_name)
        write_csv_by_wdict(f_dict, file_output_name)
