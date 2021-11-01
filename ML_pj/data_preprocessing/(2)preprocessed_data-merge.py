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

# # Data-Merge
# * 전처리한 각 파일을 필요에 따라 merge

# +
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %matplotlib inline 
# %config InlineBackend.figure_format = 'retina' 

# +
# 전처리 된 모든 데이터 불러오기

customer = pd.read_csv('customer.csv')
shop_product = pd.read_csv('shop_df.csv')
out_product = pd.read_csv('shopno_df.csv')
classifi_product = pd.read_csv('productvar.csv')
# -

# # 쇼핑업종 관련 데이터 생성
# **고객Demo × 쇼핑업종 데이터 × 상품분류 데이터**
# * 고객데이터와 쇼핑업종 데이터 merge
# * 구매금액과 구매수량을 곱하여 '총쇼핑소비금액'이라는 새로운 컬럼 생성
# * 상품분류 데이터 merge 시킨 후 필요없는 컬럼 삭제

df_shop = cus_shop_pro(customer, shop_product, classifi_product)
df_shop


# # 쇼핑외업종 관련 데이터 생성
# **고객 Demo 데이터 × 쇼핑외업종 데이터**
# * 고객데이터와 쇼핑외업종 데이터 merge
# * 쇼핑외업종 데이터의 이용금액과 이용건수를 곱하여 총쇼핑외금액 컬럼 생성

# +
# merge 함수 생성

def cus_shopno_mer(cus_df, shopno_df):
    
    # 고객데이터와 쇼핑외업종 데이터 merge
    customer_out = pd.merge(cus_df, shopno_df, on='ID', how='inner')
    
    # 데이터 copy하여 새 컬럼 생성
    customer_out1 = customer_out.copy()
    customer_out1['총_쇼핑외금액'] = customer_out1['이용금액'] * customer_out1['이용건수']
    
    # 각 고객별 총쇼핑외금액 df 생성
    customer_sum_out = pd.DataFrame(customer_out1.groupby(['ID', '성별', '연령대', '시도', '시군구'])['총_쇼핑외금액'].sum().reset_index())
    
    customer_out = pd.merge(customer_sum_out, out_product, on='ID', how='inner')
    
    return customer_out


# -

df_shopno = cus_shopno_mer(customer, out_product)
df_shopno

# # 최종 데이터 저장
# * 분석시 사용할 데이터인 df_shop(쇼핑업종데이터)와 df_shopno(쇼핑외업종데이터) 저장

df_shop.to_csv('df_shop.csv', index=False)
df_shopno.to_csv('df_shopno.csv', index=False)








