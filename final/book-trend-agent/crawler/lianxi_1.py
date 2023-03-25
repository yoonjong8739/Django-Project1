from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
from typing import Tuple
from lxml import etree
import requests

# from crawler.bookstore_crawler import NaverSeriesCrawler
#
#
# def test_agent():
#     target = 'https://series.naver.com/ebook/detail.series?productNo=9521460'
#     ns_crawler = NaverSeriesCrawler(target)
#     ns_crawler.bookstore_crawler.open_browser()
#
#     img_selector = '#container > div.aside.NE\=a\:ebi > a > img'
#
#     image = ns_crawler.bookstore_crawler.get_attr(selector=img_selector, attr='src')
#
#     a = 0


# def test01():
#     json = "{\"created_at\": \"Sun Mar 12 08:13:05 +0000 2023\", \"id\": 1634829855895465984, \"id_str\": \"1634829855895465984\", \"text\": \"\\\"\\uc784\\uc5c5\\uc778\\ub4e4\\uc744 \\\" \\uc704\\ud55c \\uac00\\uacf5\\ud488\\uc2dc\\uc7a5\\uc870\\uc0ac\\n\\\"\\ucc45\\ud55c\\uad8c\\\"\\uad6c\\uc785 \\\"\\uae40\\ubbf8\\uacbd\\uc758 \\ub9c8\\ud754\\uc218\\uc5c5\\n#\\uc11c\\ubd80\\uc758\\uac15\\uc7902023.03.12 #\\ud55c\\uad6d\\uc784\\uc5c5\\ud6c4\\uacc4\\uc790\\ud611\\ud68c #\\uc784\\uc5c5\\ud6c4\\uacc4\\uc790 #\\ud574\\ubc1d\\uc74c #\\ud574\\ubc1d\\uc74c\\uc7a5\\uc560\\uc778\\ubcf5\\uc9c0\\ud68c #ESG #\\uc0b0\\ub9bc\\uce58\\uc720 #\\uc0ac\\ud68c\\uc801\\ub18d\\uc5c5 #\\uce58\\uc720\\ub18d\\uc5c5\\uc0ac\\u2026 https://t.co/buhpgKB4xo\", \"truncated\": true, \"entities\": {\"hashtags\": [{\"text\": \"\\uc11c\\ubd80\\uc758\\uac15\\uc7902023\", \"indices\": [39, 49]}, {\"text\": \"\\ud55c\\uad6d\\uc784\\uc5c5\\ud6c4\\uacc4\\uc790\\ud611\\ud68c\", \"indices\": [56, 66]}, {\"text\": \"\\uc784\\uc5c5\\ud6c4\\uacc4\\uc790\", \"indices\": [67, 73]}, {\"text\": \"\\ud574\\ubc1d\\uc74c\", \"indices\": [74, 78]}, {\"text\": \"\\ud574\\ubc1d\\uc74c\\uc7a5\\uc560\\uc778\\ubcf5\\uc9c0\\ud68c\", \"indices\": [79, 89]}, {\"text\": \"ESG\", \"indices\": [90, 94]}, {\"text\": \"\\uc0b0\\ub9bc\\uce58\\uc720\", \"indices\": [95, 100]}, {\"text\": \"\\uc0ac\\ud68c\\uc801\\ub18d\\uc5c5\", \"indices\": [101, 107]}, {\"text\": \"\\uce58\\uc720\\ub18d\\uc5c5\\uc0ac\", \"indices\": [108, 114]}], \"symbols\": [], \"user_mentions\": [], \"urls\": [{\"url\": \"https://t.co/buhpgKB4xo\", \"expanded_url\": \"https://twitter.com/i/web/status/1634829855895465984\", \"display_url\": \"twitter.com/i/web/status/1\\u2026\", \"indices\": [116, 139]}]}, \"metadata\": {\"result_type\": \"recent\", \"iso_language_code\": \"ko\"}, \"source\": \"<a href=\\\"http://twitter.com/download/android\\\" rel=\\\"nofollow\\\">Twitter for Android</a>\", \"in_reply_to_status_id\": null, \"in_reply_to_status_id_str\": null, \"in_reply_to_user_id\": null, \"in_reply_to_user_id_str\": null, \"in_reply_to_screen_name\": null, \"user\": {\"id\": 983268293984239616, \"id_str\": \"983268293984239616\", \"name\": \"\\uc870\\ub3d9\\ud45c\", \"screen_name\": \"W956dRZT7hvTuAn\", \"location\": \"\\ub300\\ud55c\\ubbfc\\uad6d\", \"description\": \"\\uc0ac)\\ud574\\ubc1d\\uc74c\\uc7a5\\uc560\\uc778\\ubcf5\\uc9c0\\ud68c \\uc774\\uc0ac\\uc7a5\\uc870\\ub3d9\\ud45c\\uc785\\ub2c8\\ub2e4\\n\\n\\uc0ac\\ud68c\\uc801\\uae30\\uc5c5 \\uacfc \\uc911\\uc99d\\uc7a5\\uc560\\uc778\\uc0dd\\uc0b0\\ud488\\uc744 \\uc0dd\\uc0b0\\uc6b4\\uc601\\n\\uad00\\ub9ac\\ud558\\uace0\\uc788\\uc2b5\\ub2c8\\ub2e4\\n\\n(\\uc870\\uacbd\\uc2dd\\uc7ac\\uacf5\\uc0ac\\uc5c5,\\ub18d\\uc5c5 \\ud654\\ud6fc \\uae30\\ud0c0\\ud654\\ucd08,\\uc7a5\\uc560\\uc778\\uace0\\uc6a9\\uc11c\\ube44\\uc2a4\\uc9c0\\uc6d0)\\n\\n\\uc0ac\\uc5c5\\uc744 \\ud558\\uace0\\uc788\\uc2b5\\ub2c8\\ub2e4\\n\\ub9ce\\uc740 \\uc0ac\\ub791\\uacfc \\uc544\\ub08c\\uc5c6\\ub294 \\uad00\\uc2ec \\ubd80\\ud0c1\\ub4dc\\ub9bd\\ub2c8\\ub2e4.\", \"url\": \"https://t.co/vb03d8MYRD\", \"entities\": {\"url\": {\"urls\": [{\"url\": \"https://t.co/vb03d8MYRD\", \"expanded_url\": \"https://www.facebook.com/dongpoy.cho\", \"display_url\": \"facebook.com/dongpoy.cho\", \"indices\": [0, 23]}]}, \"description\": {\"urls\": []}}, \"protected\": false, \"followers_count\": 163, \"friends_count\": 354, \"listed_count\": 1, \"created_at\": \"Mon Apr 09 09:00:04 +0000 2018\", \"favourites_count\": 29, \"utc_offset\": null, \"time_zone\": null, \"geo_enabled\": true, \"verified\": false, \"statuses_count\": 708, \"lang\": null, \"contributors_enabled\": false, \"is_translator\": false, \"is_translation_enabled\": false, \"profile_background_color\": \"F5F8FA\", \"profile_background_image_url\": null, \"profile_background_image_url_https\": null, \"profile_background_tile\": false, \"profile_image_url\": \"http://pbs.twimg.com/profile_images/1537289636245950465/tvq08PZ2_normal.jpg\", \"profile_image_url_https\": \"https://pbs.twimg.com/profile_images/1537289636245950465/tvq08PZ2_normal.jpg\", \"profile_banner_url\": \"https://pbs.twimg.com/profile_banners/983268293984239616/1670105489\", \"profile_link_color\": \"1DA1F2\", \"profile_sidebar_border_color\": \"C0DEED\", \"profile_sidebar_fill_color\": \"DDEEF6\", \"profile_text_color\": \"333333\", \"profile_use_background_image\": true, \"has_extended_profile\": true, \"default_profile\": true, \"default_profile_image\": false, \"following\": null, \"follow_request_sent\": null, \"notifications\": null, \"translator_type\": \"none\", \"withheld_in_countries\": []}, \"geo\": null, \"coordinates\": null, \"place\": {\"id\": \"01cf7da075e9af41\", \"url\": \"https://api.twitter.com/1.1/geo/id/01cf7da075e9af41.json\", \"place_type\": \"city\", \"name\": \"Dong-gu\", \"full_name\": \"Dong-gu, Republic of Korea\", \"country_code\": \"KR\", \"country\": \"Republic of Korea\", \"contained_within\": [], \"bounding_box\": {\"type\": \"Polygon\", \"coordinates\": [[[127.410134084176, 36.2122430120538], [127.554044803784, 36.2122430120538], [127.554044803784, 36.446500948914], [127.410134084176, 36.446500948914]]]}, \"attributes\": {}}, \"contributors\": null, \"is_quote_status\": false, \"retweet_count\": 0, \"favorite_count\": 0, \"favorited\": false, \"retweeted\": false, \"possibly_sensitive\": false, \"lang\": \"ko\"}"
#     json2 = json.replace("'\"'", "")
#     with open('try3.json', 'w') as outfile:
#         json_str = json.dumps(json2)
#         json.dump(json_str, outfile)


# def parse_test01():
#     tmp_header = {
#         'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
#     }
#     url = 'https://search.shopping.naver.com/book/catalog/37350394621'
#     isbn_page_parent = '#book_section-info > div.bookBasicInfo_basic_info__HCWyr > ul'
#     r = requests.get(url, headers=tmp_header)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     try:
#         tmp = soup.select(isbn_page_parent)
#         element = tmp[0]
#         # element = soup.select(selector)[0]
#         p = 0
#     except:
#         return False


def test02():
    import requests
    from bs4 import BeautifulSoup

    url = "https://search.kyobobook.co.kr/web/search?vPstrKeyWord=klover&orderClick=LAG"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 상세 도서 페이지 링크 추출
    book_link = soup.select_one("div.title a").get("href")
    book_response = requests.get(book_link)
    book_soup = BeautifulSoup(book_response.text, "html.parser")

    # Klover 리뷰 크롤링
    klover_reviews = book_soup.select("div.tab_con div.box_detail_review div.review_cont")

    for review in klover_reviews:
        print(review.text.strip())



if __name__ == '__main__':
    # test_agent()
    # test01()
    # parse_test01()
    test02()
