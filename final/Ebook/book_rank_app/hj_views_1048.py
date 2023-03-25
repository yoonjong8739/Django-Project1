import time
from django.shortcuts import render
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
# Create your views here.


def homepage(request):
    # return HttpResponse('homepage')

    Naver_rank()



    return render(request,'book_rank_app/base.html')



# 네이버 시리즈 랭킹
def Naver_rank(request):
    while True:

        global naver_list

        naver_list = []

        options = webdriver.ChromeOptions()

        # 창 열리지 않게
        options.add_argument('headless')
        naver_url = 'https://series.naver.com/ebook/top100List.series'

        driver = webdriver.Chrome('chromedriver', options=options)
        driver.get(naver_url)
        html = driver.page_source
        soup = bs(html, 'html.parser')

        for i in range(10):
            rank = soup.select('li> span.num > em')[i].text.strip()
            image_src = soup.select('ul> li > a > img')[i]['src']
            title = soup.select('ul > li > a > strong')[i].text.strip()
            author = soup.select('ul > li > a > span.writer')[i].text.strip()
            naver_list.append((rank, image_src, title, author))

            time.sleep(3600)
            return render(request,'book_rank_app/base.html',{"rank": rank,"img":image_src,"title":title,"author" :author})


'''
naver 먼저 완성 후 추가

#Yes24 랭킹

def Yes24_rank(request):

    global yes24_list

    yes24_list = []

    options = webdriver.ChromeOptions()

    # 창 열리지 않게
    options.add_argument('headless')
    yes24_url = 'http://www.yes24.com/Mall/Main/EBook/017?CategoryNumber=017'

    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get(yes24_url)
    html = driver.page_source
    soup = bs(html, 'html.parser')
   
    for i in range(10):
        rank = soup.select('div.item_img > div > span > span > em')[i].text.strip()
        image_src = soup.select('div.item_img > div > span > span > a > em.img_bdr > img')[i]['data-original']
        title = soup.select('ul > li > div > div > div.info_row.info_name > a')[i].text.strip()
        author = soup.select('ul > li > div > div.item_info > div.info_row.info_pubGrp > span.info_auth')[i].text.strip()

        yes24_list.append((rank, image_src, title, author))

    return render('base.html', {"data": yes24_list})


'''




