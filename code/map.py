import numpy as np
import pandas as pd
import json
import requests
import branca
import folium

seoul_lib = pd.read_csv('./data/서울도서관.csv')

url = 'https://raw.githubusercontent.com/suanlab/dataset/master'
seoul_geo = f'{url}/seoul_municipalities_geo_simple.json'

m = folium.Map(
    location=[37.528043, 126.980238],
    zoom_start=11
)
folium.GeoJson(
    #json.loads(requests.get(seoul_geo).text),
    seoul_geo,
    name='seoul_municipalities'
).add_to(m)

for idx in range(len(seoul_lib)):
    folium.Marker([seoul_lib['위도'][idx], seoul_lib['경도'][idx]],
                tooltip = seoul_lib.iloc[idx, 0]+'<p>'+seoul_lib.iloc[idx, 6]+'<p>'+seoul_lib.iloc[idx, 1]+'<p>'+seoul_lib.iloc[idx, 2]).add_to(m)
    
m.save('seoul_library.html')  # html로 저장 (크롬이 저장된다.)