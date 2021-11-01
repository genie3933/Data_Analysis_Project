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

# -----------------------------

# # 프로젝트 설명
# * 컨셉 : 신인 걸그룹 데뷔를 앞둔 엔터테인먼트의 ‘전략 신인개발팀‘
# * 목표 : 수집한 멜론 음원 데이터를 기반으로 최적의 신인 걸그룹 데뷔 전략 수립
# * 데이터 셋 소개 : 멜론 시대별 차트 Top 100 국내 종합 데이터 (1984 ~ 2020년)
# * 데이터 수집 방법 : Python의 Selenium, Chrome Web-driver 라이브러리를 이용해 원하는 데이터 셋을 멜론 사이트에서 직접 크롤링하여 수집
# * 컬럼 정의 : 
#     * 연도 
#     * 순위 : 당시 연도에 가장 유행했던 곡들의 순위 
#     * 제목 : 곡 제목 
#     * 가수 : 아티스트 명 (솔로 / 그룹 모두 포함)
#     * 앨범 : 앨범의 이름
#     * 좋아요 수 : 멜론 유저들이 곡에 누른 하트 수
#     * 발매일 : 앨범이 발매된 년, 월, 일
#     * 장르 : 곡의 장르
#     * 가사 : 곡의 가사
#     * 팬수 : 아티스트와 팬 맺기를 한 멜론 유저의 수
#     * 멤버수 : 그룹 아티스트의 경우 멤버의 수 (솔로 아티스트는 1명으로 집계)
#     * 성별 : 아티스트의 성별 (여성 / 남성 / 혼성)
#     * 솔로 / 그룹 : 솔로 / 그룹 여부
#     * 작사 : 곡을 작사한 작사가 이름
#     * 작곡 : 곡을 작곡한 작곡가 이름
#     * 편곡 : 곡을 편곡한 편곡가 이름

# --------------------------------

# # EDA 프로세스
# 1. 멤버 수 전략
# 2. 곡 장르 전략
# 3. 곡 제목 수 분석
# 4. 작사/작곡/편곡 분석
# 5. 가사분석
# 6. 발매일 전략

# 라이브러리 로드
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from wordcloud import WordCloud # 워드클라우드 시각화를 위한 라이브러리 불러오기
from konlpy.tag import Twitter # 가사 속 단어를 추출하기 위한 라이브러리 불러오기
from konlpy.tag import Okt # konlpy 라이브러리의 경우 사전에 설치 필요
from collections import Counter # 단어의 상위 빈도수를 불러오기 위한 라이브러리
import nltk 

# +
# 윈도우일 경우
# plt.rc("font", family = "Malgun Gothic")

# 맥일 경우
plt.rc("font", family = "AppleGothic")

# -

melon_df = pd.read_csv('/Users/cj/Desktop/개인/project/멜론/Realfinal.csv', encoding='utf-8-sig')

melon_df.head(5)

melon_df.tail(5)

melon_df.info()

# -----------------------------

# ## 1. 멤버수 전략
# * 년도 별 그룹의 수 (어떤 년도가 그룹이 많았을까?)
# * 그룹에 해당하는 아티스트의 평균 멤버수는?
# * 남 그룹, 여 그룹 각자 평균 멤버수는?

# 그룹 df
group_df = melon_df[melon_df['솔로/그룹'] == '그룹']

group_df.groupby('연도')['가수'].nunique()

# 그룹수가 가장 많았던 연도 5개
group_df.groupby('연도')['가수'].nunique().sort_values(ascending=False).head()

# 연도별 top100 차트에 있던 가수 중 그룹이었던 가수가 가장 많았던 연도는 2011년, 그 뒤로는 2009년이 뒤를 이었다.

# 시각화
plt.figure(figsize= (33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('연도별 그룹 수 변화', fontsize = 20)
plt.plot(group_df.groupby('연도')['가수'].nunique())
plt.axvline(x = 2011, color = 'r', linestyle = ":")

# 눈에 띄는 년도는 1997, 2011년으로 그래프가 솟은 것을 볼 수 있음. 2011년 이후로는 감소 추세를 보이고 있다.

# 연도별, 성별 그룹 수
year_sex = pd.DataFrame(group_df.groupby(['연도', '성별'])['가수'].nunique())
year_sex = year_sex.rename(columns = {'가수' : '그룹수'})
year_sex

# 시각화
plt.figure(figsize= (33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('연도별 성별 그룹 수 변화', fontsize = 20)
sns.set_palette("bright")
plt.axvline(x=1997, color='r', linestyle='--')
plt.axvline(x=1999, color='r', linestyle='--')
plt.axvline(x=2005, color='r', linestyle='-')
plt.axvline(x=2011, color='r', linestyle='-')
sns.lineplot(data=year_sex, x="연도", y="그룹수", hue="성별")

# 1997~1999년에는 무슨일이...? 혼성 그룹은 남,여 그룹에 비해 저조한 비율
# 남성그룹은 감소, 여성그룹은 증가하는 추세. but 남, 여 그룹 모두 2010년대 초반에 많이 나온 것을 알 수 있다.
# 특히 여성그룹은 2005년 ~ 2010년 사이 가파른 성장세를 보인다.

# 그렇다면 그룹에 해당하는 아티스트의 평균 멤버수는 몇 명일까?

group_df.tail(2)

group_df['멤버수'].mean()

# 그룹에 해당하는 아티스트들의 멤버수는 평균 3.6명

# 연도별 평균 멤버수
year_member = group_df.groupby('연도')['멤버수'].mean()
year_member

year_member.sort_values(ascending=False).head()

# 평균 멤버수가 가장 높았던 년도는 모두 최근 5년 이내의 년도. 그 중에서도 2018년의 차트 순위에 들었던 그룹의 평균 멤버수는 5.7명으로 6명에 가까운 숫자를 보임

# 시각화
plt.figure(figsize= (33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('연도별 평균 멤버 수 변화 추이', fontsize = 20)
plt.plot(group_df.groupby('연도')['멤버수'].mean())

# 전체적으로 봤을 때 그룹의 멤버수는 계속해서 증가하고 있는 추세.

# 성별로 보는 전체년도 평균 멤버수는?

# 남자그룹의 평균 멤버수
male_group = group_df[group_df['성별'] == '남성']
male_group['멤버수'].mean()

# 여자그룹의 평균 멤버수
female_group = group_df[group_df['성별'] == '여성']
female_group['멤버수'].mean()

mixed_group = group_df[group_df['성별'] == '혼성']
mixed_group['멤버수'].mean()

# 전체년도에서는 남그룹 평균 3.3명, 여그룹 평균 4.6명, 혼성그룹 평균 3.2명의 멤버수를 보임

# 앞의 시각화를 통해 그룹이 가장 많았던 2011년을 기준으로 2011년 이전, 2011년 이후의 그룹의 평균 멤버수에는 차이가 있을까?

member_count =  pd.DataFrame(group_df.groupby(['연도', '성별'])['멤버수'].mean())
member_count = member_count.reset_index()
member_count

# 시각화
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title("연도별 성별 평균 멤버수 변화 추이")
sns.set_palette("bright")
sns.lineplot(data=member_count, x='연도', y='멤버수', hue='성별')

# 2011년 이전
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title("2011년 이전 평균 멤버수")
sns.set_palette("bright")
sns.lineplot(data=member_count[member_count['연도'] < 2011], x='연도', y='멤버수', hue='성별')

# 2011년 이후
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title("2011년 이후 평균 멤버수")
sns.set_palette("bright")
sns.lineplot(data=member_count[member_count['연도'] >= 2011], x='연도', y='멤버수', hue='성별')

# 2011년을 기준으로 여성그룹, 남성그룹의 평균 멤버수는 증가추세를 보임. 혼성그룹은 1990년대 초반과 말에만 평균 멤버수의 수가 높았음

# 전체년도에서 여그룹 평균 멤버수는 4.6명, 2011년 이후로는 평균 멤버수가 5명대를 유지하고 있으므로 종합적으로 여그룹의 멤버수는 4명 or 5명을 추천.

# 그렇다면 5명의 멤버수를 넘긴다면?
# 5명의 멤버수를 넘긴 여그룹은 차트에 곡이 몇 개 정도 올랐을까?

# 순위에 오른 4인 이상 여그룹 곡의 총 수(중복 제거)
tot_member_count = female_group[female_group['멤버수'] >= 4]['제목'].nunique()
tot_member_count

# 6명 이상의 멤버수를 가진 여그룹의 순위에 오른 곡 수 (중복 제거)
six_over_member = female_group[female_group['멤버수'] >= 6]['제목'].nunique()
six_over_member

# 4명의 멤버수를 가진 여그룹의 순위에 오른 곡 수 (중복 제거)
four_member = female_group[female_group['멤버수'] == 4]['제목'].nunique()
four_member

# 5명의 멤버수를 가진 여그룹의 순위에 오른 곡 수 (중복 제거)
five_member = female_group[female_group['멤버수'] == 5]['제목'].nunique()
five_member

# 파이차트로 시각화
labels = ['4명', '5명', '6명 이상']
data = [four_member/tot_member_count, five_member/tot_member_count,six_over_member/tot_member_count]
categories= ['4명', '5명', '6명 이상']
explode = [0.02, 0.02, 0.02]
colors = ['#ff9999', '#ffc000', '#8fd9b6']
wedgeprops={'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
plt.figure(figsize=(10, 10))
plt.pie(data, labels=labels, autopct='%.1f%%', explode=explode, wedgeprops=wedgeprops)
plt.title('멤버수 별 순위에 오른 여그룹 곡 수 비율')
plt.show()

# 바 차트 시각화
data_2 = pd.DataFrame({'멤버수' : ['4명', '5명', '6명 이상'],
                       '곡 수' : [111, 53, 71]})
plt.figure(figsize=(33, 10))
plt.title('멤버수 별 순위에 오른 여그룹 곡 수')
sns.set_palette("bright")
sns.barplot(data=data_2, x='멤버수', y='곡 수')

# 5명의 멤버수를 넘겼을 때보다 추천했던 4~5명의 멤버수를 가진 그룹의 순위에 오른 곡 수의 비율이 더 높다.
# * 6명이상: 71곡, 4명: 111곡, 5명: 53곡
# * 전통적으로 여그룹은 4명의 멤버수일 때 차트에 오르는 곡 수가 많았기에 4명을 추천하지만, 최근 트렌드는 평균 5명의 멤버이므로 5명도 고려

# 한 그룹에 곡 수가 편향되었을수도 있으니 그룹별로 몇 곡이 있는지 다시 파이차트로 시각화

# 곡 수가 몇몇 그룹에게 편향된 것은 아닌지 알아보기 위해 파이차트로 시각화
pie_member = pd.DataFrame(female_group[(female_group['가수'] == '이브') | (female_group['가수'] == '핑클 (Fin.K.L)') | (female_group['가수'] == '샤크라') | (female_group['가수'] == '빅마마') | (female_group['가수'] == '쥬얼리') | (female_group['가수'] == '버블 시스터즈') | 
                         (female_group['가수'] == '슈가') | (female_group['가수'] =='브라운아이드걸스') | (female_group['가수'] == '블랙펄') | (female_group['가수'] == '2NE1') | (female_group['가수'] == '미쓰에이') | (female_group['가수'] == '시크릿') | 
                         (female_group['가수'] == '씨스타') | (female_group['가수'] == '걸스데이') | (female_group['가수'] =='써니힐') |  (female_group['가수'] =='마마무 (Mamamoo)') | (female_group['가수'] =='BLACKPINK') |
                         (female_group['가수'] == '환불원정대') | (female_group['가수'] == '베이비복스') | (female_group['가수'] == '원더걸스') | (female_group['가수'] == '4minute') | (female_group['가수'] == '카라') | 
                        (female_group['가수'] == 'f(x)') | (female_group['가수'] =='시크릿') | (female_group['가수'] == '크레용팝') | (female_group['가수'] == '레이디스 코드') | 
                        (female_group['가수'] == 'EXID') | (female_group['가수'] == 'Red Velvet (레드벨벳)') | (female_group['가수'] == 'ITZY (있지)') | 
                         (female_group['가수'] == '소녀시대 (GIRLS\' GENERATION)') | (female_group['가수'] == '티아라, 초신성') | (female_group['가수'] == '애프터스쿨') | (female_group['가수'] == '티아라') | 
                         (female_group['가수'] == '레인보우') | (female_group['가수'] =='달샤벳') | (female_group['가수'] == 'F-ve Dolls') | (female_group['가수'] == 'Apink (에이핑크)') | 
                         (female_group['가수'] == 'AOA') | (female_group['가수'] == '여자친구 (GFRIEND)') | (female_group['가수'] == 'TWICE (트와이스)') | (female_group['가수'] == '아이오아이 (I.O.I)') | 
                         (female_group['가수'] == '러블리즈') |(female_group['가수'] == '언니쓰') | (female_group['가수'] == '모모랜드 (MOMOLAND)') | (female_group['가수'] == '(여자)아이들') |  
                         (female_group['가수'] == '오마이걸 (OH MY GIRL)') | (female_group['가수'] == 'IZ*ONE (아이즈원)')].groupby('가수')['제목'].nunique().sort_values(ascending=False))
pie_member = pie_member.rename(columns={'제목' : '곡 수'})

pie_member.plot.pie(y='곡 수', figsize = (20, 20), legend = False, autopct = "%.1f%%")

# 2NE1의 곡 수 비율이 가장 높긴 하지만 그룹별로 심한 편향을 보이지는 않음.

# 결론적으로 그룹의 멤버수는 4명(전통적인 멤버수) or 5명(최근 트렌드)으로 하는 것이 적당하다

# ---------------------------------

# ## 2. 곡 장르 전략
# * 최근 30년간 장르 트렌드 변화
# * 연도별 가장 인기있는 장르는?
# * 그룹의 성별에 따라 인기있는 장르가 다를까?
# * 솔로 아티스트의 인기 장르는?
# * 연도별 좋아요 수가 많은 장르는?
# * 연대별 1위를 가장 많이 차지한 장르는?

# ### 장르 트렌드 변화

# 최근 30년간 가장 인기있었던 장르 top10
top_genre = pd.DataFrame(melon_df.groupby('장르')['제목'].count().sort_values(ascending=False)).reset_index().head(10)
top_genre = top_genre.rename(columns = {'제목' : '곡 수'})
top_genre

# +
# 최근 30년간 장르 트렌드의 변화
# 연도별 트렌드 장르
year_trend = pd.DataFrame(melon_df.groupby(['연도','장르'])['제목'].count()).reset_index().rename(columns = {'제목' : '곡 수'})


# 연도별 곡 수가 가장 많은 장르만 출력
idx = year_trend.groupby(['연도'])['곡 수'].transform(max) == year_trend['곡 수']
year_trend[idx]
# -

# '발라드' 장르가 예전부터 꾸준히 top100 차트에 머무는 것을 발견. 눈여겨볼만한 점은 2000년대에는 발라드가 유행하다가 2010년에 와서는 '댄스' 장르가 인기가 있었던것으로 나타났다. 아마 2세대 아이돌(빅뱅, 투애니원, 소녀시대, 샤이니 등등...)의 등장이 영향을 미치지 않았을까 생각이 든다. 그러나 최근(2019년)부터는 다시 발라드곡이 top100차트에 많이 올라온 것을 볼 수 있다.

# ### 그룹이 많이 시도했던 장르는?
# * 여그룹이 많이 시도한 장르, 남그룹이 많이 시도한 장르
# * 그룹의 성별에 따라 인기있는 장르가 다른가?

# 여그룹의 인기있는 장르 top10
female_group_trend = pd.DataFrame(female_group.groupby('장르')['제목'].count()).rename(columns = {'제목' : '곡 수'}).reset_index().sort_values(by = '곡 수', ascending=False).head(10)
female_group_trend

# 시각화
plt.figure(figsize=(33, 10))
plt.title('여그룹 인기 장르')
plt.xticks(rotation = 30)
sns.set_palette("bright")
sns.barplot(data=female_group_trend, x='장르', y='곡 수')

# 남그룹의 인기있는 장르 top10
male_group_trend = pd.DataFrame(male_group.groupby('장르')['제목'].count()).rename(columns = {'제목' : '곡 수'}).reset_index().sort_values(by = '곡 수', ascending=False).head(10)
male_group_trend

# 시각화
plt.figure(figsize=(33, 10))
plt.title('남그룹 인기 장르')
plt.xticks(rotation = 30)
sns.set_palette("bright")
sns.barplot(data=male_group_trend, x='장르', y='곡 수')

# 여그룹, 남그룹 인기있는 장르가 다른 것을 알 수 있다.
# 여그룹은 댄스 장르가 압도적으로 많은 반면 남그룹은 발라드, 댄스 장르의 차이가 크지 않으며 여그룹보다 비교적으로 다양한 장르의 곡이 순위에 오른 것을 볼 수 있다.

# 남, 여그룹 모두 인기가 있는 장르는 '댄스'이며 만약 여그룹을 데뷔시킨다면 '댄스' 장르의 곡으로 데뷔를 시키는 것이 유리할 것으로 예상된다.

# ### 좋아요 수와 장르
# * 종합적으로 좋아요 수가 가장 많은 장르 top10
# * 연도별 좋아요 수가 가장 많은 장르
# * 여그룹 곡 중 좋아요 수가 많은 장르

# 전체년도에서 좋아요 수가 많은 장르 top 10
likes_sum = pd.DataFrame(melon_df.groupby('장르')['좋아요 수'].sum().sort_values(ascending=False).reset_index().head(10))
likes_sum

# 좋아요 수 시각화
plt.figure(figsize = (33, 10))
plt.ticklabel_format(style='plain') # 숫자 평평하게
plt.xticks(rotation = 30)
plt.title('총 좋아요 수 top10 장르')
sns.set_palette("bright")
sns.barplot(data=likes_sum, x='장르', y='좋아요 수')

# +
# 연도별 총 좋아요 수가 가장 많은 장르만 출력
year_like_cnt = pd.DataFrame(melon_df.groupby(['연도','장르'])['좋아요 수'].sum()).reset_index().rename(columns = {'제목' : '곡 수'})

idx = year_like_cnt.groupby(['연도'])['좋아요 수'].transform(max) == year_like_cnt['좋아요 수']
year_like_cnt[idx]
# -

# 대부분의 연도에서 총 좋아요 수 역시 '발라드' 장르가 강세를 보였지만 가장 최근인 2020년 top 100 차트에서는 '댄스' 장르의 총 좋아요 수가 가장 많은 것을 알 수 있다. 아무래도 아이돌 그룹 팬의 특성상 음원 총공 같은 충성심이 총 좋아요 수에 영향을 미치지 않았나 싶다.

# +
# 솔로/그룹 여부와 좋아요 수의 상관관계 (범주형변수, 수치형변수 간의 상관분석)

# '음원총공'이라는 문화가 생겼던 2014년 이후의 데이터들만 가지고 상관분석 진행

melon_df_after = melon_df[melon_df['연도'] >= 2014]

# +
# 솔로/그룹 여부는 범주형 변수이므로 더미변수로 변경한 후 상관분석을 진행해주어야 함
# 그룹이면 0, 솔로면 1로 변경
melon_df_after_dummies = pd.get_dummies(melon_df_after['솔로/그룹'])

# del melon_df_after_dummies[melon_df_after_dummies.columns[0]]
melon_df_after_new = pd.concat([melon_df_after, melon_df_after_dummies], axis=1)

# +
from scipy import stats

# 그룹과 좋아요 수 간의 피어슨 상관관계 (상관계수, p값 순)
stats.pearsonr(melon_df_after_new['그룹'], melon_df_after_new['좋아요 수'])
# -

# 그룹과 좋아요 수 간에는 거의 상관관계가 없었다.

# 팬수과 좋아요 수 간의 피어슨 상관관계 (상관계수, p값 순)
stats.pearsonr(melon_df_after_new['팬수'], melon_df_after_new['좋아요 수'])

# 양의 상관관계를 확인하기 위해 lmplot으로 시각화
sns.set_palette("bright")
sns.lmplot(data=melon_df_after_new, x='팬수', y='좋아요 수', height=10, aspect=1.5)

# 솔로/그룹 여부보다는 팬 수와 좋아요 수간의 상관관계가 강하지는 않아도 있는 것으로 나타났다. 팬수가 많을 수록 좋아요 수도 많은 '양의 상관관계'를 보인다.
# 결국 그룹이든 솔로든 팬 수가 많아야 음원이 잘 될 가능성이 높다.

# 이것을 이용하여 음원사이트의 '팬 맺기'를 한 후 sns에 인증을 하면 포토카드나 CD를 보내주는 이벤트를 열어 팬의 유입을 늘리는 방안도 생각해보면 좋을 것 같다. (음원이 잘 되려면 우선 팬을 모아야 하기 때문)

# ### 순위와 장르
# * 전체년도에서 1위를 가장 많이 차지한 장르
# * 최근 10년간 1위를 가장 많이 차지한 장르
# * 여그룹 곡 중 1위를 가장 많이 차지한 장르 
# * 솔로가수의 곡 중 1위를 가장 많이 차지한 장르

# +
# 1위한 곡만 추출 
top_of_top = melon_df[melon_df['순위'] == 1]


# 전체년도에서 1위를 가장 많이 차지한 장르
top_of_top['장르'].value_counts()
# -

# 전체년도에서 1위를 가장 많이 차지한 장르는 '발라드' 다음이 '댄스' 장르

top_of_top[(top_of_top['연도'] >= 2010) & (top_of_top['연도'] <= 2020)]

# 최근 10년간 시대별 차트에서 1위를 가장 많이 차지한 장르는 '랩/힙합', '댄스' 장르

# 예전에 인기있었던 발라드, 요즘 인기 있는 장르인 댄스, 랩/힙합 장르만 모아 시대별로 어떻게 변화했는지 보기
genre_trend_change = year_trend[(year_trend['장르'] == '발라드') | (year_trend['장르'] == '댄스') | (year_trend['장르'] == '랩/힙합')]
genre_trend_change

# 시각화
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title("연도별 인기 장르 트렌드 변화")
sns.set_palette("bright")
sns.lineplot(data=genre_trend_change, x='연도', y='곡 수', hue='장르')

# 사재기가 의심되는 2019년을 제외하면 최근 10년간은 확실히 '발라드' 보다는 '댄스' 장르가 인기있는 것을 확인. 랩/힙합은 최근 들어서 상승하는 추세.

# 전체년도에서 여그룹 곡 중 시대별 차트에서 1위를 차지한 장르
top_of_top[(top_of_top['성별'] == '여성') & (top_of_top['솔로/그룹'] == '그룹')]['장르'].value_counts()

top_of_top[(top_of_top['성별'] == '여성') & (top_of_top['솔로/그룹'] == '그룹')]

# 여그룹 중 시대별 1위를 한 곡의 장르는 '댄스'가 대부분.
# 시대별로 top100 차트를 세웠을 때, 1위를 한 여그룹은 '빅마마, 원더걸스, 소녀시대, 미쓰에이, 티아라, 트와이스'로 6팀밖에 없다. 그중에서도 최근 10년간 시대별 top100 차트에서 1위를 한 여그룹은 '미쓰에이, 티아라, 트와이스' 뿐이며 이 세 그룹 모두 '댄스' 장르의 곡으로 1위를 차지했다.

# 그러므로 여그룹을 데뷔 시킬 때는 '댄스' 장르가 유리할 것으로 예상된다.

# ------------------------------------------

# ## 3. 곡 제목 수 분석
# * 시대별 곡 제목 수의 변화가 있는가?
# * 최근 10년간 차트에 오른 곡들의 평균 곡 제목 수
# * 곡 제목 수도 순위와 상관이 있을까? (상관분석)

# ### 시대별 차트에서의 곡 제목 수의 변화

# 곡 제목수 컬럼 추가
melon_df['곡제목수'] = melon_df['제목'].str.replace(' ', '').str.len()

# 추가된 컬럼 확인
melon_df.tail(1)

# 시대별 차트의 평균 곡 제목 수 변화
title_len_count = pd.DataFrame(melon_df.groupby('연도')['곡제목수'].mean().reset_index())

# 시각화
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('연도별 평균 곡 제목수 변화')
sns.set_palette("bright")
sns.lineplot(data=title_len_count, x='연도', y='곡제목수')

# 90년대에 잠깐 높았다가 오르락 내리락을 반복. 하지만 최근 들어 곡 제목수가 늘어난 모습을 볼 수 있다.

# ### 그렇다면 평균 곡 제목 수인 6글자를 넘는 곡의 수가 시대별로 차이가 있을까?
# * 시대별 곡 제목 6글자 이상인 곡 수

year_title_len_count = pd.DataFrame(melon_df[melon_df['곡제목수'] >= 6].groupby('연도')['제목'].nunique().reset_index())


# 연도를 년대로 나눠주는 함수
def split_by_time(x):
    if x <= 1989:
        return "1980년대"
    elif x <= 1999:
        return "1990년대"
    elif x <= 2009:
        return "2000년대"
    elif x <= 2019:
        return "2010년대"
    else:
        return "2020년대"


# 함수 적용해서 새 컬럼 만들기
year_title_len_count['년대'] = year_title_len_count['연도'].apply(lambda x: split_by_time(x))

# 년대별 곡 제목이 6글자 이상인 총 곡 수
six_len = pd.DataFrame(year_title_len_count.groupby('년대')['제목'].sum().reset_index())
six_len = six_len.rename(columns = {'제목' : '6글자 이상인 곡 수'})

six_len

# 시각화
plt.figure(figsize=(33, 10))
plt.title('연대별 6글자 이상인 곡 수')
sns.set_palette("bright")
sns.barplot(data=six_len, x='년대', y='6글자 이상인 곡 수')

# 전체년도 평균 곡 제목 수였던 6글자를 넘은 곡의 수는 top100 차트 안의 곡에서는 1990년대가 가장 많은 것으로 나타났다.

# ### 최근 10년간 차트에 오른 곡들의 평균 곡 제목 수

recently_title_len_count = pd.DataFrame(melon_df[(melon_df['연도'] >= 2010) & (melon_df['연도'] <= 2020)].groupby('연도')['곡제목수'].mean().reset_index())

recently_title_len_count

# 시각화
plt.figure(figsize=(33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('최근 10년간 차트에 오른 곡들의 평균 곡 제목 수')
sns.set_palette("bright")
sns.barplot(data=recently_title_len_count, x='연도', y='곡제목수')

# * 최근 10년간 차트에 오른 곡들을 살펴보면 2010년대는 오히려 곡 제목수가 짧은게 트렌드였음을 확인 할 수 있다. 
# * 뒷받침하는 기사: https://news.sbs.co.kr/news/endPage.do?news_id=N1002417879
# * 최근에서야 다시 곡 제목수가 길어지는 추세이다.

# 여성 댄스 그룹
female_dance_group = melon_df[(melon_df['성별'] == '여성') & (melon_df['솔로/그룹'] == '그룹') & (melon_df['장르'] == '댄스')]

# 여성 댄스 그룹이 전체 평균 곡 제목 수
female_dance_group['곡제목수'].mean()

# 여성 댄스 그룹의 연도별 평균 곡 제목 수
pd.DataFrame(female_dance_group.groupby('연도')['곡제목수'].mean().reset_index())

# +
# 평균으로만 보는 것은 오류가 있을 수 있으므로 boxplot으로도 시각화

plt.figure(figsize=(33, 10))
plt.xticks(rotation = 30)
plt.title('연도별 여성 댄스 그룹의 곡 제목 수 boxplot')
sns.boxplot(data=female_dance_group, x='연도', y='곡제목수')
# -

# 최근 10년으로 시각화
plt.figure(figsize=(33, 10))
plt.xticks(rotation = 30)
plt.title('최근 10년 여성 댄스 그룹의 곡 제목 수 boxplot')
sns.boxplot(data=female_dance_group[female_dance_group['연도'] >= 2010], x='연도', y='곡제목수')

# 전체년도 곡 제목 평균과 비슷하게 확실히 최근으로 갈수록 곡 제목수의 범위가 넓어지고 있다.

# ### 곡 제목 수도 순위와 상관이 있을까?

corr = melon_df.corr()

plt.figure(figsize = (33,10))
sns.set_palette("bright")
sns.heatmap(corr, annot=True, cmap='Blues')

# 곡 제목 수가 연도별로 다르지만 이것이 순위와 상관은 없는것으로 보인다. 결국 순위를 의식해서 곡 제목 수가 늘어났다기 보다는 사회적인 유행이 곡 제목 수에 영향을 준 것으로 추측된다.

# -------------------------------------

# ## 4. 작사/작곡/편곡 분석
# * 종합차트에서 인기있는 작사/작곡/편곡가 (가장 핫한 작사/작곡/편곡가는 누구?)
# * 여자아이돌 곡을 담당하는 작사/작곡/편곡가
# * 좋아요 수와 작사/작곡/편곡가

# ### 종합차트에서 인기있는 작사/작곡/편곡가 (가장 핫한 작사/작곡/편곡가는 누구?)
# * 최근 10년간 차트에 오른 빈도수가 높은 작사/작곡/편곡가 top20
# * 1위를 등극시킨 빈도가 높은 작사/작곡/편곡가는?

# 데이터 다시 로드
df = pd.read_csv('/Users/cj/Desktop/개인/project/멜론/Realfinal.csv', encoding='utf-8-sig')
df.shape

# 시대별 최근 10년간 차트에 오른 빈도수가 높은 작사/작곡/편곡가 top20
# 최근10년 작사가의 빈도수
dfdf = df[(df["연도"]>= 2011) & (df["연도"]<=2020)]["작사"].value_counts().drop('Nan').to_frame().reset_index().rename(columns={"index" : "작사가","작사":"작사수"}).head(20)
# 최근10년 작곡가의 빈도수
dfdf2 = df[(df["연도"]>= 2011) & (df["연도"]<=2020)]["작곡"].value_counts().drop('Nan').to_frame().reset_index().rename(columns={"index" : "작곡가","작곡":"작곡수"}).head(20)
# 최근10년 편곡가의 빈도수
dfdf3 = df[(df["연도"]>= 2011) & (df["연도"]<=2020)]["편곡"].value_counts().drop('Nan').to_frame().reset_index().rename(columns={"index" : "편곡가","편곡":"편곡수"}).head(20)

# 시각화
plt.figure(figsize=(33,10))
plt.xticks(rotation = 40 )
plt.title("최근 10년간 히트곡을 낸 작사가 20명")
sns.barplot(x="작사가", y="작사수", data=dfdf)

plt.figure(figsize=(33,10))
plt.xticks(rotation = 40 )
plt.title("최근 10년간 히트곡을 낸 작곡가 20명")
sns.barplot(x="작곡가", y="작곡수", data=dfdf2)

plt.figure(figsize=(33,10))
plt.xticks(rotation = 40 )
plt.title("최근 10년간 히트곡을 낸 편곡가 20명")
sns.barplot(x="편곡가", y="편곡수", data=dfdf3)

# * 멜론 TOP100의 최근10년(2011년 ~ 2020년)데이터에서 가장 많은 성과를 낸 작업자들의 빈도수가 위와 같이 보여지고 있다.

# 1위를 등극시킨 빈도가 많은 작사/작곡/편곡가는?
a = df[df["순위"] == 1][["작사","연도"]].value_counts().to_frame().reset_index()
b = df[df["순위"] == 1][["작곡","연도"]].value_counts().to_frame().reset_index()
c= df[df["순위"] == 1][["편곡","연도"]].value_counts().to_frame().reset_index()

# 1위를 등극시킨 작사가의 빈도
a

# 1위를 등극시킨 작곡가의 빈도
b

# 1위를 등극시킨 편곡가의 빈도
c

# ### 여자아이돌 곡을 담당하는 작사/작곡/편곡가
# * 여자댄스그룹에서 좋은 성과를 내었던 작사/작곡/편곡가는 어떠한 사람들이 있을까?
# * 연도별 여자댄스그룹의 곡을 작업한 사람들의 추이는 어떠할까?
# * 여자댄스그룹의 1위등극시킨 빈도가 잦은 작업자들은 어떠한 사람들이 있을까?
# * 이 그룹이 해당 작사/작곡/편곡가가 아닌 다른 작업자와 협업했을 때의 순위는?
# *1. 좋은시너지로 꾸준한 성과를 내고있던 트와이스가 블랙아이드필승 작업자와 작업유무에 따른 순위비교, 
# *2. 좋은시너지로 꾸준한 성과를 내고있던 마마무가 김도훈 작업자와 작업유무에 따른 순위비교

# 여자댄스그룹 에서 인기 있는 작사/작곡/편곡가는?
a1 = df[(df["성별"] == "여성") & (df["솔로/그룹"]=="그룹") & (df["장르"] == "댄스")]["작사"].value_counts().drop("Nan").head(10).to_frame().reset_index().rename(columns={"index":"작사가","작사":"빈도수"})
b1 = df[(df["성별"] == "여성") & (df["솔로/그룹"]=="그룹") & (df["장르"] == "댄스")]["작곡"].value_counts().drop("Nan").head(10).to_frame().reset_index().rename(columns={"index":"작곡가","작곡":"빈도수"})
c1 = df[(df["성별"] == "여성") & (df["솔로/그룹"]=="그룹") & (df["장르"] == "댄스")]["편곡"].value_counts().drop("Nan").head(10).to_frame().reset_index().rename(columns={"index":"편곡가","편곡":"빈도수"})

# +
# 시각화
ratio = a1["빈도수"]
labels = a1["작사가"]

plt.figure(figsize=(10,10))
plt.pie(ratio, labels=labels, autopct='%.1f%%')
plt.title('여성댄스그룹에서 히트곡을 많이 낸 작사가')
plt.show()

# +
ratio1 = b1["빈도수"]
labels1 = b1["작곡가"]

plt.figure(figsize=(10,10))
plt.pie(ratio1, labels=labels1, autopct='%.1f%%')
plt.title('여성댄스그룹에서 히트곡을 많이 낸 작곡가')
plt.show()

# +
ratio2 = c1["빈도수"]
labels2 = c1["편곡가"]

plt.figure(figsize=(10,10))
plt.pie(ratio2, labels=labels2, autopct='%.1f%%')
plt.title('여성댄스그룹에서 히트곡을 많이 낸 편곡가')
plt.show()
# -

# * 작사가
#     * 1위 박진영 2위 용감한형제 3위 TEDDY
# * 작곡가
#     * 1위 박진영 2위 용감한형제 3위 블랙아이드필승
# * 편곡가
#     * 1위 신사동호랭이 2위 라도 3위 용감한형제
# * 위의 3개 차트를 기반으로 협업자들을 선정한다면 신인 그룹의 첫 기반을 다지는데에 큰 도움이 될 수 있을 것 같다.

# +
# 여자그룹의 댄스곡을 작사/작곡/편곡했던 사람 중 시대별로 인기있었던 작사/작곡/편곡가 (차트에 곡이 많은것이 인기의 기준)
a = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스")].groupby("연도")["작사"].value_counts()
b = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스")].groupby("연도")["작곡"].value_counts()
c = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스")].groupby("연도")["편곡"].value_counts()

a = a.to_frame().rename(columns={"작사":"작사수"}).reset_index()
a = a[a["작사"] != 'Nan']
a = a.groupby("연도").sum()

b = b.to_frame().rename(columns={"작곡":"작곡수"}).reset_index()
b = b[b["작곡"] != 'Nan']
b = b.groupby("연도").sum()

c = c.to_frame().rename(columns={"편곡":"편곡수"}).reset_index()
c = c[c["편곡"] != 'Nan']
c = c.groupby("연도").sum()

# 시각화
fig = plt.figure(figsize=(33,10)) ## 캔버스 생성

fig.set_facecolor('white') ## 캔버스 색상 설정
ax = fig.add_subplot() ## 그림 뼈대(프레임) 생성

ax.plot(a,label='작사가') ## 선그래프 생성
ax.plot(b,label='작곡가') 
ax.plot(c,label='편곡가') 

ax.legend() ## 범례
plt.title('여자그룹가수의 작사/작곡/편곡가의 시대별 증가추이',fontsize=20) ## 타이틀 설정
plt.show()
# -

# * 작사가 / 작곡가의 데이터가 동일하여 선차트가 겹쳐져 작사가가 차트에 표기되지 않음
# * 1984년 ~ 2020년 기간동안 여자댄스그룹의 작사/작곡/편곡가의 인원수 추세가 나타나있다. 2007년부로 급상승추세가 보여지고 있고 여자댄스그룹 붐이 일어났을 것으로 보여지고 2013년에 조금씩 하락하며 열기가 식고 있는것으로 나타타진다.

# 여자댄스그룹 중 1위를 많이 차지한 작사/작곡/편곡가는?
temp = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["순위"] == 1) & (df["장르"] == "댄스")]["작사"].value_counts()
temp = temp.to_frame().reset_index().rename(columns={"index" :"작사가"})
temp2 = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["순위"] == 1) & (df["장르"] == "댄스")]["작곡"].value_counts()
temp2 = temp2.to_frame().reset_index().rename(columns={"index" :"작곡가"})
temp3 = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["순위"] == 1) & (df["장르"] == "댄스")]["편곡"].value_counts()
temp3 = temp3.to_frame().reset_index().rename(columns={"index" :"편곡가"})

# 시각화
temp.plot(kind = "bar",x="작사가",y="작사",color="r")
plt.title("여자그룹댄스중 1위를 많이 차지한 작사가")
plt.xticks(rotation=45)
plt.show()

temp2.plot(kind = "bar",x="작곡가",y="작곡")
plt.title("여자그룹댄스중 1위를 많이 차지한 작곡가")
plt.xticks(rotation=45)
plt.show()

temp3.plot(kind = "bar",x="편곡가",y="편곡",color="g")
plt.title("여자그룹댄스중 1위를 많이 차지한 편곡가")
plt.xticks(rotation=45)
plt.show()

# * 여자댄스그룹을 가장 많이 1위로 등극시킨 사람들로는 다음과 같은 작업자들이 보여지고 있다.

# 여그룹의 곡 중 '댄스' 장르를 작사/작곡/편곡했던 사람 중 시대별 or 최근 10년간 인기있었던 작사/작곡/편곡가
q = df[(df["성별"] =="여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["연도"] >= 2011) & (df["연도"] <= 2020)][["연도","작사"]]
w = df[(df["성별"] =="여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["연도"] >= 2011) & (df["연도"] <= 2020)][["연도","작곡"]]
e = df[(df["성별"] =="여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["연도"] >= 2011) & (df["연도"] <= 2020)][["연도","편곡"]]
q = q[q["작사"] != "Nan"]
w = w[w["작곡"] != "Nan"]
e = e[e["편곡"] != "Nan"]
q = q.value_counts().to_frame().sort_values("연도").rename(columns={0: "횟수"})
w = w.value_counts().to_frame().sort_values("연도").rename(columns={0: "횟수"})
e = e.value_counts().to_frame().sort_values("연도").rename(columns={0: "횟수"})

# 최근 10년간 여성댄스그룹 작사가
q

# 최근 10년간 여성댄스그룹 작곡가
w

# 최근 10년간 여성댄스그룹 편곡가
e

# * 최근 10년(2011 ~ 2020) 여자댄스그룹의 작업자들의 빈도수 차이는 크게 나타나지 않는 것으로 보여진다.

# +
# 이 그룹이 해당 작사/작곡/편곡가가 아닌 다른 작곡가와 협업했을 때의 순위는?
# 특정 가수들과의 시너지로 좋은 성과를 내었던 트와이스가 블랙아이드필승 작업자와 협업유무에 따른 순위,
# 마마무가 김도훈 작업자와 협업하지 않았을 때의 순위 등

a = df[(df["가수"] == "TWICE (트와이스)") & (df["작사"].str.contains("블랙아이드필승"))][["작사","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작사순위"}).drop(0,axis=1)
b = df[(df["가수"] == "TWICE (트와이스)") & (df["작곡"].str.contains("블랙아이드필승"))][["작곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작곡순위"}).drop(0,axis=1)
c = df[(df["가수"] == "TWICE (트와이스)") & (df["편곡"].str.contains("블랙아이드필승"))][["편곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"편곡순위"}).drop(0,axis=1)
nota = df[(df["가수"] == "TWICE (트와이스)") & (~df["작사"].str.contains("블랙아이드필승"))][["작사","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작사순위"}).drop(0,axis=1)
notb = df[(df["가수"] == "TWICE (트와이스)") & (~df["작곡"].str.contains("블랙아이드필승"))][["작곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작곡순위2"}).drop(0,axis=1)
notc = df[(df["가수"] == "TWICE (트와이스)") & (~df["편곡"].str.contains("블랙아이드필승"))][["편곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"편곡순위"}).drop(0,axis=1)


d = df[(df["가수"] == "마마무 (Mamamoo)") & (df["작사"].str.contains("김도훈"))][["작사","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작사순위"}).drop(0,axis=1)
e = df[(df["가수"] == "마마무 (Mamamoo)") & (df["작곡"].str.contains("김도훈"))][["작곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작곡순위"}).drop(0,axis=1)
f = df[(df["가수"] == "마마무 (Mamamoo)") & (df["편곡"].str.contains("김도훈"))][["편곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"편곡순위"}).drop(0,axis=1)
notd = df[(df["가수"] == "마마무 (Mamamoo)") & (~df["작사"].str.contains("김도훈"))][["작사","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작사순위"}).drop(0,axis=1)
note = df[(df["가수"] == "마마무 (Mamamoo)") & (~df["작곡"].str.contains("김도훈"))][["작곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"작곡순위2"}).drop(0,axis=1)
notf = df[(df["가수"] == "마마무 (Mamamoo)") & (~df["편곡"].str.contains("김도훈"))][["편곡","순위"]].value_counts().to_frame().reset_index().rename(columns={"순위":"편곡순위"}).drop(0,axis=1)

# +
# 전처리 테스트
# abc = pd.concat([b,notb],axis=1)
# abc2 = pd.concat([f,notf],axis=1)
# abc2
# -

# 시각화
ax = abc.plot(kind='bar', title='트와이스가 블랙아이드필승 작곡가와의 협업유무에따른 순위비교', figsize=(33, 10), legend=True, fontsize=15)
ax.set_xlabel('작곡가', fontsize=15)          # x축 정보 표시
ax.set_ylabel('순위', fontsize=15)     # y축 정보 표시
ax.legend(['블랙아이드필승', '블랙아이드필승 외 작곡가'], fontsize=15)    # 범례 지정

# * 트와이스의 TOP100에 올랐던 노래중 시너지가 좋은 블랙아이드필승과 작업하였을때의 곡순위와 그외의 작업자들의과 작업하였을때의 곡순위를 비교해 보았다. 블랙아이드필승과 작업한 곡의 순위가 그렇지 않을때보다 상대적으로 높은것으로 보여지고 있다. (차트의 높이가 낮을수록 순위가 높음)

# +
ratio = [f["편곡"].shape[0],notf["편곡"].shape[0]]
labels = ["김도훈편곡가와협업","김도훈외편곡가와협업"]

plt.figure(figsize=(10,10))
plt.pie(ratio, labels=labels, autopct='%.1f%%')
plt.show()
# -

# * 멜론 TOP100에 오른 마마무의 곡들중 시너지가 좋은 김도훈 작업자와의 곡과 그외의 작업자들과의 곡의 점유율을 나타내는 차트이다.
# * 시너지가 좋은 작업자와 함께 하였을 때 TOP100의 점유율이 3.5배 더 높은것으로 나타나고 있다.

# 블랙아이드필승과 트와이스, 김도훈 프로듀서와 마마무는 좋은 시너지를 내는 협업 파트너이다. 트와이스는 블랙아이드필승과 작업하였을 때의 곡 순위가 그렇지 않을 때보다 상대적으로 더 좋은 성과가 나타났으며, 마마무 역시 좋은 파트너인 김도훈 프로듀서와 작업하였을 때가 훨씬 더 높은 비율로 좋은 성과를 내었다.

# 결과적으로 데뷔할 신인 걸그룹 역시 지속적으로 이러한 시너지를 낼 수 있는 협업자들을 선정해 작업을 한다면 좋은 성과를 낼 수 있을 것이다.

# ### 좋아요 수와 작사/작곡/편곡가
# * 최근 10년동안 (2011년 ~ 2020년) 좋아요 수가 많은(10만개이상) 곡의 작사/작곡/편곡가는 어떠한 사람들이 있을까?
# * 여자댄스그룹 장르의 좋아요 수가 많은 노래의 작사/작곡/편곡가는 누구?

# 최근 10년 (2011년 ~ 2020년) 동안 좋아요수를 많이 받은 작업자들은 어떠한 사람들이 있을까?
# 좋아요 수가 많은 기준은 10만개 이상
new = df[(df["연도"] >= 2011) & (df["연도"] <= 2020) & (df["좋아요 수"] >= 100000)][["연도","작사","작곡","편곡"]]
new

# * 가수의 곡 좋아요 수가 10만개 이상인 작업자들을 탐색해 보았다.

# 여그룹의 '댄스' 장르의 좋아요 수를 많이 획득하게 해준 작사/작곡/편곡가는 누구? (상위 10명)
a = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["좋아요 수"] >= 100000)]["작사"].value_counts().to_frame().reset_index().rename(columns={"index":"작사가명","작사":"횟수"}).head(10)
b = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["좋아요 수"] >= 100000)]["작곡"].value_counts().to_frame().reset_index().rename(columns={"index":"작곡가명","작곡":"횟수"}).head(10)#.rename("index":"작곡가명","작곡":"횟수")
c = df[(df["성별"] == "여성") & (df["솔로/그룹"] == "그룹") & (df["장르"] == "댄스") & (df["좋아요 수"] >= 100000)]["편곡"].value_counts().to_frame().reset_index().rename(columns={"index":"편곡가명","편곡":"횟수"}).head(10)#.rename("index":"편곡가명","편곡":"횟수")

# 여자댄스그룹의 좋아요 10만개 이상의 빈도수가 높은 작사가 상위 10명
a

# 여자댄스그룹의 좋아요 10만개 이상의 빈도수가 높은 작곡가 상위 10명
b

# 빈도수가 높은 편곡가 상위 10명
c

# +
ratio = a["횟수"]
labels = a["작사가명"]

plt.figure(figsize=(10,10))
plt.rc('xtick', labelsize=20)
plt.pie(ratio, labels=labels, autopct='%.1f%%')
plt.title('좋아요수를 많이 획득한 작사가')
plt.show()

# +
ratio = b["횟수"]
labels = b["작곡가명"]

plt.figure(figsize=(10,10))
plt.rc('xtick', labelsize=20)
plt.pie(ratio, labels=labels, autopct='%.1f%%')
plt.title('좋아요수를 많이 획득한 작곡가')
plt.show()

# +
ratio = c["횟수"]
labels = c["편곡가명"]

plt.figure(figsize=(10,10))
plt.rc('xtick', labelsize=20)
plt.pie(ratio, labels=labels, autopct='%.1f%%')
plt.title('좋아요수를 많이 획득한 편곡가')
plt.show()
# -

# 상위 10명의 작사 / 작곡 / 편곡가를 분석 해본 결과,
#
# 작사가에서는 KENZIE, 박진영, 임수호&용배(RBW)
#
# 작곡가에서는 임수호&용배(RBW), 블랙아이드필승 전군, 박진영 
#
# 편곡가에는 라도, 신사동호랭이, 임수호&용배(RBW)
#
# 위의 프로듀서들이 작사 / 작곡 / 편곡에서 좋아요 순 Top3 로 나타났다.

# 그러므로 위의 Top 3 프로듀서들과 작업을 한다면 차후 팬층확보와 적극적인 지지를 얻을 수 있을 것이라 예상이 된다.

# + active=""
#
# -

# ### 작사 / 작곡 / 편곡 분석 결론
# >우선순위 선정 기준 (임의의 가설설정,통계x)
#     
#     1. 종합부문에서 빈도수가 높았던 작업자들은 가수의 성별,솔로/그룹,장르 등 피처 구분없이 가장실력검증이 된사람이다.(어떠한 가수들과 협업을 하여도 앨범을 성공시킬 확률이 높다) 
#             * 가장 큰범주에서 증명된 작업자로 판단하여 1순위 선정
#             
#     2. 여자댄스그룹 부문에서 빈도수가 높았던 작업자들은 여자댄스그룹을 성공시킨 경험이 많은 실력이 검증된 사람들이다.(프로젝트 컨셉과 일치하기에 다른 여자댄스그룹을 런칭할때도 성공할 확률이 높다고 예상) 
#             * 프로젝트 컨셉과 일치하는 피처들로 선정하였지만 1순위보다는 더 적은 범주로 구분지었다 판단하여 2순위 선정
#                         
#     3. 여자댄스그룹의 좋아요를 많이(10만개이상) 받게한 작업자들은 팬들의 참여,지지율을 많이받게해준 작업자들이다.  
#             * 좋아요를 통해 참여,지지율의 장점은 있으나 신규여자댄스그룹 런칭에서는 가장 적은 범주로 판단하여 3순위 선정
#
#
#         * 1984년도 ~ 2020년도 데이터를 기준으로
#         * 1순위 시각화시 사용 컬럼 => 작사 , 작곡 , 편곡
#         * 2순위 시각화시 사용 컬럼 => 성별 , 장르 , 솔로/그룹 , 작사 , 작곡 , 편곡
#         * 3순위 시각화시 사용 컬럼 => 성별 , 장르 , 솔로/그룹 , 좋아요 수 , 작사/작곡 , 편곡
#         * 컬럼을 적게사용할수록 더 큰 범주에서 영향력을 보였던 사람들이라고 판단하였고 우선순위를 위와같이 설정 

# 작사 / 작곡 / 편곡 결론
#
#     * 1순위(종합부문 상위 곡 기준): TEDDY / TEDDY / TEDDY
#     
#     * 2순위(여자댄스그룹 중 상위 곡 기준): 용감한형제 / 용감한형제 / 용감한형제
#     
#     * 3순위(좋아요 수가 많은 기준): 임수호&용배(RBW) / 임수호&용배(RBW) / 임수호&용배(RBW)

# 부가적으로, 정해질 컨셉에 따라 해당 프로듀서들을 고려해볼 수 있다.                       
#
#     * 걸크러시 컨셉으로 간다면 1순위인 TEDDY 추천 
#
#     * 청량으로 간다면 2순위인 용감한형제 추천 
#
#     * 청순으로 간다면 3순위인 임수호&용배(RBW)를 추천

# -------------------------------------

# ## 5. 가사분석
#  ### 시대별 top100 차트에 오른 가사
#    ** 가사의 2글자 이상인 명사만 추출하여 곡의 컨셉이나 주제를 분석해보자
#  
#    * 여성 그룹 가사
#    * 여성 그룹 연대별 가사
#    * 여성 댄스 그룹 가사
#    * 여성 댄스 그룹 연대별 가사
#    * 여성 댄스 그룹 멤버수 4명 가사
#    * 작사가와 가사
#    * 여성 댄스 그룹 순위별 가사

# 데이터셋 다시 로드
melon_df = pd.read_csv('/Users/cj/Desktop/개인/project/멜론/Realfinal.csv', encoding = 'utf-8')

# 기본 데이터 셋을 유지한채 melon 이라는 데이터 셋 복사본 생성
melon = melon_df.copy()

# 연도 컬럼 datetime 형태로 변경
melon['연도'] = pd.to_datetime(melon['연도'],format='%Y')

# ### '전체년도', '여성', '그룹' 가사분석

# melon 이용해서 '여성', '그룹'만 필터링
df_여성그룹 = melon[(melon['성별'] == '여성') & (melon['솔로/그룹'] =='그룹')]

df_여성그룹["가사"].to_csv('df_여성그룹.txt', sep = '\t', index = False, header = None)

# +
### df_여성그룹 워드클라우드 시각화


f = open('df_여성그룹.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
               # 윈도우일 경우
               # 'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc여성그룹.png')
plt.show()
# -

# 2글자 이상의 가사 빈도수
tags

# barchart로 시각화
df여성그룹 = pd.DataFrame(most)
df여성그룹.columns = ["단어" , "빈도수"]
plt.rcParams['figure.figsize'] = [33, 10]
sns.barplot(data = df여성그룹 , x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)

# ### 여성 그룹 연대별 가사
# * df_8489 - ’1984-1989’ 연도 묶음
# * df_9099 - ’1990-1999’ 연도 묶음
# * df_0009 - ’2000-2009’ 연도 묶음
# * df_1020 - ’2010-2020’ 연도 묶음

# 84-89년도 여성 그룹
df_8489 = df_여성그룹[(df_여성그룹['연도'].dt.year >= 1984) & (df_여성그룹['연도'].dt.year <= 1989)]

df_8489

# 90-99년도 여성 그룹
df_9099 = df_여성그룹[(df_여성그룹['연도'].dt.year >= 1990) & (df_여성그룹['연도'].dt.year <= 1999)]

# 00-09년도 여성 그룹
df_0009 = df_여성그룹[(df_여성그룹['연도'].dt.year >= 2000) & (df_여성그룹['연도'].dt.year <= 2009)]

# 10-20년도 여성 그룹
df_1020 = df_여성그룹[(df_여성그룹['연도'].dt.year >= 2010) & (df_여성그룹['연도'].dt.year <= 2020)]

# 해당 데이터셋 text 파일로 저장
df_8489["가사"].to_csv('df_8489.txt', sep = '\t', index = False, header = None)
df_9099["가사"].to_csv('df_9099.txt', sep = '\t', index = False, header = None)
df_0009["가사"].to_csv('df_0009.txt', sep = '\t', index = False, header = None)
df_1020["가사"].to_csv('df_1020.txt', sep = '\t', index = False, header = None)

# +
# 해당 데이터 셋 명사 추출 및 시각화
# 84~89년도 여성 그룹 워드 클라우드

f = open('df_8489.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc그룹8489.png')
plt.show()
# -

# 2글자 이상 단어 빈도수
tags

# barchart로 시각화
df8489 = pd.DataFrame(most)
df8489.columns = ["단어" , "빈도수"]
sns.barplot(data = df8489 , x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.xticks(fontsize = 15) 
plt.rcParams['figure.figsize'] = [33, 10]
plt.savefig('그룹8489.png')

# +
# 90~99년도 여성 그룹 워드 클라우드

### df_9099


f = open('df_9099.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc그룹9099.png')

plt.show()
# -

# barchart로 시각화
df9099 = pd.DataFrame(most)
df9099.columns = ["단어" , "빈도수"]
sns.barplot(data = df9099 , x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('그룹9099.png')

# 2글자 이상 단어 빈도수
most

# +
# 00~09년도 여성 그룹 워드 클라우드
### df_0009


f = open('df_0009.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df0009 = pd.DataFrame(most)
df0009.columns = ["단어" , "빈도수"]
sns.barplot(data = df0009, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.xticks(fontsize = 15)
plt.rcParams['figure.figsize'] = [33, 10]
plt.show()

# 2글자 이상 단어 빈도수
most

# +
# 10~20년도 여성 그룹 워드 클라우드
### df_1020


f = open('df_1020.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 100건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df1020 = pd.DataFrame(most)
df1020.columns = ["단어" , "빈도수"]
sns.barplot(data = df1020, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# 2글자 이상 단어 빈도수
most

# + active=""
# 연대별 가사 분석 결과
#     1. 가사에 '사랑' 이 연대별 Top 1에 위치한다
#     2. 1984-1989 연대의 경우 적용한 필터('여성'인 '그룹')에 해당하는 곡이 총 3곡 밖에 없다
#     3. 1990-1999, 2000-2009, 2010-2020 의 총 3개의 연도에서 '사랑'의 빈도수가 증가하고 있다
#     4. 연대별 빈도 상위 50개의 단어는 큰 차이가 없었으며 최근으로 올 수록 단어의 빈도수도 늘어나고 있다
# -

# ### '여성', '댄스', '그룹' 가사

# df_여성그룹에서 '댄스'만 추가
df_여성댄스그룹 = df_여성그룹[df_여성그룹["장르"] == "댄스"]

# 여성댄스그룹 txt 파일로 저장
df_여성댄스그룹["가사"].to_csv('df_여성댄스그룹.txt', sep = '\t', index = False, header = None)

# +
# 여성댄스그룹 가사 워드클라우드
### df_여성댄스그룹


f = open('df_여성댄스그룹.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc댄스그룹.png')

plt.show()
# -

# barchart로 시각화
df여성댄스그룹 = pd.DataFrame(most)
df여성댄스그룹.columns = ["단어" , "빈도수"]
sns.barplot(data = df여성댄스그룹, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('댄스그룹.png')

# 2글자 이상 단어 빈도수
most

# ### '여성', '댄스', '그룹' 연대별 가사
# * df_8489댄스 - ’1984-1989’ 연도 묶음
# * df_9099댄스 - ’1990-1999’ 연도 묶음
# * df_0009댄스 - ’2000-2009’ 연도 묶음
# * df_1020댄스 - ’2010-2020’ 연도 묶음

# 1984-1989 여성 댄스 그룹 
# 1984년에서 1989년 사이에는 해당 결과 없음
df_8489댄스 = df_여성댄스그룹[(df_여성댄스그룹['연도'].dt.year >= 1984) & (df_여성댄스그룹['연도'].dt.year <= 1989)]

# 1990-1999 여성 댄스 그룹
df_9099댄스 = df_여성댄스그룹[(df_여성댄스그룹['연도'].dt.year >= 1990) & (df_여성댄스그룹['연도'].dt.year <= 1999)]

# 2000-2009 여성 댄스 그룹
df_0009댄스 = df_여성댄스그룹[(df_여성댄스그룹['연도'].dt.year >= 2000) & (df_여성댄스그룹['연도'].dt.year <= 2009)]

# 2010-2020 여성 댄스 그룹
df_1020댄스 = df_여성댄스그룹[(df_여성댄스그룹['연도'].dt.year >= 2010) & (df_여성댄스그룹['연도'].dt.year <= 2020)]

# 해당 데이터셋 text 파일로 저장
df_8489댄스["가사"].to_csv('df_8489댄스.txt', sep = '\t', index = False, header = None)
df_9099댄스["가사"].to_csv('df_9099댄스.txt', sep = '\t', index = False, header = None)
df_0009댄스["가사"].to_csv('df_0009댄스.txt', sep = '\t', index = False, header = None)
df_1020댄스["가사"].to_csv('df_1020댄스.txt', sep = '\t', index = False, header = None)

# +
# 해당 데이터 셋 명사 추출 및 워드클라우드로 시각화

### df_9099댄스


f = open('df_9099댄스.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df9099댄스 = pd.DataFrame(most)
df9099댄스.columns = ["단어" , "빈도수"]
sns.barplot(data = df9099댄스, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# +
### df_0009댄스


f = open('df_0009댄스.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df0009댄스 = pd.DataFrame(most)
df0009댄스.columns = ["단어" , "빈도수"]
sns.barplot(data = df0009댄스, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# +
### df_1020댄스


f = open('df_1020댄스.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df1020댄스 = pd.DataFrame(most)
df1020댄스.columns = ["단어" , "빈도수"]
sns.barplot(data = df1020댄스, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# ### '여성', '댄스', '그룹', '멤버수 4명' 가사
# * 여성댄스그룹의 가사는 전체 연도와 10연단위 묶음으로 봐도 '사랑'이라는 단어가 가사에 독보적으로 많이 사용된 것을 볼 수 있었다.
# * 그렇다면 4명인 여성댄스그룹의 가사는 어떤 차이가 있을까?

# 4인 댄스그룹 가사만 뽑아 새로운 df 만들기
df_4명댄스그룹가사 = df_여성댄스그룹[df_여성댄스그룹["멤버수"] == 4]["가사"]
df_4명댄스그룹가사

# 워드클라우드를 위해 txt 파일로 저장
df_4명댄스그룹가사.to_csv('df_4명댄스그룹가사.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드로 시각화
f = open('df_4명댄스그룹가사.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc4명댄스그룹.png')

plt.show()
# -

# barchart로 시각화
df4명댄스그룹가사 = pd.DataFrame(most)
df4명댄스그룹가사.columns = ["단어" , "빈도수"]
sns.barplot(data = df4명댄스그룹가사, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('4명댄스그룹.png')

# 4인 여자댄스그룹 역시 '사랑'이라는 단어가 상당히 많이 쓰인 것을 볼 수 있었다.

# 두 글자 이상 단어 빈도수
most

# ### 작사가와 가사

# 차트에 오른 4인 여성댄스그룹의 곡은 어떤 작사가가 작업했을까?

# 4인 여성댄스그룹의 작사가별 곡 수
df_여성댄스그룹[df_여성댄스그룹["멤버수"] == 4]["작사"].value_counts()

df_여성댄스그룹[df_여성댄스그룹["멤버수"] == 4]["작사"].describe()

df_4명댄스그룹 = df_여성댄스그룹[df_여성댄스그룹["멤버수"] == 4]
df_4명댄스그룹

df_4명그룹작사 = df_4명댄스그룹[['순위','가수',"작사",'제목','가사','연도']]
df_4명그룹작사

df_4명그룹작사["작사"].describe()

# 4인 여성그룹으로 차트 100에 오른 기준 100위 안에 든 곡들의 작사가는 중복을 제외하고 41명이다.

df_4명그룹작사["작사"].value_counts()

# * 노래에 따라서 동일인물임에도 작사명이 다른 것이 있고, 추가 작사가가 있으면 분리되어 카운트 되는 것이 있다.
# * 많은 빈도수를 보여준 탑5 작사가
#     * 테디 15곡, 김이나 10곡, 김도훈 8곡, 박진영 5곡, 용감한형제 5곡

df_4명그룹작사1 = df_4명그룹작사.copy()
df_4명그룹작사1.nunique()

# 4인 여성그룹으로 차트 100에 오른 기준의 결과, 100위 안에 든 곡들의 작사가는 총 81명으로 찍히나 중복을 제외한 총 작사가는 41명이다.

df_4명그룹작사1.sort_values(by=['순위'], axis=0, ascending = True,  inplace=True)
df_4명그룹50 = df_4명그룹작사1[df_4명그룹작사1["순위"] <  50]

df_4명그룹50["작사"].describe()

df_4명그룹50["작사"].value_counts()

# * 4인 여성그룹으로 차트 50에 오른 기준의 결과, 50위 안에 든 곡들의 작사가는 총 46명으로 찍히나 중복을 제외한 총 작사가는 26명이다.
# * 노래에 따라 동일 작사가 임에도 작사가 이름이 다른 것이 있었고 메인 작사가 외에 추가 작사가가 있으면 분리되어 카운트 되는 것이 있어 작사가 혼자 작업한 결과값에 일괄적으로 포함하였음
#
# #### 많은 빈도수를 보여준 탑5 작사가
#     * 테디 12곡, 김도훈 6곡, 김이나 5곡, 이단옆차기 4곡, 박진영 4곡, 김기범 3곡, 블랙아이드필승 3곡 용감한형제 2곡

# +
# 파이차트로 본 작사가의 곡 비율

labels = ['TEDDY','김도훈','김이나','이단옆차기','박진영', '김기범', '블랙아이드필승', '용감한형제'] ## 라벨
frequency = [12,6,5,4,4,3,3,2] ## 빈도
colors = ['red','yellow','lightblue','goldenrod','lightcoral','brown', 'green', 'orange']
explode = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
 
fig = plt.figure(figsize=(10,10)) ## 캔버스 생성
fig.set_facecolor('white') ## 캔버스 배경색을 하얀색으로 설정
ax = fig.add_subplot() ## 프레임 생성
 
pie = ax.pie(frequency, ## 파이차트 출력
       startangle=90, ## 시작점을 90도(degree)로 지정
        counterclock=False, ## 시계 방향으로 그린다.
       autopct=lambda p : '{:.1f}%'.format(p), ## 퍼센티지 출력
       colors = ['red','yellow','lightblue','goldenrod','lightcoral','brown', 'green', 'orange'] ## 색상 지정
       ,explode=explode, labels = labels)

plt.show()
# -

# * '4명'의 '여성''댄스''그룹'으로 1-50위에 든 곡의 작사가는 TEDDY가 30.8%로 가장 높았으며 김도훈, 김이나, 이단옆차기, 박진영순으로 10% 이상을 보여주었다

# #### 상위 3명인 TEDDY, 김도훈, 김이나 작사가의 가사를 분석해보자

df_4명그룹50[df_4명그룹50["작사"].str.contains("TEDDY")]

df_4명그룹50[df_4명그룹50["작사"].str.contains("TEDDY")]["순위"].mean()

# * 작사가 TEDDY의 경우 총 10개의 곡이 50위안에 들었으며 그 평균 순위는 14.7위 이다

df_TEDDY가사  = df_4명그룹50[df_4명그룹50["작사"].str.contains("TEDDY")]["가사"]
df_TEDDY가사

df_TEDDY가사.to_csv('df_TEDDY가사.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드로 시각화
f = open('df_TEDDY가사.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('df_TEDDY가사.png')

plt.show()
# -

df_TEDDY가사 = pd.DataFrame(most)
df_TEDDY가사.columns = ["단어" , "빈도수"]
sns.barplot(data = df_TEDDY가사, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('df_TEDDY가사.png')

# * 앞선 분석 결과와 동일하게 '사랑'이 약 24회 정도로 가장 많이 들어가있음을 볼 수 있다

df_4명그룹50[df_4명그룹50["작사"].str.contains("김도훈")]

df_4명그룹50[df_4명그룹50["작사"].str.contains("김도훈")]["순위"].mean()

# * 김도훈 작사가의 경우 총 6개의 곡이 50위안에 들었으며 그 평균 순위는 27.5위 이다

df_김도훈가사  = df_4명그룹50[df_4명그룹50["작사"].str.contains("김도훈")]["가사"]
df_김도훈가사

df_김도훈가사.to_csv('df_김도훈가사.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드로 시각화
f = open('df_김도훈가사.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('df_김도훈가사.png')

plt.show()
# -

df_김도훈가사 = pd.DataFrame(most)
df_김도훈가사.columns = ["단어" , "빈도수"]
sns.barplot(data = df_김도훈가사, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('df_김도훈가사.png')

# * 유일하게 단어빈도 Top 50 안에 '사랑'이 들어가 있지 않다 이를 통해 '사랑'을 포함하여 '마음', '남자' 등 계속 등장하였던 단어의 빈도가 순위와는 관련이 적다고 볼 수도 있다

df_4명그룹50[df_4명그룹50["작사"].str.contains("김이나")]

df_4명그룹50[df_4명그룹50["작사"].str.contains("김이나")]["순위"].mean()

df_김이나가사  = df_4명그룹50[df_4명그룹50["작사"].str.contains("김이나")]["가사"]
df_김이나가사

df_김이나가사.to_csv('df_김이나가사.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드로 시각화
f = open('df_김이나가사.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('df_김이나가사.png')

plt.show()
# -

df_김이나가사 = pd.DataFrame(most)
df_김이나가사.columns = ["단어" , "빈도수"]
sns.barplot(data = df_김이나가사, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('df_김이나가사.png')

# * 김이나 작사가의 경우도 '사랑'이 가장 많은 빈도를 보여주고 있음을 볼 수 있었다





# ### 50위 안에 들었던 곡 중에서 최근 10곡의 가사

df_4명그룹50_1 = df_4명그룹50.copy()

df_4명그룹50_1.sort_values(by=['연도'], axis=0, ascending = True,  inplace=True)
df_4명그룹50_1



# 50위 안에 포함된 4명 여자댄스그룹의 곡 중에서 최근 10곡의 가사 분석
df_4명그룹50_2 = df_4명그룹50_1.tail(10)

# 워드클라우드를 위해 txt파일로 저장
df_4명그룹50_2["가사"].to_csv('df_4명그룹50_2.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드로 시각화

f = open('df_4명그룹50_2.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df4명그룹50_2 = pd.DataFrame(most)
df4명그룹50_2.columns = ["단어" , "빈도수"]
sns.barplot(data = df4명그룹50_2, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# 곡 제목에 해당하는 단어가 가사에 많이 포함된 점을 파악하였다

# +
# 워드클라우드 시각화2

f = open('df_4명그룹50_2.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
morphs = nlpy.morphs(lines)
# 두 글자 이상 단어만 추출
words = []
for n in morphs:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()
# -

# barchart로 시각화
df4명그룹50_2 = pd.DataFrame(most)
df4명그룹50_2.columns = ["단어" , "빈도수"]
sns.barplot(data = df4명그룹50_2, x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.show()

# 형태소 형태로 보았을때는 곡 제목에 들어가는 단어 뿐만 아니라 영어 단어가 많이 포함되어 있는 것을 볼 수 있었다.

# ### '여성', '댄스', '그룹'의 순위별 가사
# * 1-30위와 50-100위 순위 분류
# * (조작적 정의 : 1-30위 차트인 하여 초대박/대박을 친 곡, 50-100위 차트인 하였지만 상대적으로 순위가 낮은 곡)

# 50-100위 순위(중복값 제거 전)
df_50이상 = df_4명댄스그룹[df_4명댄스그룹["순위"] >= 50]

# 1-30위 순위(중복값 제거 전)
df_30이하 = df_4명댄스그룹[df_4명댄스그룹["순위"] <= 30]

df_30이하.describe()

df_50이상.describe()

# 1-30위의 데이터와 50-100위의 데이터에 둘다 포함이 된 2곡은 제거하여 분석

# 1-30위 순위(중복값 제거 후)
df_30이하 = df_30이하[df_30이하.제목 != "불장난"]
df_30이하 = df_30이하[df_30이하.제목 != "마지막처럼"]

# 1-30위 가사 txt 파일로 저장
df_30이하["가사"].to_csv('df_30이하.txt', sep = '\t', index = False, header = None)

# +
# 중복값 제거 후의 워드클라우드
f = open('df_30이하.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc30이하.png')

plt.show()
# -

# barchart로 시각화
df30이하 = pd.DataFrame(most)
df30이하.columns = ["단어" , "빈도수"]
sns.barplot(data = df30이하 , x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('30이하.png')

# 두 글자 이상 단어 빈도수
most

# 1-30위의 데이터와 50-100위의 데이터에 둘다 포함이 된 2곡은 제거하여 분석

# 50-100위 순위(중복값 제거 후)
df_50이상 = df_50이상[df_50이상.제목 != "마지막처럼"]
df_50이상 = df_50이상[df_50이상.제목 != "불장난"]

# 중복값 제거 후 워드클라우드를 위해 txt파일로 저장
df_50이상["가사"].to_csv('df_50이상.txt', sep = '\t', index = False, header = None)

# +
# 워드클라우드 시각화
f = open('df_50이상.txt', "r", encoding='utf-8')
lines = f.read()
from konlpy.tag import Twitter
nlpy = Twitter()
nouns = nlpy.nouns(lines)
# 두 글자 이상 단어만 추출
words = []
for n in nouns:
    if len(n) > 1:
        words.append(n)
# 단어 빈도수 계산하여 상위 50건만 추출
count = Counter(words)
most = count.most_common(50)
tags = {}
for n, c in most:
    tags[n] = c
wc = WordCloud(font_path= 
#                'C:/Windows/Fonts/gulim.ttc',
               # 맥일 경우, 
               '/Library/Fonts/AppleGothic.ttf',
                background_color="white",
                width=1000,
                height=1000,
                max_words=50,
                max_font_size=300)
wc = wc.generate_from_frequencies(tags)
plt.figure(figsize=(10,10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.savefig('wc50이상.png')

plt.show()
# -

# barchart로 시각화
df50이상 = pd.DataFrame(most)
df50이상.columns = ["단어" , "빈도수"]
sns.barplot(data = df50이상 , x = "단어", y = "빈도수", palette = sns.color_palette("bright"))
plt.rcParams['figure.figsize'] = [33, 10]
plt.xticks(fontsize = 15)
plt.savefig('50이상.png')

# 두 글자 이상 단어 빈도수
most

df_30이하[df_30이하["가사"].str.contains("사랑")]["순위"].mean()

df_30이하[~df_30이하["가사"].str.contains("사랑")]["순위"].mean()

# * 1위-100위의 차트중 1-30위를 기록한 곡들에서 가사에 '사랑'이 포함된 곡의 평균 순위는 10.6위
# * 1위-100위의 차트중 1-30위를 기록한 곡들에서 가사에 '사랑'이 포함되지 않은 곡의 평균 순위는 14.5위

df_50이상[df_50이상["가사"].str.contains("사랑")]["순위"].mean()

df_50이상[~df_50이상["가사"].str.contains("사랑")]["순위"].mean()

# * 1위-100위의 차트중 50-100위를 기록한 곡들에서 가사에 '사랑'이 포함된 곡의 평균 순위는 70.5위
# * 1위-100위의 차트중 50-100위를 기록한 곡들에서 가사에 '사랑'이 포함되지 않은 곡의 평균 순위는 72위

# 1-30위 와 50-100위 비교 결과
#    * 먼저 블랙핑크의 '마지막처럼'과 '불장난'이 1-30위와 50-100위에 둘 다 포함되어 있어 좀 더 명확한 결과를 보기 위해 제거하였다
#    * 중복값을 제거하여 1-30위에 총 32곡 50-100위에 총 33곡으로 매우 유사한 조건으로 분석을 진행하였다
#    * '사랑'이 두 순위 구간에서 가장 많이 쓰였다
#    * 50-100위의 순위에서 1-30위보다 '사랑'의 단어 사용 빈도는 약 2배 정도 많았다
#    * 하지만 1-30위와 50-100위 두 구간에서 '사랑'이 포함된 곡의 순위가 '사랑'이 포함되지 않은 곡의 순위보다 높게 나왔다 

# ### 가사분석결론
#     
#     여성그룹, 연대별 여성그룹, 여성댄스그룹, 4인 여성댄스그룹 결과에서 '사랑'의 단어 사용 빈도가 가사에서 압도적으로 많음을 볼 수 있다.
#     4인 여성댄스그룹 순위 1-30과 50-100을 보았을 때, 50-100위에 '사랑'의 단어 사용 빈도가 1-30위보다 2배 가량 많았다.
#     그러나, 1-30위와 50-100위의 곡에서 '사랑'이 들어간 곡들이 1-30위와 50-100위의 곡에 '사랑'이 들어가지 않은 곡들보다 순위에서 높음을 보여주었다.
#     
#     * 따라서, 신인 걸그룹 곡에는 '사랑'이 들어간 주제나 컨셉의 곡을 작사하는 것을 추천하며 단어의 빈도는 적게 하는 것을 추천한다.

# -------------------------------

# ## 6. 발매일 전략
# * 연도별 순위에 오른 곡 수 변화
# * 월 별 인기 장르 비교
# * 장르에 따른 멤버수 별 곡 수

# 데이터셋 다시 불러오기
df = pd.read_csv('/Users/cj/Desktop/개인/project/멜론/Realfinal.csv', encoding = 'utf-8')
df = df[df['연도'] <= 2020]

# ### 연도별 순위에 오른 곡 수 변화
# * 전체년도 곡 수 변화
# * 연도별 top100에 오른 여성그룹수 변화

# 발매일 타입 변환
df['발매일']= pd.to_datetime(df['발매일'])
df['발매일']

# 발매일에서 발매월만 추출
df['발매월']= df['발매일'].dt.month
df[['발매월']].tail()

# 발매월별 top100에 오른 곡 수를 파악하기 위해 발매일 컬럼에서 발매월을 추출하기 위한 과정이 필요했음.

# df에서 솔로/그룹에서 그룹만 추출 group_df로 지정
group_df = df[df['솔로/그룹'] == '그룹']
group_df

# 연도별 그룹들의 top100에 오른 곡 수 파악
group_df.groupby('연도')['가수'].nunique()

# 시각화
plt.figure(figsize= (33, 10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
plt.title('연도별 순위에 오른 그룹들의 곡 수 변화', fontsize=20)
plt.plot(group_df.groupby('연도')['가수'].nunique())

# 연도별 순위에 오른 그룹들의 곡 수 변화를 확인하고 다음으로 여성 그룹으로 범위를 정해서 진행

# group_df에서 여성의 그룹만 추출. female_group으로 지정 및 확인
female_group = group_df[group_df['성별']=='여성']
female_group.head()

# 1984~2020년간 데뷔한 여성그룹의 곡 수 파악
female_group['가수'].nunique()

# 여자 그룹의 평균 멤버수 확인
female_group = group_df[group_df['성별']=='여성']
female_group['멤버수'].mean()

# 약 36년간 73개의 여성그룹이 존재했고, 이들의 평균 멤버수는 4.6명으로 파악함.

gmember_count = pd.DataFrame(female_group.groupby('연도')['가수'].nunique())
gmember_count = gmember_count.reset_index()
gmember_count

# 시각화
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
plt.title('연도별 top100에 오른 여성그룹 수 변화')
sns.lineplot(data = gmember_count, x='연도', y='가수')

#연도별 top100에 오른 여성 그룹의 곡수 gmember_scount로 지정 
gmember_count = pd.DataFrame(female_group.groupby('연도')['제목'].count())
gmember_scount = gmember_count.rename(columns = {'제목': '곡 수'})
gmember_scount = gmember_scount.reset_index()
gmember_scount

# 연도별 top100안에 오른 여성그룹의 곡 수
gmember_scount = pd.DataFrame(female_group.groupby('연도')['제목'].count())
gmember_scount = gmember_count.rename(columns = {'제목': '곡 수'})
gmember_scount = gmember_scount.reset_index()
gmember_scount

# 시각화
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
plt.title('연도별 top100에 오른 여성그룹의 곡 수 변화')
sns.lineplot(data = gmember_scount, x='연도', y='곡 수')

# 시각화한 결과값을 통해 확인할 수 있는 부분이 2005년을 기점으로 2011년까지 여성 그룹의 곡 수가 증가했으나 이후 하락하는 추세임을 확인할 수 있음.

# 1984년 ~ 2020년의 4대 연대 여성그룹의 곡 수 (80년대/ 90년대 / 00년대 / 10~20년대)를 통해 연도별 특징을 파악하기 위한 과정

# 80년대 여성그룹의 곡 수 
g80=gmember_scount[gmember_scount['연도']<1990]
g80

# 80년대 여성그룹의 곡 수 시각화 
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
plt.title('80년대 top100에 오른 여성그룹 노래')
sns.boxplot(data=g80, x='연도', y='곡 수')

# * 80년대 여성그룹의 경우 총 3곡

# 90년대 여성그룹의 곡 수 
g90=gmember_scount[(gmember_scount['연도']>=1990) & (gmember_scount['연도']<2000)]
g90

# 90년대 여성그룹의 곡 수 시각화
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('90년대 top100에 오른 여성그룹 노래')
sns.lineplot(data=g90, x='연도', y='곡 수')

# 90년도에서는 1997년 2곡에서 1998년에 9곡으로 눈에 띄는 변화를 보임

# 00년대 여성그룹의 곡 수 
g00 = gmember_scount[(gmember_scount['연도']>=2000) & (gmember_scount['연도']<2010)]
g00

# 00년대 여성그룹의 곡 수 시각화
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.axvline(x=2007, color='r', linestyle='--')
plt.axvline(x=2009, color='r', linestyle='--')
plt.title('00년대 top100에 오른 여성그룹 노래')
sns.lineplot(data=g00, x='연도', y='곡 수')

# 2007년도까지 조금씩 곡 수가 많아지다가 2007년도부턴 급격하게 곡 수가 많아지는 모습을 보여줌

# 10~20년대 여성그룹의 곡 수 
g1020=gmember_scount[gmember_scount['연도']>2010]
g1020

# 10~20년대 여성그룹의 곡 수 시각화
plt.rc("font", family = "AppleGothic")
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.title('10~20년도 top100에 오른 여성그룹 노래')
sns.lineplot(data=g1020, x='연도', y='곡 수')

# 연도를 나누는 과정에서 뚜렷한 특징이 없다고 판단되어 2000년 이전 / 2000년에서 2010년 / 2010년 이후로 분류해서 특징을 확인하는 과정

# 2000년 이전 차트에 오른 평균 곡 수
gmember_scount[gmember_scount['연도'] <2000].mean()

# 2000년대 차트에 오른 평균 곡 수
gmember_scount[(gmember_scount['연도'] >=2000) & (gmember_scount['연도'] < 2010)].mean()

# 2010년 이후 차트에 오른 평균 곡 수
gmember_scount[gmember_scount['연도'] >=2010].mean()

# 2000년 이전 / 2000년-2010년 / 2010년 이후의 결과에서 점차 곡 수가 많아졌음을 확인

# ### 월 별 인기 장르 비교
# * 발매월별 여성 그룹의 곡 수
# * 여그룹 월 별 인기 장르
# * 월 별 여성댄스그룹의 곡 수

# 월에 따른 top100에 오른 여성 그룹의 곡 수를 파악하는 과정. 이를 통해 여성그룹의 월별 활동정도를 파악하고자 함.

# 발매월별 여성그룹수 gmember_mcount로 지정
gmember_mcount = pd.DataFrame(female_group.groupby('발매월')['멤버수'].count())
gmember_mcount = gmember_mcount.rename(columns = {'멤버수': '그룹수'})
gmember_mcount = gmember_mcount.reset_index()
gmember_mcount

# 84년~20년까지의 발매월별 top100에 오른 여성그룹들의 곡 수 시각화
plt.figure(figsize=(33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.axvline(x=5, color='r', linestyle='--')
plt.axvline(x=7, color='r', linestyle='--')
plt.title('발매월별 top100에 오른 여성그룹의 노래')
sns.lineplot(data=gmember_mcount, x='발매월', y='그룹수')

# 5월을 시작으로 7월까지 발매하는 곡 수가 증가하기 시작했다. 이것으로 보아 '여름'을 겨냥한 여성그룹의 활동이 높아지지 않았나 추측할 수 있었다.

# 전체 연도별 여그룹 인기있는 장르 top10을 female_group_trend로 지정
female_group_trend = pd.DataFrame(female_group.groupby('장르')['제목'].count()).rename(columns = {'제목' : '곡 수'}).reset_index().sort_values(by = '곡 수', ascending=False).head(10)
female_group_trend

# 위에서 여성그룹의 경우 남성그룹보다 댄스를 장르로 많은 활동을 하는 것을 다시 한번 확인하는 과정

# 연도별 여그룹 인기장르 시각화
plt.figure(figsize=(33,10))
plt.title('연도별 여그룹 인기장르 시각화')
plt.xticks(rotation = 30)
sns.barplot(data= female_group_trend, x='장르', y='곡 수')

# 여그룹 발매월별 인기장르 top10 ->  댄스곡이 주로 6,7월에 집중되어있음
fg_mtrend= pd.DataFrame(female_group.groupby(['장르','발매월'])['제목'].count()).rename(columns ={'제목':'곡 수'}).reset_index().sort_values(by = '곡 수', ascending = False)
fg_mtrend

# 가장 인기있는 장르는 댄스이며 주로 6,7월에 집중되어있음
fg_mtrend.head(10)

# 여성그룹 월별 인기장르 시각화
plt.figure(figsize = (33,10))
plt.title('여그룹 월별 인기장르 top10')
sns.barplot(data =fg_mtrend, x= '발매월', y= '곡 수', hue= '장르')

# 여성그룹의 경우 댄스가 압도적으로 인기가 많은 장르임을 다시 한번 파악할 수 있었다.

# 여성그룹 발매월별 장르 댄스 시각화 
fgd=fg_mtrend[fg_mtrend['장르']=='댄스']
plt.figure(figsize = (33,10))
plt.title('발매월별 장르가 댄스')
sns.barplot(data =fgd, x= '발매월', y= '곡 수')

# 발매월별 장르가 댄스인 여성그룹의 곡 수 시각화
fgd=fg_mtrend[fg_mtrend['장르']=='댄스']
plt.figure(figsize = (33,10))
ax=plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
plt.axvline(x=5, color='r', linestyle='--')
plt.axvline(x=7, color='r', linestyle='--')
plt.title('발매월별 장르가 댄스')
sns.lineplot(data =fgd, x= '발매월', y= '곡 수')

# * 여러 시각화를 통해 발매월별 장르가 댄스인 곡 수를 파악한 결과 5월부터 증가하기 시작해서 7월에 최고치에 도달하는 것을 알 수 있음.
# * 이를 통해 여성그룹의 경우 여름을 겨냥한 댄스곡으로 많은 활동을 하지않을까라는 추측. 
# * 12월의 경우에는 가장 적은 발매시기이지만 오히려 신인의 경우 이 시기를 공략해보는 것도 전략이 될 수 있다고 생각한다.
#
#

# ### 장르에 따른 멤버수 별 곡 수
# * 3명 이하
# * 4명
# * 5명
# * 6명 이상

# 장르와 멤버수에 따른 곡 수를 fggm으로 지정
fggm= pd.DataFrame(female_group.groupby(['장르','멤버수'])['제목'].count()).reset_index().rename(columns ={'제목':'곡 수'})
fggm

# 장르에 따른 멤버수별 곡 수 시각화
plt.figure(figsize = (33,10))
plt.title('장르에 따른 멤버수별 곡 수')
sns.barplot(data =fggm, x= '멤버수', y= '곡 수', hue='장르')

# 장르에 따른 여성그룹의 멤버수별 top100에 오른 곡 수를 파악해본 결과 멤버수가 4명/5명/6명이상의 경우
# 압도적인 비중으로 댄스를 차지하고 있음을 확인

# 장르가 댄스, 멤버가 3명이하인 여성그룹
fg3d=female_group[(female_group['멤버수']<=3)&(female_group['장르']== '댄스')]
fg3d

# 장르가 댄스, 멤버가 3명이하인 여성그룹
fg3d_mtrend= pd.DataFrame(fg3d.groupby('발매월')['제목'].count()).rename(columns ={'제목':'곡 수'}).reset_index()
fg3d_mtrend

# 장르가 댄스, 멤버가 3명이하인 여성그룹 시각화
plt.figure(figsize = (33,10))
plt.title(' 멤버수 3명이하인 여성댄스그룹 월별 곡 수 ')
sns.barplot(data =fg3d_mtrend, x= '발매월', y= '곡 수')

# 5월과 11월에 5곡으로 가장 높은 값을 보였다

# 장르가 댄스, 멤버가 4명인 여성그룹
fg4 = female_group[(female_group['멤버수']== 4) & (female_group['장르']== '댄스')]
fg4

# 멤버가 4명인 댄스그룹 발매월별 곡 수
fg4_mtrend= pd.DataFrame(fg4.groupby('발매월')['제목'].count()).rename(columns ={'제목':'곡 수'}).reset_index()
fg4_mtrend

# # 장르가 댄스, 멤버가 4명인 여성그룹 시각화
plt.figure(figsize = (33,10))
plt.title('멤버수 4명인 여성댄스그룹 월별 곡 수 ')
sns.barplot(data =fg4_mtrend, x= '발매월', y= '곡 수')

# 멤버가 4명인 여성그룹의 경우 6월과 7월이 17곡 15곡으로 압도적으로 높았다

# 장르가 댄스, 멤버가 5명인 여성그룹
fg5 = female_group[(female_group['멤버수'] == 5) & (female_group['장르']== '댄스')]
fg5

# # 장르가 댄스, 멤버가 5명인 여성그룹
fg5_mtrend= pd.DataFrame(fg5.groupby('발매월')['제목'].count()).rename(columns ={'제목':'곡 수'}).reset_index()
fg5_mtrend

# 장르가 댄스, 멤버가 5명인 여성그룹 시각화
plt.figure(figsize = (33,10))
plt.title('멤버수 5명인 여성댄스그룹 월별 곡 수 ')
sns.barplot(data =fg5_mtrend, x= '발매월', y= '곡 수')

# 멤버가 5명인 여성그룹의 경우 9월이 10곡으로 가장 높은 값을 보여줬다

# 장르가 댄스, 멤버가 6명 이상인 여성그룹
fg6up = female_group[(female_group['멤버수'] > 5) & (female_group['장르']== '댄스')]
fg6up['가수']

# 장르가 댄스, 멤버가 6명 이상인 여성그룹
fg6up_mtrend= pd.DataFrame(fg6up.groupby('발매월')['제목'].count()).rename(columns ={'제목':'곡 수'}).reset_index()
fg6up_mtrend

# 장르가 댄스, 멤버가 6명 이상인 여성그룹 시각화
plt.figure(figsize = (33,10))
plt.title('멤버수 6명 이상인 여성댄스그룹 월별 곡 수 ')
sns.barplot(data =fg6up_mtrend, x= '발매월', y= '곡 수')

# ### 발매일 전략 결론
#    * 전반적으로 동일한 경향을 나타나지는 않지만, 멤버수가 4명/5명/6명 이상의 경우를 분석한 결과 5월부터 7월사이 여성그룹들이 많은 곡 수를 통해 활동하는 것을 확인할 수 있었음. 
#
#    * 공통적으로 12월에는 가장 낮은 곡 수를 보이는데 이는 이 시기에는 댄스 여성그룹의 활동이 저조하다는 것을 알 수 있었음. 
#
#    * 이를 통해 신인 여성그룹이 댄스라는 장르를 가지고 데뷔를 할 때 12월에 데뷔하는 것도 전략이 될 수 있을 것이라고 판단함.

# ------------------------

# # 최종 결론

# 1. 멤버 수 전략 분석 결과   - 4명을 추천한다
#
# 2. 곡 장르 전략 분석 결과   - 댄스 장르를 추천한다
#
# 3. 곡 제목 수 분석 결과    - 순위와 관계 없는 것으로 보인다
#
# 4. 작사/작곡/편곡 분석 결과 - 각각 컨셉에 맞게 teddy(걸크러시), 용감한형제(청량), 임수호&용배(청순)이 추천한다
#
# 5. 가사 분석 결과         - '사랑'이라는 단어가 들어간 주제나 컨셉의 곡을 작사하는 것을 추천하며 단어의 빈도는 적게 하는 것이 추천한다
#
# 6. 발매일 전략            - 12월을 추천한다
