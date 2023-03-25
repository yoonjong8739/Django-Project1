from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.options import Options
import time

from book_trends.review_crawler import ReviewCrawler
from book_trends.twitter_crawler import TwitterCrawler
from crawler import mysecrets
from crawler.base_crawler import BaseCrawler
import pandas as pd
import datetime as dt
from dateutil.tz import gettz
import os
import numpy as np


class BestBooksCrawler:
    def __init__(self, url: str, option: Options):
        self.bookstore_crawler = BaseCrawler(url, option=option)
        self.bookstore_crawler.open_browser()

    def _naver_base_info(self, j, header, base_url, isbn_selector):
        # if j == 19:
        #     a = 5

        # 기본 정보
        rank = header.select("em")[0].text
        title = header.select("strong")[0].text
        writer = header.select("span.writer")[0].text.split(',')[0]
        image = header.select("img")[0]['src']
        sub_link = header.select("a")[0]['href']
        container_selector = 'div#book_section-info > div.bookBasicInfo_basic_info__HCWyr > ul'

        # 책 상세정보페이지 (to get isbn link)
        isbn_link = self.bookstore_crawler.quick_attr_in_link(base_url + sub_link, isbn_selector, 'href')

        # 책 상세 정보가 없는 경우 -> 국립중앙도서관 전자책 ISBN 조회
        if not isbn_link:
            title_tmp = title.replace(' ', '+')
            gov_url = f'https://www.nl.go.kr/seoji/contents/S80100000000.do?page=1&pageUnit=10&schType=simple&schFld=title&schStr={title_tmp}&ebookYn=Y'

            gov_sel = 'div#resultList_div'
            gov_tag = self.bookstore_crawler.quick_tag_in_link(gov_url, gov_sel)

            try:
                # 검색 결과가 없는 경우(ISBN 번호가 부여되지 않은 전자책의 경우)
                isbn_container = gov_tag.find('li', string='제본형태: 전자책').find_parent()
            except AttributeError:
                print(f"rank {rank} : {title} - does not exist in gov-library")
                return None

            gov_isbn_tag = isbn_container.select("li:nth-child(3)")
            tmp = gov_isbn_tag[0]
            isbn_val = tmp.text

            # ISBN: 978-89-378-3637-4 (05830)
            isbn_val = isbn_val.split(' ')[1].replace('-', '')
            print(f'naver {rank}위 {title} 수집 필요')

        else:
            # isbn 추출 (parent select)
            self.bookstore_crawler.new_tab(isbn_link)

            soup = self.bookstore_crawler.get_soup()

            try:
                # 성인인증 페이지인경우 IndexError
                container = soup.select(container_selector)[0]
            except IndexError:
                print(f"rank {rank} : {title} - unable to collect due to rate-18")
                return None

            isbn_container = container.find('div', string='ISBN').find_parent()
            isbn_tag = isbn_container.select("div:nth-child(2)")
            isbn_val = isbn_tag[0].text
            self.bookstore_crawler.to_preveious_tap()

        # isbn, 순위, 사이트, 제목, 작가, 이미지 수집
        return {
            'isbn': isbn_val,
            'rank': rank,
            'website': 'naver',
            'title': title,
            'writer': writer,
            'image': image
        }

    def fetch_naver_best(self):
        target = 'https://series.naver.com/ebook/top100List.series?page='
        wrapper = 'div#content > div.lst_thum_wrap'
        base_url = 'https://series.naver.com'
        isbn_selector = '#content > ul.end_info.NE\=a\:ebi > li:nth-child(2) > span > a'
        page_books = []

        for i in range(1, 6):
            # page_books = []
            self.bookstore_crawler.move_page(target+str(i))
            ori_element = self.bookstore_crawler.select_element(selector=wrapper)[0]
            headers = ori_element.find_all("li", class_=None)

            for j, header in enumerate(headers):
                rst = self._naver_base_info(j, header, base_url, isbn_selector)
                if rst:
                    page_books.append(rst)
                time.sleep(0.5)

        return page_books

    def _millie_base_info(self, j, header):
        # isbn_wrapper = 'div#wrap > section > div > div.book-content > div:nth-child(7) > div.introduction.section > div.book-info-detail.slide-container'
        isbn_wrapper = 'div.book-info-detail.slide-container'
        # 기본 정보
        rank = header.select("div.book_ranking")[0].text
        title = header.select("p.book_name")[0].text
        writer = header.select("p.book_writer")[0].text
        image = header.select("img")[0]['src']
        sub_link = header.select("a")[0]['href']
        millie_id = sub_link.split('seq=')[1]

        # 책 상세정보페이지 (to get isbn link)
        base_url = f'https://www.millie.co.kr/v3/bookdetail/{millie_id}?nav_hidden=y'

        # isbn 추출 (parent select)
        self.bookstore_crawler.new_tab(base_url)
        soup = self.bookstore_crawler.get_soup()
        container = soup.select(isbn_wrapper)[0]

        try:
            # ISBN이 없는 경우 AttributeError
            isbn_container = container.find('p', string='ISBN').find_parent()
        except AttributeError:
            return None

        isbn_tag = isbn_container.select("strong")
        isbn_val = isbn_tag[0].text
        self.bookstore_crawler.to_preveious_tap()

        # isbn, 순위, 사이트, 제목, 작가, 이미지 수집
        return {
            'isbn': isbn_val,
            'rank': rank,
            'website': 'millie',
            'title': title,
            'writer': writer,
            'image': image
        }

    def fetch_millie_best(self):
        wrapper = 'div#bookList'
        page_books = []

        ori_element = self.bookstore_crawler.select_element(selector=wrapper)[0]
        headers = ori_element.find_all("li", class_=None)
        for j, header in enumerate(headers):
            rst = self._millie_base_info(j, header)
            print(rst)

            if rst:
                page_books.append(rst)

            time.sleep(0.5)

        return page_books

    def export_to_csv(self, in_list, outfile):
        df = pd.DataFrame.from_records(in_list)
        today = dt.datetime.now(gettz('Asia/Seoul')).today().strftime('%Y-%m-%d')
        df['date'] = today
        df = df.drop_duplicates(subset='isbn', keep='first')
        df.to_csv(f'../outfile/rank/{outfile}_{today}.csv', mode='w', index=False, header=True, encoding='utf-8-sig')
        print(outfile+' is saved')

    @staticmethod
    def get_bestseller_list(df1, df2) -> list:
        merged_df = df1.append(df2, sort=True, ignore_index=True)
        df2 = merged_df[['title']]
        df3 = df2.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)
        df3 = df3.sort_values(by='title').reset_index(drop=True)
        # rst = df3.values.tolist()
        rst = df3['title'].tolist()
        return rst

    @staticmethod
    def make_rank_final_score(n_df, m_df):

        n_df['point'] = n_df.apply(lambda x: np.subtract(101, x['rank']), axis=1)
        m_df['point'] = m_df.apply(lambda x: np.subtract(101, x['rank']), axis=1)
        m_df = m_df.drop_duplicates(['title'], keep='first')

        # outer join
        nm_df = pd.merge(n_df, m_df, how='outer', on='title')
        ft_df = nm_df[['isbn_x', 'isbn_y', 'title', 'writer_x', 'writer_y', 'image_x', 'image_y', 'point_x', 'point_y']]
        ft_df['point_x'] = ft_df['point_x'].replace(np.nan, 0)
        ft_df['point_y'] = ft_df['point_y'].replace(np.nan, 0)

        ft_df['rank_total'] = ft_df.apply(lambda x: np.add(x['point_x'], x['point_y']), axis=1)

        ft_df['image'] = ft_df.apply(lambda x: x['image_y'] if x['image_x'] is np.nan else x['image_x'], axis=1)
        ft_df['writer'] = ft_df.apply(lambda x: x['writer_x'] if x['writer_y'] is np.nan else x['writer_y'], axis=1)

        final_df = ft_df[['isbn_x', 'isbn_y', 'title', 'writer', 'point_x', 'point_y', 'rank_total', 'image']]
        final_df.columns = ['isbn_n', 'isbn_m', 'title', 'writer', 'point_n', 'point_m', 'rank_total', 'image']
        final_df = final_df.sort_values(by='rank_total', ascending=False)
        final_df = final_df.reset_index(drop=True)
        final_df.index = np.arange(1, len(final_df) + 1)

        final_df['isbn_n'] = final_df['isbn_n'].astype(str).replace('\.\d+', '', regex=True)

        return final_df

    @staticmethod
    def absolute_maximum_scale(series):
        return series / series.abs().max()

    @staticmethod
    def normalize_twitter(t_df):
        t_grouped = t_df.groupby('title')[['retweet_count']].count()
        return t_grouped

    @staticmethod
    def normalize_kyobo(k_df, today):
        tmp = today.split('-')
        tmp = list(map(int, tmp))
        today_date = dt.datetime(tmp[0], tmp[1], tmp[2])
        month_ago_date = today_date + relativedelta(months=-3)
        month_ago = str(month_ago_date.date())
        k_grouped = k_df[k_df['created_at'] > month_ago][['title', 'created_at']].groupby('title').count()
        return k_grouped

    @staticmethod
    def make_commentary_final_score(t_grouped, k_grouped):
        commentary_df = pd.merge(t_grouped, k_grouped, how='outer', on='title')
        commentary_df = commentary_df.fillna(0)
        commentary_df.reset_index(inplace=True)

        for col in commentary_df.columns:
            if col == 'title':
                continue

            commentary_df[col + '_nz'] = BestBooksCrawler.absolute_maximum_scale(commentary_df[col])

        commentary_df['commentary_total'] = commentary_df.apply(lambda x: np.add(x['retweet_count_nz'], x['created_at_nz']), axis=1)
        commentary_df = commentary_df.sort_values(by='commentary_total', ascending=False).reset_index(drop=True)

        return commentary_df


def main():

    # setup
    option = Options()
    option.add_argument("disable-infobars")
    option.add_argument("disable-extensions")
    # option.add_argument("start-maximized")
    option.add_argument('disable-gpu')
    # option.add_argument('headless')

    # crawler = BestBooksCrawler('https://series.naver.com/ebook/home.series', option)
    #
    today = dt.datetime.now(gettz('Asia/Seoul')).today().strftime('%Y-%m-%d')
    directory = f"../outfile/rank/trending_{today}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    #
    #
    # # 1. 판매량
    # # 1-1a) 네이버 베스트 100 목록 수집
    # naver_list = crawler.fetch_naver_best()
    #
    # # 1-1b) 네이버 CSV 파일로 쓰기
    # crawler.export_to_csv(naver_list, f'trending_{today}/naver')
    #
    # # 1-2a) 밀리의 서재 베스트 100 목록 수집
    # crawler.bookstore_crawler.quit_browser()
    # crawler.bookstore_crawler.new_browser('https://www.millie.co.kr/viewfinder/more_milliebest.html?range=week&referrer=best', option)
    # # millie_link = 'https://www.millie.co.kr/viewfinder/more_milliebest.html?range=week&referrer=best'
    # # crawler = BestBooksCrawler(millie_link, option)
    #
    # millie_list = crawler.fetch_millie_best()
    #
    # # 1-2b) 밀리의 서재 CSV 파일로 쓰기
    # crawler.export_to_csv(millie_list, f'trending_{today}/millie')

    # Best 도서 리스트 추출
    # naver_df = pd.read_csv(f'{directory}/naver_{today}.csv', encoding='utf-8-sig')
    # millie_df = pd.read_csv(f'{directory}/millie_{today}.csv', encoding='utf-8-sig')
    # bestseller_list = BestBooksCrawler.get_bestseller_list(naver_df, millie_df)


    # 2. 관심도
    # 2-1) 트위터 최근 7일내 해당 도서 언급량 수집 & CSV 추출
    # title / text / created_at / retweet_count / favorite_count
    # twitter_crawler = TwitterCrawler(mysecrets.consumer_key, mysecrets.consumer_secret)
    # search_list = ['created_at', 'text', 'retweet_count', 'favorite_count']
    # twitter_crawler.run_crawler(search_list, bestseller_list)

    # 2-2) 교보문고 리뷰 수집 & CSV 추출
    # title / text / created_at
    # setup
    # option = Options()
    # option.add_argument("disable-infobars")
    # option.add_argument("disable-extensions")
    # # option.add_argument("start-maximized")
    # option.add_argument('disable-gpu')
    # # option.add_argument('headless')
    #
    # target = 'https://ebook.kyobobook.co.kr/dig/pnd/welcome'
    # kyobo_review_crawler = ReviewCrawler(target, option)
    #
    # kyobo_review_crawler.run_crawler(bestseller_list)


    # 3. 점수 계산
    # 판매량 : 도서의 각 사이트별 순위를 모두 더한 뒤 x 1로 normalize
    # n_df = pd.read_csv(f'{directory}/naver_{today}.csv', encoding='utf-8-sig')
    # m_df = pd.read_csv(f'{directory}/millie_{today}.csv', encoding='utf-8-sig')
    #
    # final_df = BestBooksCrawler.make_rank_final_score(n_df, m_df)
    #
    # output = 'final_rank_score'
    # final_df.to_csv(f'../outfile/rank/trending_{today}/{output}_{today}.csv', mode='w', index=True, header=True, encoding='utf-8-sig')
    # print(output + ' is saved')


    # 관심량 : 트윗 count x 1로 normalize + 교보 리뷰 count x 1로 normalize
    # # 1. tweet
    # t_df = pd.read_csv(f'{directory}/weekly_tweets_{today}.csv', encoding='utf-8-sig')
    # t_grouped = BestBooksCrawler.normalize_twitter(t_df)
    #
    # # 2. kyobo
    # k_df = pd.read_csv(f'{directory}/weekly_reviews_{today}.csv', encoding='utf-8-sig')
    # k_grouped = BestBooksCrawler.normalize_kyobo(k_df, today)
    #
    # # 3. tweet, kyobo 각각 normalize후 총점 계산
    # commentary_df = BestBooksCrawler.make_commentary_final_score(t_grouped, k_grouped)
    # output = 'final_commentary_score'
    # commentary_df.to_csv(f'../outfile/rank/trending_{today}/{output}_{today}.csv', mode='w', index=True, header=True, encoding='utf-8-sig')
    # print(output + ' is saved')

    # 총 점수 : 관심량 x 0.6 + 판매량 x 0.4로 계산
    rank = pd.read_csv(f'{directory}/final_rank_score_{today}.csv', encoding='utf-8-sig',
                       dtype={'isbn_n': str, 'isbn_m': str, 'title': str}, index_col=0)
    commentary = pd.read_csv(f'{directory}/final_commentary_score_{today}.csv', encoding='utf-8-sig',
                       dtype={'isbn_n': str, 'isbn_m': str, 'title': str}, index_col=0)


    all_in_one = pd.merge(rank, commentary, how='outer', on='title')
    all_in_one = all_in_one.fillna(0)
    a_df = all_in_one[['isbn_n','isbn_m','title','writer','image','rank_total','commentary_total']]

    to_normalize = ['rank_total', 'commentary_total']

    for col in to_normalize:
        a_df[col + '_nz'] = BestBooksCrawler.absolute_maximum_scale(a_df[col])

    a_df['final_score_nz'] = a_df.apply(lambda x: np.add((x['rank_total_nz'] * 0.4), (x['commentary_total_nz'] * 0.6)), axis=1)
    a_df = a_df.sort_values(by='final_score_nz', ascending=False).reset_index(drop=True)
    a_df.index = np.arange(1, len(a_df) + 1)

    output = 'trending_books'
    a_df.to_csv(f'../outfile/rank/trending_{today}/{output}_{today}.csv', mode='w', index=False, header=True, encoding='utf-8-sig')
    print(output + ' is saved')




if __name__ == '__main__':
    main()


