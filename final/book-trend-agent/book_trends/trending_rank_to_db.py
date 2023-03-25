# 라이브러리 임포트
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import numpy as np

# pymysql 세팅
db = pymysql.connect(user='bali', host='localhost', passwd='ebookserver4', port=3306, db='ebook')
cursor = db.cursor()

# csv파일 불러오기

df = pd.read_csv('../outfile/rank/trending_2023-03-19/trending_books_2023-03-19.csv', encoding='utf-8-sig',
                 dtype={'isbn_n': str, 'isbn_m': str, 'title': str}, index_col=0, nrows=100)
df.index = np.arange(1, len(df) + 1)
df.reset_index(inplace=True)
df['date'] = '2023-03-19'

df.columns = ['weekly_rank', 'isbn_n', 'isbn_m', 'title', 'writer', 'image', 'rank_total', 'commentary_total', 'rank_total_nz', 'commentary_total_nz', 'final_score_nz', 'date']


# sqlalchemy를 사용해 원하는 database에 csv파일 저장
# engine = create_engine("mysql+pymysql://bali:"+"ebookserver4"+"@localhost:3306/ebook?charset=utf8", encoding="utf-8")
engine = create_engine("mysql+pymysql://bali:"+"ebookserver4"+"@localhost:3306/ebook?charset=utf8")
conn = engine.connect()
dbname = 'trend_book_app_trendingbooks'
df.to_sql(dbname, con=engine, if_exists='append', index=False)
conn.close()

# 저장 확인
sql = "select * from trend_book_app_trendingbooks limit 5"
print(pd.read_sql(sql,db))