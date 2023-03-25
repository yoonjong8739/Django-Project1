import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import Series
import time


def link(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    selector ='#content > div.com_srch > div.bs > ul > li > a > img'
    try:
        element = soup.select(selector)[0]
    except:
        print('수집못함',url)
        return False

    val = element.get('src')
    val = val.replace('m79', 'm260')

    return val


def csv_col_add():
    df = pd.read_csv('../outfile/naver_series_1_novel_page_1-226.csv', sep=',',
                     names=[1, 2, 3, 4, 5, 6], header=None, encoding='utf-8-sig')
    df['소설'] = '소설'
    df2 = df[[1, '소설', 2, 3, 4, 5, 6]]

    df2.to_csv('../outfile/naver_series_1_novel_page_1-226_edit1.csv', encoding='utf-8-sig', index=False)


def one_loop(input_list, range_tuple, target):
    img_src = []

    for item in input_list[range_tuple[0]:range_tuple[1]]:
        val = link(target + item)
        if not val:
            continue
        img_src.append((item, val))

    print('first loop finished :', range_tuple, img_src)
    df2 = pd.DataFrame(img_src, columns=[['2', 'url']])
    df2.to_csv(f'../outfile/novel_url-{range_tuple[0]}-{range_tuple[1]}.csv', encoding='utf-8-sig', index=False)

def main():
    target = 'https://series.naver.com/search/search.series?t=all&fs=ebook&q='
    my_list = []

    df = pd.read_csv('../outfile/naver_series_1_novel_page_1-226_edit1.csv')
    tmp = df["2"]


    title_list = list(tmp)

    a= 0


    # img_src = []
    #
    # for item in title_list[0:100]:
    #     val = link(target + item)
    #     img_src.append((item, val))
    #
    # df2 = pd.DataFrame(img_src, columns=[['2', 'url']])
    # df2.to_csv('../outfile/novel_url-100.csv', encoding='utf-8-sig', index=False)
    one_loop(title_list, (0, 500), target)
    one_loop(title_list, (500, 1000), target)
    one_loop(title_list, (1000, 1500), target)
    one_loop(title_list, (1500, 2000), target)
    one_loop(title_list, (2000, 2618), target)


def concat_details():
    df1 = pd.read_csv('../outfile/naver_series_1_novel_page_1-226_edit1.csv', encoding='utf-8-sig')
    df2 = pd.read_csv('../outfile/novel_url-0-2619.csv', encoding='utf-8-sig')
    df3 = pd.merge(left=df1, right=df2, how="outer", on="2")
    df3.to_csv('../outfile/naver_series_1_novel_page_1-226_edit2.csv', encoding='utf-8-sig', index=False)

    a = 0


if __name__ == '__main__':
    pass
    # csv_col_add()
    # main()
    # concat_details()