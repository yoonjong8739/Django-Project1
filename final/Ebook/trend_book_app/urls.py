from django.urls import path, include
from . import views

app_name = 'trend_book_app'

urlpatterns = [
    path('', views.main, name="main"),
    path('trends', views.trends_list, name='trends-list'),


    path('all', views.trends_all, name='trends-all')


    # path('slug/<str:slug>', views.article_details, name="detail"),
    # create/ 하면 이렇게만 써야됨
]