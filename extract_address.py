#!/usr/bin/env python3

import csv, os, re, sys

def extract_store_info(html_content):
    """
    HTMLコンテンツから店舗名と住所を抽出します。
    """
    store_info = []

    # 店舗名を抽出する正規表現
    # <h3 class="result-item-head__ttl">店舗名</h3> の形式を想定
    names = re.findall(r'<h3 class="result-item-head__ttl">(.*?)</h3>', html_content)

    # 住所を抽出する正規表現
    # <p class="result-item-cts-desc__area" style="word-break:break-all;">住所<span> &nbsp; </span> の形式を想定
    # 余分な<span>タグとその中身、およびその後の<br />タグと駅情報は削除します。
    addresses = re.findall(r'<p class="result-item-cts-desc__area" style="word-break:break-all;">(.*?)(?:<span> &nbsp; </span>\s*<br />\s*.*?)?</p>', html_content, re.DOTALL)

    # 抽出された店舗名と住所を組み合わせます
    # マッチしないケースを考慮して、短い方のリストの長さに合わせます
    for i in range(min(len(names), len(addresses))):
        # 住所から余分な改行やスペースを削除し、駅情報を除く
        cleaned_address = addresses[i].strip()
        # "土崎駅" や "秋田駅 / 秋田駅" のような駅情報が残っている場合は取り除く
        cleaned_address = re.sub(r'\s*<br />\s*.*駅(?:.*?)*$', '', cleaned_address)
        # 最後に残る可能性のある余分な空白を除去
        cleaned_address = cleaned_address.strip()
        
        store_info.append([names[i].strip(), cleaned_address])
    
    return store_info

def create_csv_file(data, filename):
    """
    抽出したデータをCSVファイルに書き込みます。
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        #csv_writer.writerow(['店舗名', '住所']) # ヘッダー行
        csv_writer.writerows(data)
    print(f"CSVファイル '{filename}' が正常に作成されました。")

def read_file_as_single_string(filepath):
    """
    テキストファイルの内容を一つの文字列として読み込みます。

    Args:
        filepath (str): 読み込むファイルのパス

    Returns:
        str: ファイルの内容を格納した文字列。
             ファイルが見つからない場合はNoneを返します。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        return file_content
    except FileNotFoundError:
        print(f"エラー: ファイル '{filepath}' が見つかりません。")
        return None
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        return None

def list_filepath_in_directory(directory):
    """
    指定されたディレクトリ内のファイルパスのリストを返します。

    Args:
        directory (str): ファイルパスを取得したいディレクトリ。

    Returns:
        list: ディレクトリ内のファイルパスのリスト。
              ディレクトリが存在しない場合は空のリストを返します。
    """
    if not os.path.isdir(directory):
        print(f"エラー: ディレクトリ '{directory}' が存在しないか、ディレクトリではありません。")
        return []

    files = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return sorted(files)
    
def extract_address(directory):
    ret = []
    for filepath in list_filepath_in_directory(directory):
        print(filepath)
        html_content = read_file_as_single_string(filepath)
        extracted_data = extract_store_info(html_content)
        ret.extend(extracted_data)
        
    if ret:
        create_csv_file(ret, 'stores.csv')
    else:
        print("抽出できる店舗情報が見つかりませんでした。")
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        directory = sys.argv[1]
        extract_address(directory)
    else:
        usage = '[SAMPLE] ./extract_address.py input/由利本荘市_スーパーマーケット'
        print(usage)
