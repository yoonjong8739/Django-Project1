from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
# from .models import Article
# from django.contrib.auth.decorators import login_required
from trend_book_app.models import TrendingBooks


def base(request):
    mylist='check'
    return render(request, 'trend_book_app/trend-book.html',{'data': mylist})


def main(request):
    query = "select id, weekly_rank, isbn_n, isbn_m, title, writer, image from trend_book_app_trendingbooks limit 6"

    book_list = []
    for book in TrendingBooks.objects.raw(query):
        # print(book)
        book_list.append(book)

    no = [x+1 for x in range(len(book_list))]
    # zip_list = zip(no, book_list)
    # context = {'books': zip_list}
    context = []
    for key, value in zip(no, book_list):
        context.append((key, value))

    return render(request, 'trend_book_app/trends-main.html', {'books': context})


def get_main_trends():
    query = "select id, weekly_rank, isbn_n, isbn_m, title, writer, image from trend_book_app_trendingbooks limit 7"

    book_list = []
    for book in TrendingBooks.objects.raw(query):
        # print(book)
        book_list.append(book)

    no = [x + 1 for x in range(len(book_list))]
    # zip_list = zip(no, book_list)
    # context = {'books': zip_list}
    context = []
    for key, value in zip(no, book_list):
        context.append((key, value))

    return context

def trends_list(request):
    # trends = TrendingBooks.objects.get()
    # trends = TrendingBooks.objects.all()
    query = "select id, weekly_rank, isbn_n, isbn_m, title, writer, image from trend_book_app_trendingbooks"
    books = TrendingBooks.objects.raw(query)
    book_list = []
    for book in TrendingBooks.objects.raw(query):
        # print(book)
        book_list.append(book)

    return render(request, 'trend_book_app/trends-component.html', {'books': book_list})


def trends_all(request):
    # trends = TrendingBooks.objects.get()
    # trends = TrendingBooks.objects.all()
    query = "select id, weekly_rank, isbn_n, isbn_m, title, writer, image from trend_book_app_trendingbooks"
    books = TrendingBooks.objects.raw(query)
    book_list = []
    for book in TrendingBooks.objects.raw(query):
        # print(book)
        book_list.append(book)

    return render(request, 'trend_book_app/trends_all.html', {'books': book_list})


# def article_list(request):
#     # articles = Article.objects.all().order_by('date');
#     # return render(request, 'articles/article_list.html', { 'articles': articles })
#     return None
#
# def article_details(request, slug):
#     # return HttpResponse("hello "+ slug)
#     # article = Article.objects.get(slug=slug)
#     # return render(request, 'articles/article_detail.html', {'article': article })
#     return None
#
# # @login_required(login_url="/accounts/login/")
# def article_create(request):
#     return render(request, 'articles/article_create.html')