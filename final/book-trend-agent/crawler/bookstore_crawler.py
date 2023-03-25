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
from base_crawler import BaseCrawler
import pandas as pd


class NaverSeriesCrawler:
    def __init__(self, url: str):
        option = Options()
        option.add_argument("disable-infobars")
        option.add_argument("disable-extensions")
        # option.add_argument("start-maximized")
        option.add_argument('disable-gpu')
        # option.add_argument('headless')

        self.bookstore_crawler = BaseCrawler(url, option=option)
        # self.translation_xpath = '//*[@id="content"]/ul[1]/li[1]/ul/li[2]/span'
        self.translation_xpath = '//*[@id="content"]/ul[1]/li[1]/ul/li[6]/span'

    def check_adult(self):
        html = self.bookstore_crawler.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # 성인인증 페이지 여부
        try:
            adult_msg = soup.select('span#adult_msg')[0].text
            if '서비스 이용을 위해 연령 확인이 필요합니다.' in adult_msg:
                return 1
            else:
                return 0
        except:
            print('check_adult error')
            return -1

    # 1. 'div.bookBasicInfo_info_detail__I0Fx5' 2. 'div#book_section-info > div.bookBasicInfo_basic_info__HCWyr > ul > li:nth-child(2) > div > div.bookBasicInfo_info_detail__I0Fx5')[0] 3.
    def get_isbn_code(self, isbn):
        html = self.bookstore_crawler.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        big=soup.select(isbn)
        try:
            isbn = big[2].text
        except:

            # 성인인증 페이지 여부
            try:
                adult_msg = soup.select('span#adult_msg')[0].text
                if '서비스 이용을 위해 연령 확인이 필요합니다.' in adult_msg:
                    return False
            except:
                pass
            # alternative = soup.select('div.bookBasicInfo_info_detail__I0Fx5')[0]

            parent_selector = '#book_section-info > div.bookBasicInfo_basic_info__HCWyr'
            try:
                base = soup.select(parent_selector)[0]
            except IndexError:
                return False

            for i in range(2, 5):
                try:
                    inner = base.select(f"ul.bookBasicInfo_list_info__2zETc > li:nth-child({i}) > div.bookBasicInfo_inner__YIfRy")[0]
                    is_isbn = inner.select('.bookBasicInfo_info_title__a5LHB')[0].text

                    # parent div안에 title(ISBN)과 detail(97911646641338)이 각자의 div태그로 존재
                    # -> ISBN 검증 후 parent div(inner)의 2번째 div를 선택해 text를 추출
                    if is_isbn == 'ISBN':
                        tmp = inner.select('div:nth-child(2)')
                        isbn = tmp[0].text
                        return isbn
                    else:
                        # unable to find ISBN in the loop
                        if i == 5:
                            return False


                except:
                    # unavailable to collect
                    return False




            alternative = soup.select('div#book_section-info > div.bookBasicInfo_basic_info__HCWyr > ul > li:nth-child(2) > div > div.bookBasicInfo_info_detail__I0Fx5')[0]
            alt_text = alternative.text

            # isbn collected
            return alt_text


        return isbn

    def get_isbn_link(self, isbn_page_button):
        isbn_link = self.bookstore_crawler.select_tag_attr_by_xpath(selector=isbn_page_button, attr='href')

        return isbn_link

    def scrap_detail_by_page(self, i, data_to_collect, category):
        # move to detail page
        detail_path = '//*[@id="content"]/div/ul/li[{num}]/a/span'.format(num=i)  # img
        self.bookstore_crawler.click_button((By.XPATH, detail_path))

        # isbn을 조회할 책정보 및 성인인증 화면인 경우 이전 페이지로 이동
        isbn_page_button = '//*[@id="content"]/ul[1]/li[2]/span/a'
        if self.bookstore_crawler.check_exists((By.XPATH, isbn_page_button)) is not True:
            self.bookstore_crawler.to_previous_page()
            return None

        # 책 정보 수집
        # - 책 제목        - 작가        - 가격        - 별점        - 카테고리        - 등급
        curr_detail = {'isbn': '', 'category': category}
        self.bookstore_crawler.set_temp_html()

        for key, value in data_to_collect.items():

            if key == 'rating' and self.bookstore_crawler.check_exists((By.XPATH, self.translation_xpath)):
                value_for_translated_books = value.replace('[4]', '[5]')

                key_text = self.bookstore_crawler.get_text((By.XPATH, value_for_translated_books))
                curr_detail[key] = key_text
                continue

            key_text = self.bookstore_crawler.get_text((By.XPATH, value))
            curr_detail[key] = key_text

        # 이미지 수집
        img_selector = '#container > div.aside.NE\=a\:ebi > a > img'
        image_url = self.bookstore_crawler.get_attr(selector=img_selector, attr='src')
        curr_detail['img'] = image_url

        # ISBN 수집
        isbn_link = self.get_isbn_link(isbn_page_button)
        self.bookstore_crawler.new_tab(new_url=isbn_link)
        isbn_css = 'div.bookBasicInfo_info_detail__I0Fx5'

        isbn_text = self.get_isbn_code(isbn_css) #returns false in case of rate-18
        if not isbn_text:
            # tab 닫기
            self.bookstore_crawler.to_preveious_tap()
            # 상세페이지에서 -> 책목록으로 돌아가기
            self.bookstore_crawler.to_previous_page()
            print(curr_detail, 'rating-18: unable to collect')
            return False

        curr_detail['isbn'] = isbn_text


        # data type 변환 및 기타 처리
        try:
            curr_detail['price'] = int(curr_detail['price'].replace(",", ""))
        except:
            curr_detail['price'] = 0


        if curr_detail['grade'] == '':
            curr_detail['grade'] = '전체 이용가'

        # tab 닫기
        self.bookstore_crawler.to_preveious_tap()

        # 상세페이지에서 -> 책목록으로 돌아가기
        self.bookstore_crawler.to_previous_page()
        print(curr_detail)
        return curr_detail



def naver_series_agent(category_num:int, page_range:tuple):
    ######## Data Setup #############
    category_dict = {
        '소설': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=301&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '시/에세이': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=302&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '경제/경영': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=303&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',

        '자기계발': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=304&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '인문': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=305&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '역사/문화': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=306&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '사회': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=307&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '과학': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=308&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '예술/종교': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=309&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '어린이/청소년': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=310&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '생활': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=311&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '취미': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=312&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '어학': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=313&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        'IT': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=314&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '학습': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=315&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        '해외도서': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=316&orderTypeCode=new&isFree=false&isDiscounted=false&isPcPossible=false&page=',
        # '19세 미만 관람불가 성인': 'https://series.naver.com/ebook/categoryProductList.series?categoryTypeCode=genre&genreCode=19',
    }

    data_to_collect = {
        'book_name': '//*[@id="content"]/div[1]/h2',
        'author': '//*[@id="content"]/ul[1]/li/ul/li[1]/a',
        'price': '//*[@id="content"]/dl[2]/dd[1]/span[1]/strong',
        'star': '//*[@id="content"]/div[1]/div[1]/em',
        # 'category': '//*[@id="content"]/ul[1]/li[1]/ul/li[4]/a',
        'grade': '//*[@id="content"]/ul[1]/li[1]/ul/li[4]/text()'
    }

    cat_list = list(category_dict.keys())
    eng_list = ['novel', 'poem', 'economics', 'selfimprovement', 'humanities', 'history', 'society', 'science', 'art', 'kids', 'living', 'hobby', 'lang', 'IT', 'edu', 'intl']

    cat = cat_list[category_num]
    target = category_dict[cat]
    # page = (226, 1099)
    page = page_range
    # outfile = 'naver_series_1_novel'
    outfile = f"naver_series_{category_num+1}_{eng_list[category_num]}"
    cur_page = page[0]
    ns_crawler = NaverSeriesCrawler(target+str(cur_page))

    #####################

    # page setup
    ns_crawler.bookstore_crawler.open_browser()
    time.sleep(1)
    if page[0] > 1:
        tmp = target+str(page[0])
        ns_crawler.bookstore_crawler.move_page(tmp)

    # 페이지 범위 loop
    for cur_page in range(page[0]+1, page[1]+2):
        book_detail_list = []

        # 한 페이지 내의 도서 수집 loop (total:25개)
        for i in range(1, 26):
            book_detail_dict = ns_crawler.scrap_detail_by_page(i, data_to_collect, cat)
            if book_detail_dict:
                book_detail_list.append(book_detail_dict)
            else:
                # book detail 수집 실패
                pass


        ns_crawler.bookstore_crawler.move_page(target+str(cur_page))

        # 수집 records 저장
        book_df = pd.DataFrame.from_records(book_detail_list)
        print(f"cur_page = {cur_page}")

        book_df.to_csv(f'../outfile/{outfile}_page_{page[0]}-{page[1]}.csv', mode='a', index=False, header=False, encoding='utf-8-sig')

    print('finished')


if __name__ == '__main__':

    print('*******************************')
    print('Program started')
    print('*******************************')

    # # 1 시/에세이 finished
    # idx = 1
    # start = 1
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 2 경제/경영 finished
    # idx = 2
    # start = 1
    # end = 100
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 3 자기계발 finished
    # idx = 3
    # start = 1
    # end = 100
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 4 인문 finished
    # idx = 4
    # start = 1
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # # 5 역사/문화 finished
    # idx = 5
    # start = 3
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    #
    # # 6 사회 finished
    # idx = 6
    # start = 1
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 7 과학 finished
    # idx = 7
    # start = 1
    # end = 100
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 8 예술/종교 finished
    # idx = 8
    # start = 1
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 9 어린이/청소년 finished
    # idx = 9
    # start = 24
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # 10 생활 finished
    # idx = 10
    # start = 1
    # end = 100
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # # 11 취미 finished
    # idx = 11
    # start = 16
    # end = 50
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # # 12 어학 finished
    # idx = 12
    # start = 1
    # end = 30
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    # # 13 IT finished
    # idx = 13
    # start = 1
    # end = 10
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # print('*******************************')
    # print('finished all')
    # print('*******************************')

    ''' 2회차 수집 '''

    # 0 소설
    idx = 0
    start = 227
    end = 400
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 0 소설
    idx = 0
    start = 401
    end = 600
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 1 시/에세이
    idx = 1
    start = 201
    end = 400
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 2 경제/경영
    idx = 2
    start = 101
    end = 200
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 3 자기계발
    idx = 3
    start = 101
    end = 200
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 4 인문
    idx = 4
    start = 201
    end = 400
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # # 5 역사/문화  finished max 203
    # idx = 5
    # start = 3
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')
    #
    #
    # # 6 사회 finished max 256
    # idx = 6
    # start = 1
    # end = 200
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # # 7 과학 finished max 115
    # idx = 7
    # start = 1
    # end = 100
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    # 8 예술/종교
    idx = 8
    start = 201
    end = 400
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 9 어린이/청소년
    idx = 9
    start = 201
    end = 400
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 10 생활
    idx = 10
    start = 101
    end = 200
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 11 취미
    idx = 11
    start = 51
    end = 100
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # 12 어학
    idx = 12
    start = 31
    end = 80
    print(f'start idx {idx} - {start} to {end}')
    naver_series_agent(idx, (start, end))
    print(f'finished idx {idx} - {start} to {end}')

    # # 13 IT finished max 28
    # idx = 13
    # start = 1
    # end = 10
    # print(f'start idx {idx} - {start} to {end}')
    # naver_series_agent(idx, (start, end))
    # print(f'finished idx {idx} - {start} to {end}')

    print('*******************************')
    print('finished all')
    print('*******************************')




