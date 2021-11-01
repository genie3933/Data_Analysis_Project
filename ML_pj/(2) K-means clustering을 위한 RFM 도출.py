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

# # K-Means clustering을 위한 RFM 도출

# # 데이터 로드

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

df = pd.read_csv('전처리완료최종데이터.csv', parse_dates=['구매일자'])
df.shape
# -

df.isnull().sum()

df

# ---

# # 데이터 준비
# * rfm_df를 만들기
# * R(최근): 마지막 구매 이후 일수
# * F(빈도): 구매 빈도
# * M(금액): 거래 총액 (기여 수익)
#
# * rfm의 이상치 처리

# ## R, F, M 변수 생성
# * 각각의 변수 생성 후 merge

# * 구매일자와 시간을 합치는 이유: 구매일자를 기준으로 구매빈도를 정하게 되면 중복값이 카운트 되므로 시간까지 고려해 구매횟수를 계산하였다

# +
df_일자시간 = df.copy()

# 구매일자와 구매시간을 합치기 위해 문자열로 타입 변경

df_일자시간['구매일자'] = df_일자시간['구매일자'].astype('str')
df_일자시간['구매시간'] = df_일자시간['구매시간'].astype('str')
df_일자시간['구매일자-시간'] = df_일자시간['구매일자'] + '-' + df_일자시간['구매시간'] 
# df_일자시간.drop(columns = ['구매일자', '구매시간'])
df_일자시간

# +
# Frequency 변수 생성

# 고객별 구매 횟수

rfm_f = pd.DataFrame(df_일자시간.groupby(['ID'])['구매일자-시간'].nunique().reset_index())
rfm_f.columns = ['CustomerID', 'Frequency']
rfm_f.head()

# +
# Recency 변수 생성

# 이 데이터셋의 가장 최근 날짜

max_date = max(df['구매일자'])
df['구매텀'] = max_date - df['구매일자']

# 최신성을 얻기 위해 고객별 마지막 거래가 얼마나 지났는지 알아보기

rfm_r = pd.DataFrame(df.groupby('ID')['구매텀'].min().reset_index())
rfm_r['구매텀'] = rfm_r['구매텀'].dt.days # 일수만 추출
rfm_r.columns = ['CustomerID', 'Recency']



# Monetary 변수 생성

df['총쇼핑금액'] = df['구매금액'] * df['구매수량'] # 수량 * 가격

# 고객별 총 거래 수익

rfm_m = pd.DataFrame(df.groupby('ID')['총쇼핑금액'].sum().reset_index())
rfm_m.columns = ['CustomerID', 'Monetary']

# +
# r, f, m을 merge

rf_merge = pd.merge(rfm_m, rfm_f, on='CustomerID', how='inner')
rfm = pd.merge(rf_merge, rfm_r, on='CustomerID', how='inner')
rfm.head()
# -

rfm.isnull().sum()

rfm.shape

# ## RFM DF의 이상치 탐색 및 제거

rfm.describe()

rfm[rfm['Monetary'] == 18187690]

# +
# boxplot으로 각각의 이상치 탐색

cols = ['Monetary', 'Frequency', 'Recency']

for col in cols : 
    plt.figure(figsize = (10, 6))
    sns.boxplot(data=rfm[col], orient="v", palette="Set2" ,whis=1.5,saturation=1, width=0.7)
    plt.title(f'{col} boxplot', fontsize=20)
    plt.xlabel('속성')
    plt.ylabel('범위')
# -

# * boxplot을 그려본 결과 Monetary, Frequency의 경우 이상치 처리가 필요해보임

# +
# 이상치 제거를 위해 일반적으로 사용하는 사분위수 기준으로 Q1, Q3의 범위 지정

Q1 = rfm.Monetary.quantile(0.25)
Q3 = rfm.Monetary.quantile(0.75)
IQR = Q3 - Q1


# 해당하는 값의 범위만 rfm에 다시 할당
# 최소값은 문제없으므로 최대값만 범위 다시 지정

rfm = rfm[(rfm.Monetary <= Q3 + 1.5*IQR)] 
# rfm = rfm[(rfm.Frequency <= Q3 + 1.5*IQR)]
# -

rfm.describe()

# +
# 최종 RFM

rfm.head()
# print(rfm.shape)
# -

# ---

# # RFM DF CSV 파일 저장

# +
# rfm.to_csv('고객rfm.csv', index=False)
# -




