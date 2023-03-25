from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from typing import Tuple
from crawler.base_crawler import BaseCrawler
import pandas as pd
import datetime as dt
from dateutil.tz import gettz


class ReviewCrawler:
    def __init__(self, url: str, option: Options):
        self.bookstore_crawler = BaseCrawler(url, option=option)
        self.bookstore_crawler.open_browser()

    def to_query_page(self, q):
        # wrappers = []
        q_string = q.replace(' ', '%20')
        target = f'https://search.kyobobook.co.kr/search?keyword={q_string}&gbCode=EBK&target=ebook'
        self.bookstore_crawler.move_page(target)
        to_click = 'a.prod_link'

        # 검색결과가 없는 경우
        if not self.bookstore_crawler.check_exists((By.CSS_SELECTOR, to_click)):
            return None

        time.sleep(1)
        try:
            self.bookstore_crawler.click_button((By.CSS_SELECTOR, to_click))
        except:
            try:
                self.bookstore_crawler.click_button((By.CSS_SELECTOR, '.prod_img_load'))
            except:
                return None

        return True



    def get_reviews(self, title):
        value_list = []

        to_scrap = 'div#kloverContents'
        try:
            # 불일치 도서 (ex 학술논문 등)
            wrapper = self.bookstore_crawler.select_element(to_scrap)[0]
            # 동일한 도서인데 제목이 불일치하는 경우 처리 필요?
        except:
            return None

        elements = [child for child in wrapper.contents if child != '\n']

        for elem in elements:
            values = {}
            ori_dict = {'title': title}
            created_at_css = 'div.left_area > div.user_info_box > span:nth-child(4)'
            values['created_at'] = elem.select(created_at_css)[0].text

            text_css = 'div:nth-child(2) > div > div > div > div:nth-child(2) > div > div > div > div'
            original = elem.select(text_css)[0].text
            final_txt = original.replace('\n', ' ').strip()
            values['text'] = final_txt
            ori_dict.update(values)
            value_list.append(ori_dict)

        return value_list

    @staticmethod
    def export_to_csv(in_list, outfile):
        df = pd.DataFrame.from_records(in_list)
        today = dt.datetime.now(gettz('Asia/Seoul')).today().strftime('%Y-%m-%d')
        df['date'] = today
        df.to_csv(f'../outfile/rank/trending_{today}/{outfile}_{today}.csv', mode='w', index=False, header=True, encoding='utf-8-sig')
        print(outfile+' is saved')

    def run_crawler(self, keywords: list) -> None:
        review_list = []

        # keyword = 김미경의 마흔 수업
        for keyword in keywords:
            rst = self.to_query_page(keyword)
            # 검색결과가 존재하지 않는 경우
            if not rst:
                continue

            time.sleep(0.5)
            rst_list = self.get_reviews(keyword)

            if rst_list:
                for item in rst_list:
                    review_list.append(item)

        self.export_to_csv(review_list, 'weekly_reviews')




# if __name__ == '__main__':
#     # setup
#     option = Options()
#     option.add_argument("disable-infobars")
#     option.add_argument("disable-extensions")
#     # option.add_argument("start-maximized")
#     option.add_argument('disable-gpu')
#     # option.add_argument('headless')
#
#     target = 'https://ebook.kyobobook.co.kr/dig/pnd/welcome'
#     kyobo_review_crawler = ReviewCrawler(target, option)
#
#     keyword_list = ['구의 증명', '사라진 여자들', '김미경의 마흔 수업']
#
#     kyobo_review_crawler.run_crawler(keyword_list)
