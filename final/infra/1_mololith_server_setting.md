# Monolith로 Nginx, Gunicorn, MySql, Django 배포 (Ubuntu)

## 패키지 및 라이브러리 설치 

1. nginx, python3, mysqlclient, virtualvenv 등 다운로드


```bash
sudo apt-get update
sudo apt-get install nginx mysql-server python3-pip python3-dev libmysqlclient-dev ufw virtualenv
sudo apt install python3-venv
```

2. django 파일에서 python3으로 가상환경 만들고 활성화
가상환경이름: myvenv

```bash
sudo mkdir django
cd django
python3 -m venv myvenv
source myvenv/bin/activate
```

3. 필요한 라이브러리 pip install

```bash
(myvenv) cd ~/django/ebook
(myvenv) pip install -r requirements.txt
(myvenv) pip install mysqlclient django gunicorn
```


## 방화벽
- 활성화 하여 port open하거나 disable시킨다.

<br>


## MySql 데이터베이스 세팅

1. mysql 설치 후 root로 로그인
``` bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

2. DB 생성
- 한글 사용한다면 CHARACTER SET utf8 COLLATE utf8_general_ci 설정할 것
- 접속 ID : BALI
- 접속 PW : EBOOKSERVER4
- DB 이름: EBOOK
```
CREATE DATABASE EBOOK DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE USER BALI;
GRANT ALL ON EBOOK.* TO 'BALI'@'%' IDENTIFIED BY 'EBOOKSERVER4';
FLUSH PRIVILEGES;
QUIT
```

## Django Skeleton 참고
```
\home\lab18\django\Ebook\
│
├── myvenv                    # 가상환경
│
└── Ebook
    │
    ├── requirements.txt      # 필요 패키지
    ├── Ebook.sock            # 소켓
    ├── manage.py
    ├── media                 # 유저가 업로드 한 파일
    ├── static
    │    │
    │    ├── user_app
    │    ├── book_app
    │    ├── book_rank_app
    │    ├── map_app
    │    └── trend_book_app   # HTML에 연결되는 개발 리소스
    │        │
    │        ├── slide.js
    │        ├── mypic.jpg
    │        └── styles.css ...
    │
    ├── templates       #  공용 html
    │    │
    │    ├── index.html
    │    └── base-layout.html
    │
    ├── user_app     # 개별 앱 (Feature)
    ├── book_app
    ├── book_rank_app
    ├── map_app
    ├── trend_book_app
    │    │
    │    ├── templates
    │    │    |
    │    │    └── trend_book_app
    │    │        |
    │    │        └── trend-book.html      # 개별 앱의 HTML 파일
    │    │
    │    ├── __init__.py
    │    ├── apps.py
    │    ├── models.py
    │    ├── urls.py
    │    └── views.py
    │
    └── Ebook
        │
        ├── __init__.py
        ├── urls.py
        ├── settings.py
        └── wsgi.py
```

## 데이터 베이스 및 서버 설정

1. Django settings.py 수정

    (/home/lab18/django/Ebook/Ebook/settings.py)

``` python
# -*- coding: utf-8 -*-
# ↑ 주석에 한글 사용하고 싶다면 추가

...

# SECURITY WARNING: don't run with debug turned on in production!
# 1-1. 개발
# DEBUG = True
# 1-2. 배포
DEBUG = False

# 2-1. 개발
# ALLOWED_HOSTS = []
# 2.2. 배포
# ALLOWED_HOSTS = ['127.0.0.1', 'domain.name', 'ip-address']
ALLOWED_HOSTS = ['*']

...

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# 3-2. 배포
DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.mysql',
         'OPTIONS': {
             'sql_mode': 'traditional',
         },
         'NAME': 'EBOOK',
         'USER': 'BALI',
         'PASSWORD': 'EBOOKSERVER4',
         'HOST': 'localhost',
         'PORT': '3306',
     }
}

...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

```

2. DB 마이그레이션

``` bash
(myvenv) cd /home/sypark/django/djangonautic
(myvenv) python manage.py makemigrations
(myvenv) python manage.py migrate
(myvenv) python manage.py collectstatic
```

3. django 단독으로 돌아가는지 확인 (설정 반영 확인차)
- runserver는 개발할때 사용, 실제 배포 X
- 정상 동작하면 끄기
``` python
(myvenv) python manage.py runserver
```


## Gunicorn (웹서비스 게이트웨이) 설정
runserver(개발 확인용) 대신 Gunicorn과 Django를 연결시켜 실행

1. gunicorn 테스트 (gunicorn이 동작하는지 확인)

```
(myvenv) gunicorn --bind 0.0.0.0:8000 Ebook.wsgi:application
(myvenv) gunicorn --bind 0:8000 Ebook.wsgi:application
```
<hr>
[2023-03-17 00:32:42 +0000] [7115] [INFO] Starting gunicorn 20.1.0
[2023-03-17 00:32:42 +0000] [7115] [INFO] Listening at: http://0.0.0.0:8000 (7115)
[2023-03-17 00:32:42 +0000] [7115] [INFO] Using worker: sync
[2023-03-17 00:32:42 +0000] [7118] [INFO] Booting worker with pid: 7118
<br><br>
이렇게 나오면 정상 동작

<hr><br>

> http://15.152.232.36:8000/admin/

브라우저 창에 입력하면 admin 페이지가 css가 적용 안된 채로 나오면 정상 동작

도스창에서 ctrl+c로 테스트용 gunicorn 끄기
<br><br>

2. 데몬용 service 파일 작성 (백그라운드에서 돌아가도록)

```bash
sudo nao /etc/systemd/system/gunicorn.service
```

```
[Unit]
Description=gunicorn service
After=network.target

[Service]
User=lab18
Group=www-data
WorkingDirectory=/home/lab18/django/Ebook/
ExecStart=/home/lab18/django/myvenv/bin/gunicorn \
           --access-logfile - --workers 3 \
           --bind unix:/home/sypark/django/Ebook/Ebook.sock \
           Ebook.wsgi:application

[Install]
WantedBy=multi-user.target

```
ctrl+o -> ctrl+x로 저장 닫기

3. 데몬 service 실행

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
sudo systemctl status gunicorn.service

```

```
# 참고
sudo systemctl restart gunicorn
sudo systemctl stop gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

데몬으로 실행시키면 status만 확인하면 되고
> http://15.152.232.36:8000/admin/

로는 접속이 되지 않음 -> NGINX랑 연결하면 최종 확인 가능하니 넘어갈 것

<br>

## Nginx (Load Balancer, Web Server, & Reverse Proxy) 설정

- nginx 설정은 sites-available(가능한 것), <b><u>sites-enabled</u></b>(실행할 것)이 구분되어있음
    1. 먼저 sites-available 폴더에 nginx 설정파일을 만들고
    2. sites-enabled 폴더로 링크를 건다음에 (복사되는 것임)
    3. sites-enabled 폴더 안의 default를 지우면(기존에 설정된 하드링크 풀기)
    4. default 대신 내가 만든 설정파일로 nginx를 실행시킬 수 있음

1. nginx 설정 파일 작성
```
sudo nano /etc/nginx/sites-available/Ebook
```

```
server {
       listen 1180;
       server_name 127.0.0.1;
       location = /favicon.ico {access_log off;log_not_found off;}

        location /static/ {
            alias /home/lab18/django/Ebook/static/;
        }

        location /media/ {
            alias /home/lab18/django/Ebook/media/;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/lab18/django/Ebook/Ebook.sock;
        }
     }

```
- <b><u>listen</u></b> = 유저(client)에게서 받을 port
 
    기본은 80인데, 다른 프로그램이 port 80을 사용해서 겹치는 경우가 있어서
    겹치지않는 대역대로 설정 -> 1180

- <b><u>server_name</u></b> = gunicorn이 있는 서버 주소
 
    monolith라서 1대의 서버 안에 nginx & (gunicorn+django)가 같이 있기때문에
    127.0.0.1(inernal ip)로 설정
    
    -> 물리적으로 분리되어있다면 gunicorn+django가 있는 ip 기재할 것

- <b><u>location /static/</u></b> = django settings.py의 static 폴더 위치
 
- <b><u>location /media/</u></b> = django settings.py의 media 폴더 위치

- <b><u>proxy_pass</u></b> = django 프로젝트의 socket 파일 위치


<br>

2. default 링크 삭제 (초기 nginx 세팅 제거)
```
sudo rm /etc/nginx/sites-enabled/default
```
sites-enabled만 지우는 것이라서 sites-available에는 default 파일이 남아있음

3. 내가설정한 파일 link 걸기

    nginx는 sites-enable에 있는 파일로 설정하여 실행됨

```
sudo ln -s /etc/nginx/sites-available/Ebook /etc/nginx/sites-enabled

sudo ln -sf /etc/nginx/sites-available/Ebook /etc/nginx/sites-enabled/

```

/etc/nginx/sites-enabled/ 폴더에 Ebook이라는 파일이 있으면 정상

4. 실행
```
sudo service nginx restart
```

- nginx 오류있는지 확인
```
sudo nginx -t
```

- nginx 데몬 정상동작하는지 확인
```
sudo systemctl status nginx
```
 nginx.service - A high performance web server and a reverse proxy server

   Loaded: loaded(/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   
   Active: <span style="color:green"><b>active (running)</b></span> since Thu 2023-03-16 08:36:29 UTC; 17h ago


로 나오면 정상 동작

<br>

## Client(user)에서 최종 확인

> http://15.152.232.36:1180/admin/

css 적용이 된 admin 화면이 나오면 정상 동작

- flow:
    1. nginx의 1180 포트로 유저가 접속
    2. nginx가 gunicorn 8000 포트로 전달
    3. django가 request를 받고 처리 값 response
    4. nginx에서 static 파일과 response를 결합해서 client로 return


<br>


##  Monolith로 Django 서버 띄우기 완성 :sparkles:
<br>
<img src="https://www.marinhumane.org/wp-content/uploads/2021/04/Congrats.jpg" width=130/>
<br>
<b>Congratulations!!</b>

:tada: :tada: :tada: :tada: 