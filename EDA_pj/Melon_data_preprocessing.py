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

# # 멜론 데이터 전처리(1984~2020)
# * '데뷔곡' 컬럼 삭제
# * 팬수, 좋아요수 dtype을 object 타입에서 float 형태로 바꾸기
# * 2021년 데이터 삭제(형평성 문제 때문) 즉, 새로운 표준 데이터셋은 1984~2020년의 데이터가 범위가 되는 것
# * 가사컬럼 row 줄바꿈 없애기
# * 2020년 데이터까지만
# * Unnamed: 0컬럼 없애고 인덱스 정리
# * 결측치 있는 행 모두 0으로 처리
# * 스트리밍 서비스가 중지된 곡의 가사들은 '가사준비중~'으로 뜨기 때문에 '가사 없음'으로 처리
# * 19금 노래인 경우 가사와 제목에 전처리 필요
# * 제목에 같이 붙어있는 괄호와 괄호안의 소제목, 피쳐링 등 삭제

# 라이브러리 로드
import pandas as pd

# Unnamed: 0컬럼 없애고 인덱스 정리
melon_df = pd.read_csv('data/Melon_Data.csv', index_col=0)
melon_df = melon_df.drop(['Unnamed: 0.1'], axis = 1)
# 2020년 데이터 까지만
melon_df = melon_df[melon_df['연도'] <= 2020]

# 데이터 확인
melon_df.tail()

# '데뷔곡' 컬럼 삭제
melon_df = melon_df.drop(['데뷔곡'], axis=1)
melon_df.head()

# 데이터 info 확인
melon_df.info()

# 좋아요 수와 팬 수 컬럼의 데이터 타입 바꾸기
melon_df['좋아요 수'] = melon_df['좋아요 수'].str.replace(',', '').astype(float)
melon_df['팬수'] = melon_df['팬수'].str.replace(',', '').astype(float)

# 다시 info 확인
melon_df.info()

# 결측치 확인
melon_df.isnull().sum()

# 결측치 0으로 채우기
melon_df = melon_df.fillna(0) 

# 다시 결측치 확인
melon_df.isnull().sum()

# \n 제거 (가사컬럼 row 줄바꿈 없애기)
melon_df = melon_df.replace('\n',' ', regex=True)

# 스트리밍 서비스가 중지되어 가사 준비중인 row의 경우 '가사 없음'으로 처리
melon_df['가사'][melon_df['가사'].str.contains('\[가사 준비중\] 멜론 회원 여러분!')] = '가사 없음'

melon_df['가사'].head(10)

# 19금 노래인 경우 가사 '가사 없음'으로 처리
melon_df['가사'][melon_df['가사'].str.contains('^청소년 보호법')] = '가사 없음'

# 19금 노래의 경우 제목 앞에 '19금' 삭제
melon_df['제목'] = melon_df['제목'].str.replace('19금', '')

# 제목 괄호와 괄호안에 포함된 내용 제거
melon_df['제목'] = melon_df['제목'].str.replace(r"\(.*\)","") 

# csv 파일로 저장
melon_df.to_csv('semi_final_melon_data.csv', encoding='utf-8-sig',index=False)

df = pd.read_csv('semi_final_melon_data.csv')

df.info()

df.head(10)




