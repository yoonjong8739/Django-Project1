from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from user_app.models import User, Ebooks, User_Wanted, User_Read
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

# Create your views here.

def init(request) :
    user_id = request.session.get('user')
    # print("**************************************")
    # print(user_id)
    if user_id :
        user = User.objects.get(user_id = user_id)
        content = {'user' : user}
        return render(request, 'user_app/main.html', content)
    return render(request, 'user_app/main.html')

def join(request) :
    if request.method == 'POST' :
        context = {}
        user_id = request.POST['user_id']
        user_name = request.POST['user_name']
        user_pwd = request.POST['user_pwd']
        check_pwd = request.POST['check_pwd']
        birthday = request.POST['birthday']
        
        isDup = User.objects.filter(user_id=user_id)
        if isDup.exists() :
            context['message'] = user_id +"가 중복됩니다."
            return render(request, 'user_app/join.html', context)

        else :
            if user_pwd == check_pwd :
                user = User(user_id=user_id, user_name=user_name, user_pwd=user_pwd, birthday=birthday, join_date=datetime.now())
                user.save()
                context['message'] = user_name +"님 회원 가입 되었습니다."
                return HttpResponseRedirect(reverse('user_app:login'))

            else :
                context['message'] = "password가 일치하지 않습니다."
                return render(request, 'user_app/join.html', context)

    elif request.method == 'GET' :
        return render(request, 'user_app/join.html')

def login(request) :
    if request.method == 'POST' :
        context = {}
        user_id = request.POST['user_id']
        user_pwd = request.POST['user_pwd']
        
        isDup = User.objects.filter(user_id=user_id)
        if isDup.exists() :
            checkUser = User.objects.get(user_id=user_id)
            if checkUser.user_pwd == user_pwd :
                request.session['user'] = checkUser.user_id
                context['message'] = checkUser.user_name + '님 반갑습니다.'
                return HttpResponseRedirect(reverse('user_app:home'))
                # return render(request, 'user_app/main.html')
            else :
                context['message'] = "password가 일치하지 않습니다."
                return render(request, 'user_app/login.html', context)

        else :
            context['message'] = '일치하는 회원 정보가 없습니다.'
            return render(request, 'user_app/login.html', context)
                       
    elif request.method == 'GET' :
        return render(request, 'user_app/login.html')

def logout(request) :
    if request.session.get('user') :
        del(request.session['user'])
    return HttpResponseRedirect(reverse('user_app:login'))

def delete(request) :
    if request.method == 'GET' :
        return render(request, 'user_app/delete.html')
    else :
        user = request.session.get('user')
        context = {}
        delUser = User.objects.get(user_id = user)
        check_pwd = request.POST['user_pwd']
        if check_pwd == delUser.user_pwd :
            delUser.delete()
            logout(request)
            context['message'] = '탈퇴되었습니다.'
            return HttpResponseRedirect(reverse('user_app:login'))
        else :
            context['message'] = '비밀번호가 일치하지 않습니다.'
            return render(request, 'user_app/delete.html')


def update(request) :
    if request.method=='GET' :
        return render(request, 'user_app/update.html')
    else :
        context = {}
        user_id = request.session.get('user')
        user = User.objects.get(user_id=user_id)
        update_name = request.POST['user_name']
        update_pwd = request.POST['user_pwd']
        update_check_pwd = request.POST['check_pwd']
        update_bday = request.POST['birthday']

        if update_pwd == update_check_pwd :
            user.user_name = update_name
            user.user_pwd = update_pwd
            user.birthday = update_bday
            user.save()
            context['message'] = '회원 정보가 변경되었습니다.'
            return HttpResponseRedirect(reverse('user_app:mypage'))
        else :
            context['message'] = '비밀번호가 일치하지 않습니다.'
            return render(request, 'user_app/update.html')
        

def mypage(request) :
    if request.method=='GET' :
        user_id = request.session.get('user')
        # print("**************************************")
        # print(user_id)
        if user_id :
            user = User.objects.get(user_id = user_id)
            content = {'user' : user}
            return render(request, 'user_app/mypage.html', content)

    else :
        context = {}
        return render(request, 'user_app/mypage.html')
        
        


def select_books(request) :
    books = Ebooks.objects.all()

    if 'keyword' in request.GET :
        keyword = request.GET['keyword']
        if keyword :
            books = Ebooks.objects.all().filter(title__contains=keyword)

    return render(request, 'user_app/books.html', {"books" : books})


def detail(request, pk) :
    context={}
    if request.method == 'GET' :
        book_detail = Ebooks.objects.get(book_id=pk)
        return render(request, 'user_app/detail.html', {'book_detail' : book_detail})
    else :
        user = request.session.get('user')
        id = User.objects.get(user_id=user).user_id
        book_id = Ebooks.objects.get(book_id = pk).book_id
        print(id, pk)
        if 'forward' in request.POST :
            wanted = User_Wanted(user_id=id, book_id=book_id)
            wanted.save()
            context['message'] = '읽고 싶은 책으로 등록되었습니다.'

        elif 'already' in request.POST :
            already = User_Read(user_id = id, book_id = book_id)
            already.save()
            context['message'] = '읽은 책으로 등록되었습니다.'
        return render(request, 'user_app/detail.html', context)
    

def matrix_factorization(R, K, steps = 200, learning_rate = 0.01, r_lambda = 0.01):
    num_users, num_items = R.shape

    # P와 Q 매트릭스의 크기를 지정하고 정규 분포를 가진 랜덤한 값으로 입력
    np.random.seed(1)
    P = np.random.normal(scale = 1./K, size = (num_users, K))  # 사용자-잠재 요인 행렬
    Q = np.random.normal(scale = 1./K, size = (num_items, K))  # 아이템-잠재 요인 행렬

    prev_rmse = 10000
    break_count = 0

    # R > 0인 행 위치, 열 위치, 값을 non_zeros 리스트 객체에 저장
    non_zeros = [ (i, j, R[i,j]) for i in range(num_users) for j in range(num_items) if R[i, j] > 0 ]

    # SGD 기법으로 P와 Q 매트릭스를 계속 업데이트
    for step in range(steps):
        for i, j, r in non_zeros:
            
            # 실제 값과 예측 값의 차이인 오류 값 구함
            eij = r - np.dot(P[i, :], Q[j, :].T)
            
            # Regulation을 반영한 SGD 업데이트 공식 적용
            P[i, :] = P[i, :] + learning_rate * (eij * Q[j, :] -r_lambda*P[i, :])
            Q[j, :] = Q[j, :] + learning_rate * (eij * P[i, :] -r_lambda*Q[j, :])
            
        rmse = get_rmse(R, P, Q, non_zeros)
        if (step % 10) == 0:
            print("### iteration step : ", step, "rmse : ", rmse)

    return P, Q 

def get_rmse(R, P, Q, non_zeros):
    error = 0
    # 2개의 분해된 행렬 P와 Q.T의 내적으로 예측 R행렬 생성
    full_pred_matrix = np.dot(P, Q.T)

    # 실제 R행렬에서 널이 아닌 값의 위치 인덱스 추출해 실제 R행렬과 예측 행렬 RMSE 추출
    x_non_zero_ind = [non_zero[0] for non_zero in non_zeros]
    y_non_zero_ind = [non_zero[1] for non_zero in non_zeros]
    R_non_zeros = R[x_non_zero_ind, y_non_zero_ind]
    full_pred_matrix_non_zeros = full_pred_matrix[x_non_zero_ind, y_non_zero_ind]
    mse = mean_squared_error(R_non_zeros, full_pred_matrix_non_zeros)
    rmse = np.sqrt(mse)

    return rmse


def recomm_ebook_by_userid(pred_df, userID, unseen_list, top_n = 10):
    # 예측 평점 DataFrame에서 사용자id 인덱스와 unseen_list로 들어온 ebook_list로 들어온 ebook 칼럼을 추출해 가장 예측 평점이 높은 순으로 정렬함.
    recomm_ebook = pred_df.loc[userID, unseen_list].sort_values(ascending = False)[:top_n]
    return recomm_ebook

def get_unseen_ebook(rating_matrix, userID):
    # userID로 입력받은 사용자의 모든 영화 정보를 추출해 시리즈로 변환
    # 반환된 user_rating은 ebook 제목을 인덱스로 가지는 시리즈 객체
    user_rating = rating_matrix.loc[userID, :]

    # user_rating이 0보다 크면 기존에 읽어본 ebook이다. 대상 인덱스를 추출해 list 객체로 만듦.
    already_seen = user_rating[ user_rating > 0 ].index.tolist()

    # 모든 ebook 제목을 list 객체로 만듦.
    ebook_list = rating_matrix.columns.tolist()

    # list conprehension으로 already_seen에 해당하는 영화는 movies_list에서 제외함.
    unseen_list = [ebook for ebook in ebook_list if ebook not in already_seen]

    return unseen_list


def recommend(request) :
    content={}
    if request == 'POST' :
        return render(request, 'user_app/recommend.html')
    else :
        # 세션의 user_id 가져와서 User_Read에 모든 회원이 읽은 책 목록
        user_id = request.session.get('user')
        user = User.objects.get(user_id = user_id)
        content['user'] = user
        r_user = User_Read.objects.all()

        # 전체 책 목록
        all_book=[]
        books = Ebooks.objects.all()
        for i in range(len(r_user)) :
            all_book.append(Ebooks.objects.filter(isbn = r_user[i].book.isbn))

        # user, book DataFrame 초기화
        user = pd.DataFrame(index=[i for i in range(len(r_user))], columns=['UserID', 'ISBN', 'Read'])
        book = pd.DataFrame(index=[i for i in range(len(all_book))], columns=['book_id', 'ISBN', 'title', 'author', 'price', 'star', 'category', 'img'])
        
        # user DataFrame에 object에서 값 추출하여 저장
        for i in range(len(user)) :
            user['UserID'][i] = r_user[i].user.user_id
            user['ISBN'][i] = r_user[i].book.isbn
            user['Read'][i] = True

        # book DataFrame에 object에서 값 추출하여 저장
        for i in range(len(book)) :
            for j in range(len(all_book[i])) :
                # print(all_book[i][j].book_id)
                book['book_id'][i] = all_book[i][j].book_id
                book['ISBN'][i] = all_book[i][j].isbn
                book['title'][i] = all_book[i][j].title
                book['author'][i] = all_book[i][j].author
                book['price'][i] = all_book[i][j].price
                book['star'][i] = all_book[i][j].star
                book['category'][i] = all_book[i][j].category
                book['img'][i] = all_book[i][j].img


        # ISBN으로 user와 book df merge
        rating_book = pd.merge(user, book, on='ISBN')
        # print(rating_book['Read'])

        rating_matrix = rating_book.pivot_table('Read', index='UserID', columns='title')
        rating_matrix = rating_matrix.fillna(0)
        # print(rating_matrix)
        
        P, Q = matrix_factorization(rating_matrix.values, K = 50, steps = 200, learning_rate=0.01, r_lambda=0.01)
        pred_matrix = np.dot(P, Q.T)
        # print(pred_matrix)

        ratings_pred_matrix = pd.DataFrame(data = pred_matrix, index = rating_matrix.index, columns = rating_matrix.columns)
        # print(ratings_pred_matrix)

        unseen_list = get_unseen_ebook(rating_matrix, user_id)

        recomm_ebook = recomm_ebook_by_userid(ratings_pred_matrix, user_id, unseen_list, top_n=10)
        # print(recomm_ebook)

        recomm_ebook = pd.DataFrame(data = recomm_ebook.values, index = recomm_ebook.index, columns = ['pred_score'])

        # print(recomm_ebook.index)
        content['recomm_ebook'] = recomm_ebook.index

        return render(request, 'user_app/recommend.html', content)