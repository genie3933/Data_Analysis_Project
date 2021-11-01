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

# # 1. 배경

# *흩어져있는 고객 데이터를 '군집'시키는 것이 목적*
# * 본 프로젝트에서는 마케팅에서 보편적으로 쓰이는 방식인 RFM을 기준으로 점수를 부여하여 군집을 나누는 방안을 채택하였다.
# * 그러나 데이터별로 각 변수의 중요도가 다르기 때문에 회귀모델을 이용하여 가중치를 도출하여 도출된 가중치를 최종 RFM Score에 적용하려고 한다.

# # 2. 데이터 살펴보기 

# ## 2.1 데이터 불러오기

# +
# 라이브러리 불러오기

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve, precision_score, recall_score, f1_score
import statsmodels.api as sm
import matplotlib.pyplot as plt
plt.rc("font", family="Malgun Gothic") #한글 폰트 
plt.rc("axes", unicode_minus=False) #마이너스 코드 
import time 
pd.Series([-1,0,1,3,5]).plot(title="한글폰트") # 한글폰트와 마이너스 폰트 설정 확인
from IPython.display import set_matplotlib_formats #폰트 선명하게 설정.
import warnings # 경고메세지 무시하기
warnings.filterwarnings(action='ignore')
# -

df_shop = pd.read_csv('data/전처리완료최종데이터.csv')
df_shop['구매일자'] = df_shop['구매일자'].astype('datetime64')
df_shop['구매월'] = df_shop['구매일자'].dt.month
df_shop.head()

df_shop.columns

df_shop.info()

plt.figure(figsize=(20, 8))
plt.title('월별 매출 현황', fontsize=20)
df_shop.groupby('구매월')['구매금액'].sum().plot()

# +
# 12개월 기준으로 8개월과 4개월을 분리

df_shop_aug = df_shop[df_shop['구매월']<=8]
df_shop_nov = df_shop[df_shop['구매월']>8]
# -

plt.figure(figsize=(20, 8))
plt.title('8개월 매출 현황', fontsize=20)
df_shop_aug.groupby('구매월')['구매금액'].sum().plot()

plt.figure(figsize=(20, 8))
plt.title('4개월 매출 현황', fontsize=20)
df_shop_nov.groupby('구매월')['구매금액'].sum().plot()

# # 3. 가중치 실험

# * 1년간의 고객 구매데이터를 **앞의 8개월과 뒤의 4개월 데이터로 분할**하였다.
# * 앞의 8개월 데이터에서는 R,F,M 값을 관측하고 뒤의 4개월 데이터에서는 해당 기간 동안의 구매 여부를 1(구매함)과 0(구매하지 않음)으로 코딩하여 이분형 자료를 만들었다. 
# * 이렇게 두 개로 나뉜 데이터를 비교하여 예측되는 값을 토대로 가중치로 선택하였다.
# * 참고 논문 출처: 김동석, <RFM 모형의 가중치 선택에 관한 연구>

df_shop_aug.head()

df_shop_nov.head()

# ## 3.2 가중치를 구하기 위한 로지스틱 회귀 모델 생성
# * 8개월 데이터의 RFM 분석으로 4개월 데이터에 영향을 미치는 요인의 우선순위를 찾아 가중치를 구하고자 한다.
# * 그 과정에서 데이터 특성상 목표변수를 생성할 수 있어(구매/비구매) 로지스틱 회귀 모델을 이용하였다.

# ### 3.2.1 8개월 데이터의 RFM

# +
# Monetary 변수 생성

df_shop_aug['총쇼핑금액'] = df_shop_aug['구매금액'] * df_shop_aug['구매수량'] # 수량 * 가격

# 고객별 총 거래 수익

rfm_aug_m = pd.DataFrame(df_shop_aug.groupby('ID')['총쇼핑금액'].sum().reset_index())
rfm_aug_m.columns = ['CustomerID', 'Monetary']
rfm_aug_m.head()

# +
# Frequency 변수 생성

# 고객별 구매 횟수

rfm_aug_f = pd.DataFrame(df_shop_aug.groupby(['ID'])['구매일자'].count().reset_index())
rfm_aug_f.columns = ['CustomerID', 'Frequency']
rfm_aug_f.head()

# +
# Recency 변수 생성

# 이 데이터셋의 가장 최근 날짜
max_date = max(df_shop_aug['구매일자'])
max_date
# -

df_shop_aug['구매텀'] = max_date - df_shop_aug['구매일자']
df_shop_aug.head()

# +
# 최신성을 얻기 위해 고객별 마지막 거래가 얼마나 지났는지 알아보기

rfm_aug_r = pd.DataFrame(df_shop_aug.groupby('ID')['구매텀'].min().reset_index())
rfm_aug_r['구매텀'] = rfm_aug_r['구매텀'].dt.days # 일수만 추출
rfm_aug_r.columns = ['CustomerID', 'Recency']
rfm_aug_r.head()

# +
# r, f, m을 merge

rf_aug_merge = pd.merge(rfm_aug_m, rfm_aug_f, on='CustomerID', how='inner')
rfm_aug = pd.merge(rf_aug_merge, rfm_aug_r, on='CustomerID', how='inner')
rfm_aug.head()
# -

# ### 3.2.2 이상치 탐색 및 제거

# +
# boxplot으로 각각의 이상치 탐색

cols = ['Monetary', 'Frequency', 'Recency']

for col in cols : 
    plt.figure(figsize = (10, 6))
    sns.boxplot(data=rfm_aug[col], orient="v", palette="Set2" ,whis=1.5,saturation=1, width=0.7)
    plt.title(f'{col} boxplot', fontsize=20)
    plt.xlabel('속성')
    plt.ylabel('범위')
# -

# 'Monetary' 변수에 이상치가 보이므로 이상치를 제거해주도록 한다

# +
# 사분위수를 기준으로 이상치 제거

Q1 = rfm_aug.Monetary.quantile(0.25)
Q3 = rfm_aug.Monetary.quantile(0.75)
IQR = Q3 - Q1

# 해당하는 값의 범위만 rfm_aug에 다시 할당
# 즉, 이상치를 제외

rfm_aug = rfm_aug[(rfm_aug.Monetary >= Q1 - 1.5*IQR) & (rfm_aug.Monetary <= Q3 + 1.5*IQR)] 
# -

sns.boxplot(rfm_aug['Monetary'])

# ### 2.2.3 4개월 데이터 구매여부 컬럼 생성
# * 0: 구매 X
# * 1: 구매 O

df_shop_nov['y'] = df_shop_nov['구매금액'] * df_shop_nov['구매수량'] # 수량 * 가격


# +
# 변수생성
# 총쇼핑금액으로 8개월 데이터 구매자가 4개월 데이터에서 구매했는지 알아보고자 ID를 key값으로 merge 실행
# y값이 비어있는경우, 4개월 데이터에서는 구매하지 않은 것.

aug_money = pd.DataFrame(df_shop_aug.groupby('ID')['총쇼핑금액'].sum()).reset_index()  # 8개월 데이터에서의 고객별 총 쇼핑금액
nov_money = pd.DataFrame(df_shop_nov.groupby('ID')['y'].sum()).reset_index()  # 4개월 데이터에서의 고객별 총 쇼핑금액(y)
money = pd.DataFrame(pd.merge(aug_money, nov_money, how='left', on='ID')) # 위 두개의 데이터를 합친 데이터
# -

print(aug_money.shape, nov_money.shape)

money.head()

money.shape

# +
# 비어있는 값 0으로 채움

money['y'] = money['y'].fillna(0)

# +
# 값이 0이 아닌경우에는 다 1로 바꾸기

money['y'][money['y'] != 0] = 1

# +
# 구매함 : 1, 구매하지 않음 : 0

money = money.drop(columns='총쇼핑금액', axis=1)
money = money.rename(columns={'y':'구매여부'})
money.head()

# +
# 최종데이터 (8개월 데이터에 구매여부를 생성)

rfm_aug_binary = pd.merge(rfm_aug,money, how='inner', left_on='CustomerID', right_on='ID')
rfm_aug_binary = rfm_aug_binary.drop(columns='ID', axis=1)
rfm_aug_binary.head()
# -

rfm_aug_binary.shape

rfm_aug_binary['구매여부'].value_counts()

rfm_aug_binary.isnull().sum()

rfm_aug_binary['구매여부'] = rfm_aug_binary['구매여부'].astype('int')

rfm_aug_binary.info()

# ### 2.2.4 Scaling

# - 로지스틱 회귀분석에 앞서 각각 변수의 범위가 차이가 많이나므로 스케일링을 진행하였다

# +
from sklearn.preprocessing import StandardScaler

rfm_aug_log = rfm_aug_binary[['Monetary', 'Frequency', 'Recency']]

scaler = StandardScaler()

# fit_transform
scaled_rfm_aug = scaler.fit_transform(rfm_aug_log)
print(scaled_rfm_aug.shape)
scaled_rfm_aug = pd.DataFrame(scaled_rfm_aug)
scaled_rfm_aug.columns = ['Monetary', 'Frequency', 'Recency']
scaled_rfm_aug
# -

scaled_rfm_aug['CustomerID'] = rfm_aug_binary['CustomerID']
scaled_rfm_aug['구매여부'] = rfm_aug_binary['구매여부']
scaled_rfm_aug = scaled_rfm_aug[['CustomerID', 'Monetary', 'Frequency', 'Recency', '구매여부']]
scaled_rfm_aug['구매여부'] = scaled_rfm_aug['구매여부'].astype('int')

# +
# 모델 학습에 있어 CustomerID는 제거.

scaled_rfm_aug = scaled_rfm_aug.drop(columns='CustomerID', axis=1)
scaled_rfm_aug.head()
# -

# ### 2.2.5 로지스틱 회귀 모델 생성 

# +
# 구매여부는 y값이므로 제외. 나머지 컬럼들을 X로 지정

feature_columns = scaled_rfm_aug.columns.difference(['구매여부'])

# 독립변수와 종속변수를 지정
# 독립변수(feature_columns): Monetary, Frequency, Recency
# 종속변수(y): 구매여부

X = scaled_rfm_aug[feature_columns] 
y = scaled_rfm_aug['구매여부']


# 훈련세트와 테스트 세트 생성 
train_x, test_x ,train_y, test_y = train_test_split(X, y, stratify=y,train_size=0.7,test_size=0.3,random_state=42)
print(train_x.shape, test_x.shape, train_y.shape, test_y.shape)


# +
# 로지스틱 회귀분석 모델 생성 후 훈련

model = LogisticRegression(random_state=42)
model.fit(train_x, train_y)

# +
# 모델 평가

pred = model.predict(test_x)
pred_proba = model.predict_proba(test_x)
accuracy = accuracy_score(test_y, pred)
roc_auc_score = roc_auc_score(test_y, pred)

print('accuracy : {:.3f}'.format(accuracy))
print('roc_auc_score : {}'.format(roc_auc_score))
# -

roc_auc_score

# ### 2.2.6 GridSearchCV를 이용한 하이퍼 파라미터 튜닝

# +
# GridSearchCV로 최적의 파라미터 값 찾기

from sklearn.model_selection import GridSearchCV

parameters = {'C':[0.001, 0.01, 0.1, 1, 10, 100], 'penalty' : ['l1', 'l2'], 'max_iter': [300, 500, 1000]}
grid_search = GridSearchCV(model, parameters, n_jobs=-1, cv=3, scoring='roc_auc')
grid_search.fit(train_x, train_y)
grid_search.score(train_x, train_y)

print(f'최적 하이퍼 파라미터 : {grid_search.best_params_}, 최적 평균 정확도 : {grid_search.best_score_}')

# penalty = 'L2'와 'l1', 규제(오버피팅을 방지)의 릿지와 라쏘
# L2는 페널티를 가하게 되면서 변수의 값이 0에 가까워진다. 
# L1는 0이되는 그런 형태
# C : 규제의 정도를 나타내는 것
# C값이 커지면 규제가 느슨해져 오버피팅이 일어남, 0에 가까워지면 규제가 강해짐
# n_jobs=-1 : CPU를 다 쓴다. 
# cv=3, 교차검증의 약자로, 3-fold


# +
# 최적의 하이퍼 파라미터가 적용된 모델로 값을 예측

model_best = grid_search.best_estimator_
y_pred = model_best.predict(test_x)
y_pred
# -

np.unique(y_pred, return_counts=True)

# ### 2.2.7 로지스틱 회귀 모델 평가

# +
# 회귀모델의 정확도

# from sklearn.metrics import accuracy_score
print(accuracy_score(test_y, y_pred))
roc_auc_score(test_y, y_pred)

# +
# 각 클래스들의 예측된 확률값

from sklearn.metrics import roc_auc_score, roc_curve
y_pred_proba = model_best.predict_proba(test_x)[:, 1] 
y_pred_proba
# -

roc_auc_score(test_y, y_pred)

# +
# ROC 그래프로 AUC값 확인

fpr, tpr, _ = roc_curve(test_y, y_pred_proba)
auc = roc_auc_score(test_y, y_pred)
plt.plot(fpr, tpr, 'r-', label='LogisticRegression')
plt.plot([0, 1], [0, 1], 'b--', label = 'random guess')
plt.xlabel('false positive rate')
plt.ylabel('true positive rate')
plt.title('AUC={0:.2f}'.format(auc))
plt.legend(loc='lower right');
# -

# ![image.png](attachment:image.png)

# +
# 로지스틱 회귀 모형에 대한 평가 보고서

print(classification_report(test_y, y_pred))
# -
# 모델의 성능이 매우 좋지 않으므로 로지스틱 회귀모델이 아닌 다른 방안을 찾아야 한다



