from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name='user_app'

urlpatterns = [
    path('home/', views.init, name='home'),
    path('login/', views.login, name='login'),
    path('join/', views.join, name='join'),
    path('logout/', auth_views.LogoutView.as_view() , name='logout'),
    path('delete/', views.delete, name='delete'),
    path('mypage/', views.mypage, name='mypage'),
    path('update/', views.update, name='update'),
    path('books/', views.select_books, name='books'),
    path('books/<int:pk>/', views.detail, name='detail'),
    path('recommend/', views.recommend, name='recommend'),
]