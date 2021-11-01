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

# # 멜론 월간차트 크롤링 (2021 01. ~ 02)
# * 크롤링한 데이터 출처: https://www.melon.com/chart/search/index.htm (멜론 시대별차트 차트파인더)

import selenium
from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from itertools import repeat

# 크롬 드라이버 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(5) # 대기 걸기
driver.maximize_window()


# # 2021.01월 데이터 수집
# * 트래픽에 부하를 줄 수 있으므로 1월과 2월을 나눠서 진행하였다

# +
############### 1월 데이터 수집

    
# 크롤링으로 데이터 수집

# 각 컬럼별 데이터 리스트 선정 (15개)

year = [] # 연도
rank = [] # 순위
title = [] # 곡 명
singer= [] # 가수
album = [] # 앨범명
like_count = [] # 좋아요 수

date_of_issue = [] # 앨범 발매일
genre = [] # 장르
lyrics = [] # 가사
three = [] # 작사/작곡/편곡

fan_count = [] # 팬 수

member_count = [] # 멤버수
solor_group = [] # 솔로/그룹여부
gender = [] # 성별
debut_song = [] # 데뷔곡 명


# 1~50위곡 순위, 곡 제목, 가수, 앨범, 좋아요 수 수집
for i in range(50):
    # 드라이버가 해당 url 접속
    url = 'https://www.melon.com/chart/month/index.htm' # 멜론 월간 차트 url
    driver.get(url)


    # 국내 종합 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[2]/dl/dd[1]/ul/li[2]/a/span').click()


    # 월 고르기 버튼 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/button').click()
    time.sleep(1)

    # 1월 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/div/dl/dd[1]/ul/li[1]/a/span').click()
    time.sleep(1)
    
    year.append('2021.01')
    rank.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[2]/div/span[1]').text)
    title.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[1]/span/a').text)
    singer.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[2]/a[1]').text)
    album.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[7]/div/div/div/a').text)
    like_count.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[8]/div/button/span[2]').text)
    
    

    # 앨범명 클릭 페이지 (발매일, 장르, 가사, 작사/작곡/편곡)
    driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[5]/div/a').click()
    time.sleep(2)
    date_of_issue.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[2]').text)
    genre.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text)
    lyrics.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text)


    temp = driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/ul')
    time.sleep(2)
    for i in range(len(temp)):
        three.append(temp[i].text)

    # 가수명 페이지 클릭 (팬 수를 수집하기 위함)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]/a/span[1]').click()
    time.sleep(2)
    fan_count.append(driver.find_element_by_id('d_like_count').text)

    # 상세정보 페이지 클릭 (멤버수,솔로/그룹,성별,데뷔곡을 수집하기 위함)
    try:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/ul/li[2]/a').click()
        time.sleep(2)
    except:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[4]/ul/li[2]/a').click()
        time.sleep(2)

    try:
        member_count.append(len(driver.find_element_by_class_name('wrap_atistname').text.split(',')))
        solor_group.append("그룹")

    except:
        member_count.append(1)
        solor_group.append("솔로")

    mfm = driver.find_element_by_class_name('section_atistinfo03').text
    time.sleep(2)
    if mfm.find("혼성") >= 0:
        gender.append("혼성")
    elif mfm.find("남성") >= 0:
        gender.append("남성")
    else:
        gender.append("여성")

    try:
        debut_song.append(driver.find_element_by_class_name('debutsong').text)

    except:
        debut_song.append('')
    


# +

#수집한 데이터들을 각 컬럼별로 리스트에 담아서 데이터프레임으로 만들기
df1 = pd.DataFrame({'연도' : year,
                   '순위': rank,
                   '제목': title,
                   '가수' : singer,
                   '앨범' : album,
                   '좋아요 수' : like_count,
                   '발매일' : date_of_issue,
                   '장르' : genre,
                   '가사' : lyrics,
                   '작사/작곡/편곡' : three,
                   '팬수' : fan_count,
                   '멤버수' : member_count,
                   '솔로/그룹' : solor_group,
                   '성별' : gender,
                   '데뷔곡' : debut_song
                  })
df1

# +
# 크롬 드라이버 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(5) # 대기 걸기
driver.maximize_window()

# 각 컬럼별 데이터 리스트 선정 (15개)

year = [] # 연도
rank = [] # 순위
title = [] # 곡 명
singer= [] # 가수
album = [] # 앨범명
like_count = [] # 좋아요 수

date_of_issue = [] # 앨범 발매일
genre = [] # 장르
lyrics = [] # 가사
three = [] # 작사/작곡/편곡

fan_count = [] # 팬 수

member_count = [] # 멤버수
solor_group = [] # 솔로/그룹여부
gender = [] # 성별
debut_song = [] # 데뷔곡 명


# 51~100위곡 순위, 곡 제목, 가수, 앨범, 좋아요 수 수집
for i in range(50, 100):
    # 드라이버가 해당 url 접속
    url = 'https://www.melon.com/chart/month/index.htm' # 멜론 월간 차트 url
    driver.get(url)


    # 국내 종합 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[2]/dl/dd[1]/ul/li[2]/a/span').click()


    # 월 고르기 버튼 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/button').click()
    time.sleep(1)

    # 1월 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/div/dl/dd[1]/ul/li[1]/a/span').click()
    time.sleep(1)
    
    year.append('2021.01')
    rank.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[2]/div/span[1]').text)
    title.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[1]/span/a').text)
    singer.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[2]/a[1]').text)
    album.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[7]/div/div/div/a').text)
    like_count.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[8]/div/button/span[2]').text)
    
    

    # 앨범명 클릭 페이지 (발매일, 장르, 가사, 작사/작곡/편곡)
    driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[5]/div/a').click()
    time.sleep(2)
    date_of_issue.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[2]').text)
    genre.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text)
    lyrics.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text)


    temp = driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/ul')
    time.sleep(2)
    for i in range(len(temp)):
        three.append(temp[i].text)

    # 가수명 페이지 클릭 (팬 수를 수집하기 위함)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]/a/span[1]').click()
    time.sleep(2)
    fan_count.append(driver.find_element_by_id('d_like_count').text)

    # 상세정보 페이지 클릭 (멤버수,솔로/그룹,성별,데뷔곡을 수집하기 위함)
    try:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/ul/li[2]/a').click()
        time.sleep(2)
    except:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[4]/ul/li[2]/a').click()
        time.sleep(2)

    try:
        member_count.append(len(driver.find_element_by_class_name('wrap_atistname').text.split(',')))
        solor_group.append("그룹")

    except:
        member_count.append(1)
        solor_group.append("솔로")

    mfm = driver.find_element_by_class_name('section_atistinfo03').text
    time.sleep(2)
    if mfm.find("혼성") >= 0:
        gender.append("혼성")
    elif mfm.find("남성") >= 0:
        gender.append("남성")
    else:
        gender.append("여성")

    try:
        debut_song.append(driver.find_element_by_class_name('debutsong').text)

    except:
        debut_song.append('')


# +

#수집한 데이터들을 각 컬럼별로 리스트에 담아서 데이터프레임으로 만들기
df2 = pd.DataFrame({'연도' : year,
                   '순위': rank,
                   '제목': title,
                   '가수' : singer,
                   '앨범' : album,
                   '좋아요 수' : like_count,
                   '발매일' : date_of_issue,
                   '장르' : genre,
                   '가사' : lyrics,
                   '작사/작곡/편곡' : three,
                   '팬수' : fan_count,
                   '멤버수' : member_count,
                   '솔로/그룹' : solor_group,
                   '성별' : gender,
                   '데뷔곡' : debut_song
                  })
df2
# -

result_1 = pd.concat([df1, df2], ignore_index=True)
result_1

# csv 파일로 저장
result_1.to_csv('Melon_2021_01.csv',encoding='utf-8-sig')

# # 2021.02월 데이터 수집

# +
############### 2월 데이터 수집

# 크롬 드라이버 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(5) # 대기 걸기
driver.maximize_window()
    
# 크롤링으로 데이터 수집

# 각 컬럼별 데이터 리스트 선정 (15개)

year = [] # 연도
rank = [] # 순위
title = [] # 곡 명
singer= [] # 가수
album = [] # 앨범명
like_count = [] # 좋아요 수

date_of_issue = [] # 앨범 발매일
genre = [] # 장르
lyrics = [] # 가사
three = [] # 작사/작곡/편곡

fan_count = [] # 팬 수

member_count = [] # 멤버수
solor_group = [] # 솔로/그룹여부
gender = [] # 성별
debut_song = [] # 데뷔곡 명


# 1~50위곡 순위, 곡 제목, 가수, 앨범, 좋아요 수 수집
for i in range(50):
    # 드라이버가 해당 url 접속
    url = 'https://www.melon.com/chart/month/index.htm' # 멜론 월간 차트 url
    driver.get(url)


    # 국내 종합 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[2]/dl/dd[1]/ul/li[2]/a/span').click()


    # 월 고르기 버튼 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/button').click()
    time.sleep(1)

    # 2월 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/div/dl/dd[1]/ul/li[2]/a/span').click()
    time.sleep(1)
    
    year.append('2021.02')
    rank.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[2]/div/span[1]').text)
    title.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[1]/span/a').text)
    singer.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[2]/a[1]').text)
    album.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[7]/div/div/div/a').text)
    like_count.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[8]/div/button/span[2]').text)
    
    

    # 앨범명 클릭 페이지 (발매일, 장르, 가사, 작사/작곡/편곡)
    driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[5]/div/a').click()
    time.sleep(2)
    date_of_issue.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[2]').text)
    genre.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text)
    lyrics.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text)


    temp = driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/ul')
    time.sleep(2)
    for i in range(len(temp)):
        three.append(temp[i].text)

    # 가수명 페이지 클릭 (팬 수를 수집하기 위함)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]/a/span[1]').click()
    time.sleep(2)
    fan_count.append(driver.find_element_by_id('d_like_count').text)

    # 상세정보 페이지 클릭 (멤버수,솔로/그룹,성별,데뷔곡을 수집하기 위함)
    try:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/ul/li[2]/a').click()
        time.sleep(2)
    except:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[4]/ul/li[2]/a').click()
        time.sleep(2)

    try:
        member_count.append(len(driver.find_element_by_class_name('wrap_atistname').text.split(',')))
        solor_group.append("그룹")

    except:
        member_count.append(1)
        solor_group.append("솔로")

    mfm = driver.find_element_by_class_name('section_atistinfo03').text
    time.sleep(2)
    if mfm.find("혼성") >= 0:
        gender.append("혼성")
    elif mfm.find("남성") >= 0:
        gender.append("남성")
    else:
        gender.append("여성")

    try:
        debut_song.append(driver.find_element_by_class_name('debutsong').text)

    except:
        debut_song.append('')
# -

#수집한 데이터들을 각 컬럼별로 리스트에 담아서 데이터프레임으로 만들기
df3 = pd.DataFrame({'연도' : year,
                   '순위': rank,
                   '제목': title,
                   '가수' : singer,
                   '앨범' : album,
                   '좋아요 수' : like_count,
                   '발매일' : date_of_issue,
                   '장르' : genre,
                   '가사' : lyrics,
                   '작사/작곡/편곡' : three,
                   '팬수' : fan_count,
                   '멤버수' : member_count,
                   '솔로/그룹' : solor_group,
                   '성별' : gender,
                   '데뷔곡' : debut_song
                  })
df3

# +
# 크롬 드라이버 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(5) # 대기 걸기
driver.maximize_window()
    
# 크롤링으로 데이터 수집

# 각 컬럼별 데이터 리스트 선정 (15개)

year = [] # 연도
rank = [] # 순위
title = [] # 곡 명
singer= [] # 가수
album = [] # 앨범명
like_count = [] # 좋아요 수

date_of_issue = [] # 앨범 발매일
genre = [] # 장르
lyrics = [] # 가사
three = [] # 작사/작곡/편곡

fan_count = [] # 팬 수

member_count = [] # 멤버수
solor_group = [] # 솔로/그룹여부
gender = [] # 성별
debut_song = [] # 데뷔곡 명


# 51~100위곡 순위, 곡 제목, 가수, 앨범, 좋아요 수 수집
for i in range(50,100):
    # 드라이버가 해당 url 접속
    url = 'https://www.melon.com/chart/month/index.htm' # 멜론 월간 차트 url
    driver.get(url)


    # 국내 종합 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[2]/dl/dd[1]/ul/li[2]/a/span').click()


    # 월 고르기 버튼 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/button').click()
    time.sleep(1)

    # 2월 클릭
    driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/div/div/dl/dd[1]/ul/li[2]/a/span').click()
    time.sleep(1)
    
    year.append('2021.02')
    rank.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[2]/div/span[1]').text)
    title.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[1]/span/a').text)
    singer.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[6]/div/div/div[2]/a[1]').text)
    album.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[7]/div/div/div/a').text)
    like_count.append(driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[8]/div/button/span[2]').text)
    
    

    # 앨범명 클릭 페이지 (발매일, 장르, 가사, 작사/작곡/편곡)
    driver.find_element_by_xpath(f'/html/body/div/div[3]/div/div/div[4]/form/div/table/tbody/tr[{i+1}]/td[5]/div/a').click()
    time.sleep(2)
    date_of_issue.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[2]').text)
    genre.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text)
    lyrics.append(driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text)


    temp = driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/ul')
    time.sleep(2)
    for i in range(len(temp)):
        three.append(temp[i].text)

    # 가수명 페이지 클릭 (팬 수를 수집하기 위함)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]/a/span[1]').click()
    time.sleep(2)
    fan_count.append(driver.find_element_by_id('d_like_count').text)

    # 상세정보 페이지 클릭 (멤버수,솔로/그룹,성별,데뷔곡을 수집하기 위함)
    try:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[3]/ul/li[2]/a').click()
        time.sleep(2)
    except:
        driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div[4]/ul/li[2]/a').click()
        time.sleep(2)

    try:
        member_count.append(len(driver.find_element_by_class_name('wrap_atistname').text.split(',')))
        solor_group.append("그룹")

    except:
        member_count.append(1)
        solor_group.append("솔로")

    mfm = driver.find_element_by_class_name('section_atistinfo03').text
    time.sleep(2)
    if mfm.find("혼성") >= 0:
        gender.append("혼성")
    elif mfm.find("남성") >= 0:
        gender.append("남성")
    else:
        gender.append("여성")

    try:
        debut_song.append(driver.find_element_by_class_name('debutsong').text)

    except:
        debut_song.append('')
# -

#수집한 데이터들을 각 컬럼별로 리스트에 담아서 데이터프레임으로 만들기
df4 = pd.DataFrame({'연도' : year,
                   '순위': rank,
                   '제목': title,
                   '가수' : singer,
                   '앨범' : album,
                   '좋아요 수' : like_count,
                   '발매일' : date_of_issue,
                   '장르' : genre,
                   '가사' : lyrics,
                   '작사/작곡/편곡' : three,
                   '팬수' : fan_count,
                   '멤버수' : member_count,
                   '솔로/그룹' : solor_group,
                   '성별' : gender,
                   '데뷔곡' : debut_song
                  })
df4

# 2월 데이터 프레임 합치기
result_2 = pd.concat([df3, df4], ignore_index=True)
result_2

# csv 파일로 저장
result_2.to_csv('Melon_2021_02.csv',encoding='utf-8-sig')

# 1~2월 데이터프레임 모두 합치기
result = pd.concat([df1, df2, df3, df4], ignore_index=True)
result

# csv 파일로 저장
result.to_csv('Melon_2021_01~02.csv',encoding='utf-8-sig')

# 확인
df_tot = pd.read_csv('Melon_2021_01~02.csv', index_col=0)
df_tot


