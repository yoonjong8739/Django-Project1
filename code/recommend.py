import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

# 파일 불러오기
Ebook = pd.read_csv('./data/Ebook_final.csv', encoding = 'utf-8-sig', sep = ',', index_col = False)
#Ebook['ISBN'] = Ebook['ISBN'].astype(str)
#Ebook['ISBN'] = Ebook['ISBN'].str.replace(' ', '')
#Ebook

# 임시 회원 데이터 생성
user = pd.DataFrame({'UserID' : ['guess123', 'guess123', 'multi1234!', 'guess123', 'nice777', 'multi1234!', 'atom123', 'nice777', 'abc888', 'nice777', 
                                'multi1234!', 'nice777', 'multi1234!', 'guess123', 'atom123', 'nam8739', 'nam8739', 'nam8739', 'atom123', 'nice777',
                                'aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff', 'ggg', 'hhh', 'iii', 'jjj',
                                'kkk', 'lll', 'mmm', 'nnn', 'ooo', 'ppp', 'qqq', 'rrr', 'sss', 'ttt',
                                'uuu', 'vvv', 'www', 'xxx', 'yyy', 'zzz', 'aaaa', 'bbbb', 'cccc', 'dddd',
                                'AAA!', 'BBB!', 'CCC!', 'DDD!', 'EEE!', 'FFF!', 'GGG!', 'HHH!', 'III!', 'JJJ!',
                                'KKK!', 'LLL!', 'MMM!', 'NNN!', 'OOO!', 'PPP', 'QQQ!', 'RRR!', 'SSS!', 'TTT!',
                                'UUU!', 'VVV!', 'WWW!', 'XXX!', 'YYY!', 'ZZZ!', 'AAA!', 'RRR!', 'jjj', 'nam8739', 
                                'ppp', 'lll', 'ccc', 'ccc', 'YYY!', 'ZZZ!', 'aaa', 'ddd', 'nice777', 'QQQ!',
                                'aaa', 'ddd', 'fff', 'kkk', 'KKK!', 'zzz', 'CCC!', 'atom123', 'guess123', 'vvv'],
                    'ISBN' : ['9791155352014', '9788937497285', '9791161011943', '9791169796569', '9791197389467', '9791167960566', '9788942104918', '9788920044137', '9791161011943', '9791198013033', 
                            '9791155352168', '9791190313254', '9791192579375', '9788900474992', '9788932964829', '9791155517468', '9791192625287', '9791155352014', '9791190313254', '9788942104918',
                            '9791187142690', '9791188331895', '9791189610074', '9788967821432', '9791187142690', '9791188331895', '9791169216067', '9791197149894', '9791191600285', '9791191600285',
                            '9791155352014', '9791192579375', '9791188331895', '9791165347130', '9791165347130', '9791155352014', '9791191600285', '9791191521238', '9791191521238', '9791191600285',
                            '9788901269665', '9788901269665', '9791189610074', '9791187142690', '9788901269665', '9788901269665', '9791187142690', '9791197149894', '9791191600285', '9791191600285',
                            '9791187142690', '9791165347130', '9791191521238', '979119152123',  '9788997575619', '9791191521238', '9788997575619', '9791155352014', '9791155352168', '9791169796569',
                            '9791188754618', '9791197338250', '9788920023965', '9788992985284', '9788993119084', '9791197338250', '9788926861776', '9788997206216 ', '9788926861776', '9788992985284',
                            '9791186966358', '9791161691480', '9788992164474', '9791157800575', '9791186173909', '9788992164474', '9791161691480', '9788970947877', '9788970947877', '9791186173909',
                            '9791155352168', '9791190313254', '9791192579375', '9788900474992', '9788932964829', '9791155517468', '9791192625287', '9791155352014', '9791190313254', '9788942104918',
                            '9788956994031', '9788998258191', '9788931021288', '9791162994603', '9791196795504', '9791165213206', '9791196622701', '9788998258191', '9788956994031', '9791189909208'],
                    'Read' : [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
                            True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
                            True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
                            True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
                            True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]})

rating_book = pd.merge(user, Ebook, on = 'ISBN')
rating_book

# 평점을 주지 않은 ebook을 리스트 객체로 반환하는 함수인 get_unseen_movies()를 생성
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

def recomm_ebook_by_userid(pred_df, userID, unseen_list, top_n = 10):
    # 예측 평점 DataFrame에서 사용자id 인덱스와 unseen_list로 들어온 ebook_list로 들어온 ebook 칼럼을 추출해 가장 예측 평점이 높은 순으로 정렬함.
    recomm_ebook = pred_df.loc[userID, unseen_list].sort_values(ascending = False)[:top_n]
    return recomm_ebook

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

#SGD 기반의 행렬 분해를 기반으로 한 추천시스템
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

# 사용자-아이템 평점 행렬
rating_matrix = rating_book.pivot_table('Read', index='UserID', columns='title')
rating_matrix = rating_matrix.fillna(0)
rating_matrix  # R : 사용자-아이템 평점 행렬

P, Q = matrix_factorization(rating_matrix.values, K = 50, steps = 200, learning_rate=0.01, r_lambda=0.01)
pred_matrix = np.dot(P, Q.T)

ratings_pred_matrix = pd.DataFrame(data = pred_matrix, index = rating_matrix.index, columns = rating_matrix.columns)
ratings_pred_matrix

# 사용자가 관람하지 않은 ebook 제목 추출
user_id = input("사용자 ID : ")
unseen_list = get_unseen_ebook(rating_matrix, user_id)

# 잠재요인 협업 필터링으로 ebook 추천
recomm_ebook = recomm_ebook_by_userid(ratings_pred_matrix, user_id, unseen_list, top_n=10)

# 평점 데이터를 DataFrame으로 생성
recomm_ebook = pd.DataFrame(data = recomm_ebook.values, index = recomm_ebook.index, columns = ['pred_score'])

print(recomm_ebook)
print(recomm_ebook.index)  # 책 제목만 출력