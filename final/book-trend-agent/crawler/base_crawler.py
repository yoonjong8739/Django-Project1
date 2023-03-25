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


class BaseCrawler:
    def __init__(self, url: str, option: Options):
        self.url = url
        self.option = option
        self.tmp_soup = None
        self.tmp_dom = None
        self.tmp_header = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }

        # Selenium 4.0 - load webdriver
        try:
            s = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=s, options=self.option)
        except Exception as e:
            print(e)
            return

        # self.wait = WebDriverWait(self.browser, 10)  # timeout in sec

    def set_temp_html(self):
        html = self.browser.page_source
        self.tmp_soup = BeautifulSoup(html, 'html.parser')
        self.tmp_dom = etree.HTML(str(self.tmp_soup))

    def get_soup(self):
        html = self.browser.page_source
        self.tmp_soup = BeautifulSoup(html, 'html.parser')
        self.tmp_dom = etree.HTML(str(self.tmp_soup))
        return self.tmp_soup

    def open_browser(self):
        # Move to URL
        self.browser.get(self.url)
        # self.browser.maximize_window()

    def new_browser(self, url, option):
        self.__init__(url=url, option=option)
        # Move to URL
        a = self. url
        self.browser.get(a)
        # self.browser.maximize_window()

    def move_page(self, url):
        self.browser.get(url)

    def new_tab(self, new_url):
        self.browser.switch_to.new_window('tab')
        self.browser.get(new_url)
        time.sleep(1)

    def to_preveious_tap(self):
        # Closing new_url tab
        self.browser.close()
        # Switching to old tab
        self.browser.switch_to.window(self.browser.window_handles[0])

    def to_previous_page(self):
        self.browser.execute_script("window.history.go(-1)")
        time.sleep(1)

    def quit_browser(self):
        # terminates driver
        self.browser.quit()

    def quick_tag_in_link(self, url, selector):
        r = requests.get(url, headers=self.tmp_header)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            tmp = soup.select(selector)
            element = tmp[0]
            # element = soup.select(selector)[0]
        except:
            return False

        return element

    def quick_attr_in_link(self, url, selector, attr):
        element = self.quick_tag_in_link(url, selector)
        if not element:
            return False

        val = element.get(attr)
        return val

        # r = requests.get(url, headers=self.tmp_header)
        # soup = BeautifulSoup(r.content, 'html.parser')
        # try:
        #     element = soup.select(selector)[0]
        #     val = element.get(attr)
        # except:
        #     return False
        #
        # return val



    def search_keyword(self, text_field: Tuple[By, str], value: str, search: Tuple[By, str]):
        element = self.browser.find_element(*text_field)
        element.clear()
        element.send_keys(value)
        time.sleep(0.5)
        self.browser.find_element(*search).click()

    def click_button(self, button: Tuple[By, str]):
        self.browser.find_element(*button).click()

    def scroll_down(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # 스크롤을 가장 아래로 내린다
        time.sleep(2)
        pre_height = self.browser.execute_script("return document.body.scrollHeight")  # 현재 스크롤 위치 저장

        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # 스크롤을 가장 아래로 내린다
            time.sleep(2)
            cur_height = self.browser.execute_script("return document.body.scrollHeight")  # 현재 스크롤을 저장한다.
            # 스크롤 다운 후 스크롤 높이 다시 가져옴
            if pre_height == cur_height:
                break

            pre_height = cur_height

    def select_element(self, selector: str):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.select(selector)
        return element

    def select_tag_attr_by_xpath(self, selector: str, attr: str):
        html = self.browser.page_source
        tmp_soup = BeautifulSoup(html, 'html.parser')
        tmp_dom = etree.HTML(str(tmp_soup))
        tmp2 = tmp_dom.xpath(selector)[0]
        return tmp2.attrib['href']




    def select_elements(self, selector: str):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.select(selector)
        elements_str = [i.get_text() for i in elements]
        return elements_str


    def get_text(self, button: Tuple[By, str]):
        # self.browser.find_element(*button)

        self.set_temp_html()

        if button[1].endswith('text()'):
            tmp2 = self.tmp_dom.xpath(button[1])[0]
            return str(tmp2).strip()

        tmp = self.tmp_dom.xpath(button[1])[0].text

        return tmp

    def get_attr(self, selector, attr):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.select(selector)[0]
        val = element.get(attr)
        return val


    def check_exists(self, element):
        try:
            self.browser.find_element(*element)
        except NoSuchElementException:
            return False
        return True



    def explicit_loading(self, selector: Tuple[By, str]) -> str:
        element = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((selector[0], selector[1]))
        )
        # elem.text

        return element

