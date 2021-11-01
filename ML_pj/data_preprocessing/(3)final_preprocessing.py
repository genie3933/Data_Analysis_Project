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

# # 데이터 전처리
# * 중복행 확인 및 제거
# * 데이터 범위 필터링
# * 이상치 탐색 및 제거

# # 중복행 확인 및 제거

# +
# 라이브러리 불러오기

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import warnings # 경고메세지 무시하기
warnings.filterwarnings(action='ignore')

# +
# 한글폰트

plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False) #마이너스 코드 
pd.options.display.float_format = '{:.3f}'.format
from IPython.display import set_matplotlib_formats #폰트 선명하게 설정.
set_matplotlib_formats('retina') 
pd.Series([-1,0,1,3,5]).plot(title="한글폰트") # 한글폰트와 마이너스 폰트 설정 확인

# +
# 데이터 로드

df = pd.read_csv('df_shop.csv', parse_dates=['구매일자'])
df.drop(columns = ['총_쇼핑소비금액'], inplace=True)
df.shape

# +
# 중복 행 확인

df.duplicated().sum()

# +
# 중복 행 제거

df = df.drop_duplicates()
df
# -

# # 데이터 범위 필터링
# * 시도: 서울특별시
# * 대분류명: 식품

df = df[df['시도'] == '서울특별시']
df = df[df['대분류명'] == '식품']
df

df['중분류명'].unique()

# # 이상치 탐색

# ## 구매금액 탐색 

plt.figure(figsize=(13, 6))
sns.distplot(df['구매금액'])

# distplot을 그려본결과 한 쪽에만 값이 몰려있는 모습

df['구매금액'].describe()

df['구매금액'].sort_values(ascending=False).head(10)

df[df['구매금액'] == 10088000]

# 선어세트 하나에 천만원이 넘는다는 것이 상식적으로 말이 되지 않음

df['구매금액'].sort_values(ascending=False).tail(10)

df[df['구매금액'] == 10]

# 육류가 금액이 10원이라는 것도 말이 안 됨

# ## 구매금액 이상치 제거

# +
# 0.25, 0.75로 자르는 경우 너무 많은 데이터가 잘릴 수 있으므로 최소한의 제거를 위해 0.05, 0.95 선택

Q1 = df['구매금액'].quantile(0.05)
Q3 = df['구매금액'].quantile(0.95)
IQR = Q3 - Q1



# 최대값의 경우 비싼 홍삼세트 같은 제품이 있었기에 범위를 Q3 + 1.5*IQR로 넓게 지정  

df = df[(df['구매금액'] >= Q1) & (df['구매금액'] <= Q3 + 1.5*IQR)]
df
# -

df.describe()

# ## 구매수량 탐색

plt.figure(figsize=(13, 6))
sns.distplot(df['구매수량'])

# 구매수량 역시 앞 쪽에 값이 몰려있는 모습

df['구매수량'].describe()

# +
# 값을 50개로 한정했을때의 distplot

sns.distplot(df[df['구매수량'] < 50]['구매수량'])

# +
# 값을 10개로 한정했을때의 distplot

sns.distplot(df[df['구매수량'] < 10]['구매수량'])
# -

# 값을 10개로 한정했을 때도 distplot의 분포가 앞 쪽에 많이 쏠려있으므로 구매수량의 범위는 10 미만으로 지정

# +
# 최종 데이터

df = df[df['구매수량'] < 10]
df
# -

# # 전처리 완료 df CSV 저장

# +
# df.to_csv('전처리완료최종데이터.csv', index=False)

# +
# 엑셀 저장
# df.to_excel('전처리완료최종데이터.xlsx', index=False)
# -


