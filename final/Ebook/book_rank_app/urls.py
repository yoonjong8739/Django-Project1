# from django.conf.urls import url
from django.urls import path, include
from . import views

app_name = 'book_rank_app'

urlpatterns = [
    path('', views.homepage, name="homepage"),

    # path('create', views.article_create, name="create"),
    # path('slug/<str:slug>', views.article_details, name="detail"),
]
