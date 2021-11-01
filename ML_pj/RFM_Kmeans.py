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

# # RFM 기반 Kmeans clustering

# # 배경

# * 사전 정의된 범주가 없는 데이터에서 최적의 그룹을 찾아나가기 위해 k-means 알고리즘을 사용하게 되었다
# * 데이터의 r,f,m 값을 바탕으로 최적의 클러스터링을 하여 도출된 클러스터 값을 원본 데이터에 부여하였다

# # 데이터 로드

# +
# 라이브러리 불러오기

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
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

rfm = pd.read_csv('고객rfm.csv')
rfm.shape
# -

# ---

# # K-Means Clustering

# ## 데이터 차원 변경

# +
# 클러스터가 이해하기 편하도록 차원을 변경

rfm_val = rfm[['Monetary', 'Frequency', 'Recency']].values
rfm_val
# -

# * Random seed 값의 차이에 따른 큰 변화가 없었으므로 random seeds 값은 이 중 300으로 결정

# ## 이상적인 n_cluster 구하기
#
# - KMeans 모델은 n_cluster 지정값에 영향을 받는다. 따라서 가장 이상적인 n_cluster 값을 구하는 것이 군집에 도움이 된다.   

# +
# 필요없는 컬럼인 CustomerID를 삭제 후 데이터프레임 저장

rfm_df = rfm[['Monetary', 'Frequency', 'Recency']]
rfm_df


# -

# ### 엘보우 차트 

# +
def elbow(X):
    sse = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i, init='k-means++', random_state=300, n_init=15)
        km.fit(X)
        sse.append(km.inertia_) # 군집화가 된 후에, 각 중심점에서 군집의 데이타간의 거리를 합산한것이 inertia값. 군집의 응집도를 나타냄. 이 값이 작을수록 잘 응집도 높게 군집되어 있다는 것을 의미.

    plt.figure(figsize=(12, 6))
    plt.title('Rfm Elbow Chart', fontsize=20)
    plt.plot(range(1,11), sse, marker='o')
    plt.xlabel('클러스터 개수')
    plt.ylabel('SSE')
    plt.show()
    
elbow(rfm_val)
# -

# - 3 이후로 평평해지는 모습을 보아 클러스터 3개가 적절하게 보이지만 정확한 클러스터 값을 찾기 위해 실루엣 점수를 확인해볼 필요가 있다.  

# ### 실루엣 점수
# - 처음에는 클러스터를 사용자가 임의로 지정하여 kmeans 군집분석을 진행한다.<br> 가장 이상적인 클러스터 수를 찾기 위해 반복문을 돌렸다.

# +
# 클러스터를 2부터 13까지 돌려가며 실루엣 점수 확인

model = KMeans(
    n_clusters = 2,
    init = 'k-means++',
    n_init = 15,
    random_state=300)

scores = []
clusters_results = {}
for _n_clusters in np.arange(2, 14):
    model.n_clusters = _n_clusters # 모델의 n_cluster를 2~13까지 돌리기
    cluster_results[_n_clusters] = model.fit_predict(rfm_val) # rfm arr를 모델에 훈련하여 각각 클러스터에 해당하는 라벨값을 딕셔너리에 추가
    scores.append(silhouette_score(rfm_val, model.labels_)) # 전체 실루엣 계수 평균값을 score에 추가

# for문을 돌고 나온 score값 시각화
plt.figure(figsize=(12, 6))
plt.title('Rfm Silhouette Score Plot', fontsize=20)
plt.xlabel('# Clusters', fontsize=20)
plt.ylabel('Shilhouette Score', fontsize=20)
plt.plot(np.arange(2, 14), scores, marker='s')
plt.show()
# -

# * 클러스터 2, 3, 4, 5값의 평균 실루엣 점수가 높아보인다.  

# ### n_cluster 값 선택
#
# - 군집별 평균실루엣 계수들의 값이 차이가 많이 나지 않는 군집이 이상적인 n_cluster라고 할 수 있다. 

# +
# 모델 정의

model = KMeans(
    n_clusters = 3, 
    init = 'k-means++',
    n_init = 15, 
    random_state = 300)

# 학습
rfm_df['cluster'] = model.fit_predict(rfm_val)


# rfm의 모든 개별 데이터에 실루엣 계수 값을 구하기
score_samples = silhouette_samples(rfm, rfm_df['cluster'])
# -

score_samples

# rfm_df에 실루엣 계수 컬럼 추가
rfm_df['silhouette_coeff'] = score_samples
rfm_df

rfm_df.groupby('cluster')['silhouette_coeff'].mean()

# - 직관적으로 생각했을때 이상적인 n_cluster=3개의 평균 실루엣 계수들을 구했다. <br>
# 그러나, 나머지 평균실루엣 점수가 높았던 n_cluster=2,3,4들의 평균 실루엣 계수들을 구하고 <br> 분산이 가장 적은 클러스터를 n_cluster 값으로 선택하고자 한다.  

# +
# n_cluster를 2개부터 4개까지 지정시, 군집별 평균 실루엣 계수

model = []
coff_list = []

for p in range(2,5):

    a = KMeans(
        n_clusters = p, 
        init = 'k-means++',
        n_init = 15, 
        random_state = 300)
    model.append(a) # for문을 이용하여 2부터 4까지 n_cluster값 바꿔가며 모델 객체 생성
    
for number in range(0,3):

    rfm_df['cluster'] = model[number].fit_predict(rfm_df) # 도출된 모델 4개를 훈련, 클러스터 라벨값 예측해서 부여
    score_samples = silhouette_samples(rfm, rfm_df['cluster']) # 각각의 실루엣 계수 구하기
    rfm_df['silhouette_coeff'] = score_samples # 실루엣 계수를 따로 컬럼 추가
    k = rfm_df.groupby('cluster')['silhouette_coeff'].mean().values # 각 클러스터의 실루엣 계수 평균값을 구해 coeff_list에 추가
    coff_list.append(k)

coff_list # 각 클러스터별 실루엣 계수 평균값

# +
# 클러스터들의 군집별 평균 실루엣 계수들을 데이터프레임화 

col_name = [0,1,2,3]
list_df = pd.DataFrame(coff_list, columns=col_name).T
list_df = list_df.rename(columns={0:'cluster_2', 1:'cluster_3', 2:'cluster_4'})
list_df

# +
# 클러스터들의 군집별 평균 실루엣 계수들의 분산

list_df.var()
# -

# - 분산이 적은 cluster_4로 결정하였다. 즉, n_cluster값은 4다. 

# +
# 모델 재훈련

model = KMeans(
    n_clusters = 4, 
    init = 'k-means++',
    n_init = 15, 
    random_state = 300)

# 학습
rfm['cluster'] = model.fit_predict(rfm_val)
# -

rfm.head()

# # 군집된 클러스터별 RFM 살펴보기
# * cluster0, cluster1, cluster2, cluster3의 rfm 특징

plt.figure(figsize=(13, 6))
plt.title('군집별 Monetary boxplot', fontsize=20)
sns.boxplot(data=rfm, x='cluster', y='Monetary')

plt.figure(figsize=(13, 6))
plt.title('군집별 Frequency boxplot', fontsize=20)
sns.boxplot(data=rfm, x='cluster', y='Frequency')

plt.figure(figsize=(13, 6))
plt.title('군집별 Recency boxplot', fontsize=20)
sns.boxplot(data=rfm, x='cluster', y='Recency')

# * cluster0: 수익은 조금 떨어지지만 구매빈도가 높고 최신성이 좋은 집단 (신규 우량 고객)
# * cluster1: 수익과 구매빈도가 떨어지고 최신성이 적은 집단 (저수익성 고객)
# * cluster2: 수익이 가장 높고 구매가 빈번하며 최신성이 좋은 집단 (핵심 우량 고객)
# * cluster3: 수익은 떨어지지만 구매빈도가 보통인편이며 최신성이 좋지 않은 집단 (이탈 위험 고객)

# **제안**
# * 이탈 위험 고객에게는 재활성화를 위한 프로모션, 할인 서비스 등이 필요
# * 신규 우량 고객은 자사의 핵심 우량 고객으로 양성하기 위한 노력 -> cross selling 기법으로 고객이 사려는것과 관련된 상품을 추가로 구매하게 만들기
# * 핵심우량고객에게는 프리미엄 서비스 같은 특별한 혜택 고려
# * 저수익성 고객에게는 de-marketing 하는 방향도 고려해보기

# # 도출된 클러스터 값을 바탕으로 원본 데이터 군집 나누기

# +
# 원본 데이터 불러오기

raw = pd.read_csv('전처리완료최종데이터.csv')
raw.head()

# +
# 데이터 merge

complete = pd.merge(raw, rfm, left_on='ID',right_on='CustomerID', how='inner')

# 중복되는 값인 CustomerID 삭제
complete = complete.drop(columns = ['CustomerID'], axis=1)

print(complete.shape)
complete.head()
# -

complete['구매일자'] = pd.to_datetime(complete['구매일자'])
complete.info()

# +
import datetime

complete['구매요일'] = complete['구매일자'].dt.dayofweek
complete.head(5)


# +
def 요일(x):
    if x == 0 :
        return '월'
    elif x == 1 :
        return '화'
    elif x == 2 :
        return '수'
    elif x == 3 :
        return '목'
    elif x == 4 :
        return '금'
    elif x == 5 :
        return '토'
    else :
        return '일'
    
complete['구매요일'] = complete['구매요일'].apply(lambda x: 요일(x))
complete.head()
# -

complete['구매월'] = complete['구매일자'].dt.month
complete['구매일'] = complete['구매일자'].dt.day
complete.head()

# +
# 결측치 확인

complete.isnull().sum()

# +
# 데이터 분할

cluster0 = complete[complete['cluster'] == 0]
cluster1 = complete[complete['cluster'] == 1]
cluster2 = complete[complete['cluster'] == 2]
cluster3 = complete[complete['cluster'] == 3]

cluster0.shape, cluster1.shape, cluster2.shape, cluster3.shape

# +
# # !pip install openpyxl

# +
# 데이터 저장

# cluster0.to_excel('cluster0.xlsx', index=False)
# cluster1.to_excel('cluster1.xlsx', index=False)
# cluster2.to_excel('cluster2.xlsx', index=False)
# cluster3.to_excel('cluster3.xlsx', index=False)

# +
# csv 저장

# cluster0.to_csv('cluster0.csv', index=False)
# cluster1.to_csv('cluster1.csv', index=False)
# cluster2.to_csv('cluster2.csv', index=False)
# cluster3.to_csv('cluster3.csv', index=False)
# -














