# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Data-preprocessing
#
# * 데이터셋별로 전처리 후 각각의 파일 생성
# * 전처리할 raw-data 목록: 고객Demo, 쇼핑업종상품구매, 쇼핑외업종상품구매, 쇼핑업종상품분류
# * 외부데이터: 우체국 우편번호 db 사용
# * 원본데이터출처: 제4회 L.point big data Competition 대회 데이터
# * 외부데이터출처: https://www.epost.go.kr/search/zipcode/areacdAddressDown.jsp

# +
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %matplotlib inline 
# %config InlineBackend.figure_format = 'retina' 
# -

# # 고객 Demo
# * 컬럼명 한국어로 바꾸기
# * 성별: 1, 2에서 남성, 여성으로 바꾸기
# * 연령대: PRD(영어)에서 대(한국어)로 바꾸기
# * 거주지: 
#     * null 값 9999로 채우기
#     * 우편번호 앞 3자리로 우체국 데이터와 merge
#     * 우체국 우편번호 db중 '도로명범위' db를 사용
#     * 우편번호 앞 3자리를 기반으로 시, 군, 구 데이터를 merge

customer = pd.read_csv('data/제4회 Big Data Competition-분석용데이터-01.고객DEMO.txt')
customer.head()


# +
# 고객데이터 전처리 함수 생성

def customer_preprocess(customer_df):
    post = pd.read_csv('data/20210903_도로명범위.txt', sep='|')
    post = post[['우편번호', '시도', '시군구']]
    
    # 우편번호 타입 바꾸기
    post['우편번호'] = post['우편번호'].astype('string') 
    
    # 서울과 서울외 우편번호 자리수가 다르기 때문에 따로 처리
    Seoul_real_post = post.iloc[:35817] # 서울지역
    kyonggi_real_post = post.iloc[35817:] # 서울외전체지역
    
    # 서울지역의 우편번호 앞 2자리 가져오기
    Seoul_real_post_list = []
    for i in range(35817): 
        a =Seoul_real_post['우편번호'][i][:2]
        Seoul_real_post_list.append(a)
    
    # 서울외전체지역의 우편번호 앞 세자리만 가지고 오게 만들기
    kyonggi_real_post_list = []
    for i in range(35817,307587):
        b = kyonggi_real_post['우편번호'][i][:3]
        kyonggi_real_post_list.append(b)
    
    # 서울지역 우편번호 리스트와 서울외전체지역 우편번호 앞자리 합치기
    real_post_list = Seoul_real_post_list + kyonggi_real_post_list
    
    # 우편번호에 넣어주기
    post['우편번호'] = real_post_list
    
    # 시도, 우편번호, 시군구만 남게
    post = post[['우편번호', '시도', '시군구']]
    
    real_post_k = pd.DataFrame(post.groupby(['우편번호','시도', '시군구']).count().reset_index())
    real_post_k['우편번호'] = real_post_k['우편번호'].astype('float64')
    
    # 거주지 null값 9999로 채워주기
    customer_df['HOM_PST_NO'] = customer_df['HOM_PST_NO'].fillna(9999)
    
    # 앞의 우편번호 데이터와 고객demo 데이터 merge
    real_customer = pd.merge(customer_df, real_post_k, left_on ='HOM_PST_NO', right_on='우편번호', how='left')
    real_customer.sort_values(ascending=True, by='ID')
    
    # 중복행 삭제
    real_customer = real_customer.drop_duplicates(['ID'])
    
    # 필요없는 컬럼 삭제
    real_customer = real_customer.drop(columns=['HOM_PST_NO', '우편번호'], axis=1)
    
    # 컬럼명 변경
    real_customer.columns = ['ID', '성별', '연령대', '시도', '시군구']
    real_customer['연령대'] = real_customer['연령대'].str.replace('PRD', '대')
    
    # 성별 바꾸는 함수
    def scale(x):
        if x == 1:
            return '남성'
        elif x == 2:
            return "여성"
        
    real_customer['성별'] = real_customer['성별'].apply(lambda x: scale(x))

    return real_customer


# -

# 확인
customer = customer_preprocess(customer)
customer

# # 쇼핑업종상품구매정보
# * 컬럼명 한국어로 바꾸기
# * 업종: 영어로 라벨링 되어있는 부분(A01, A02, ...)을 한국어로 바꾸기
# * 구매일자: int → datetime 형태로 바꿔주기

shop_df = pd.read_csv('data/제4회 Big Data Competition-분석용데이터-02.쇼핑업종 상품구매.txt')
shop_df.head()


# +
# 쇼핑업종데이터 전처리 함수

def shop_preprocess(shop_df):
    
    # 컬럼명 한글로
    shop_df.columns = ['ID', '영수증번호', '업종','상품소분류코드', '점포코드',
                  '구매일자', '구매시간', '구매금액', '구매수량']
    
    # 업종코드를 한글로
    def scale(x):
        if x == 'A01':
            return "백화점"
        elif x == 'A02':
            return "대형마트"
        elif x == 'A03':
            return "슈퍼마켓"
        elif x == 'A04':
            return "편의점"
        elif x == 'A05':
            return "드러그스토어"
    
    shop_df['업종'] = shop_df['업종'].apply(lambda x: scale(x))
    
    # 구매일자 int -> datetime 형태로
    shop_df['구매일자'] = pd.to_datetime(shop_df['구매일자'].astype('string'))
    
    return shop_df


# -

shop_df = shop_preprocess(shop_df)
shop_df.head()

# # 쇼핑외업종이용정보
# * 컬럼명 한국어로 
# * 업종: 영어로 라벨링 → 한국어로 
# * 이용월: int → datetime 형태로

shopno_df = pd.read_csv('data/제4회 Big Data Competition-분석용데이터-03.쇼핑외 업종 상품구매.txt')
shopno_df.head()


# +
# 쇼핑외업종 전처리 함수

def shopno_preprocess(shopno_df):
    shopno_df.columns = ['ID', '쇼핑외업종', '이용월', '이용금액', '이용건수']
    def scale(x):
        if x == 'B01':
            return "호텔"
        elif x == 'B02':
            return "여행사"
        elif x == 'B03':
            return "면세점"
        elif x == 'C01':
            return "영화관"
        elif x == 'C02':
            return "테마파크"
        elif x == 'C03':
            return "야구관람"
        elif x == 'D01':
            return "패스트푸드"
        elif x == 'D02':
            return "패밀리레스토랑"
        elif x == 'D03':
            return "카페"
    
    shopno_df['쇼핑외업종'] = shopno_df['쇼핑외업종'].apply(lambda x:scale(x))
    
    shopno_df['이용월'] = pd.to_datetime(shopno_df['이용월'].astype(str), format='%Y%m')
    
    return shopno_df
    


# -

shopno_df = shopno_preprocess(shopno_df)
shopno_df.head()

# # 쇼핑업종상품분류정보
# * 컬럼명 한국어로
# * 업종: 영어 라벨링 → 한국어로

productvar = pd.read_csv('data/제4회 Big Data Competition-분석용데이터-04.쇼핑업종 상품분류.txt')
productvar.head()


# +
# 상품분류정보 전처리 함수

def product_preprocess(productvar):
    
    productvar.columns=['업종', '상품소분류코드', '소분류명', '중분류명', '대분류명']
    
    def scale(x):
        if x == 'A01':
            return "백화점"
        elif x == 'A02':
            return "대형마트"
        elif x == 'A03':
            return "슈퍼마켓"
        elif x == 'A04':
            return "편의점"
        elif x == 'A05':
            return "드러그스토어"
    
    productvar['업종'] = productvar['업종'].apply(lambda x:scale(x)) 
    
    return productvar


# -

productvar = product_preprocess(productvar)
productvar.head()

# # 전처리된 데이터 저장

# +
# 데이터 저장하기

customer.to_csv('customer.csv', index=False) # 고객 데이터
shop_df.to_csv('shop_df.csv', index=False) # 쇼핑업종 데이터
shopno_df.to_csv('shopno_df.csv', index=False) # 쇼핑외업종 데이터
productvar.to_csv('productvar.csv', index=False) # 상품분류 데이터
# -


