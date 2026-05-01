import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def get_naver_category_id(category_name):
    """표준 카테고리 ID 매핑 (패션, 가전, 가구 등 포함)"""
    mapping = {
        "패션의류": "50000000", "패션잡화": "50000001", "화장품/미용": "50000002",
        "디지털/가전": "50000003", "가구/인테리어": "50000004", "출산/육아": "50000005",
        "식품": "50000006", "스포츠/레저": "50000007", "생활/건강": "50000008",
        "여가/생활편의": "50000009", "면세점": "50000010", "도서": "50000011"
    }
    return mapping.get(category_name)

def get_naver_related_keywords(keyword):
    """네이버 자동완성 API를 활용한 연관어 추출"""
    import urllib.parse
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://ac.search.naver.com/nx/ac?q={encoded_keyword}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items: return [item[0] for item in items[0]][:10]
    except: pass
    return []

def fetch_shopping_insight_data(endpoint, body):
    """쇼핑인사이트 API 호출 공통 함수"""
    url = f"https://openapi.naver.com/v1/datalab/shopping/category/{endpoint}"
    try:
        response = requests.post(url, json=body, headers=get_naver_headers(), timeout=10)
        if response.status_code == 200: return response.json()
    except: return None

def fetch_naver_all_data(keyword, category_id):
    """통합 검색 추이 + 쇼핑 데이터 + 랭킹 데이터 통합 추출"""
    # 1. 공통 정보 로드
    related = get_naver_related_keywords(keyword)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # 통합 검색어 추이 (Search API)
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {
        "startDate": start_date, "endDate": end_date, "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }
    try:
        res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
        df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except:
        df_time = pd.DataFrame()

    # 결과 객체 초기화
    result = {
        'time_series': df_time, 'top_queries': related,
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None, 'category_ranking': []
    }

    # 2. 카테고리 매핑 실패 시 처리
    if not category_id:
        result['error'] = 'mapping_failed'
        return result

    # 3. 쇼핑 인사이트 데이터 로드
    common_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "category": category_id}
    
    # 기기별
    res_dev = fetch_shopping_insight_data("device", common_body)
    if res_dev:
        df = pd.DataFrame(res_dev['results'][0]['data']).rename(columns={'group': 'device', 'ratio': 'value'})
        df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
        result['device_ratio'] = df

    # 성별
    res_gen = fetch_shopping_insight_data("gender", common_body)
    if res_gen:
        df = pd.DataFrame(res_gen['results'][0]['data']).rename(columns={'group': 'gender', 'ratio': 'value'})
        df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
        result['gender_ratio'] = df

    # 연령별
    res_age = fetch_shopping_insight_data("age", common_body)
    if res_age:
        result['age_ratio'] = pd.DataFrame(res_age['results'][0]['data']).rename(columns={'group': 'age', 'ratio': 'value'})

    # [중요] 카테고리 인기 검색어 실제 파싱
    res_rank = fetch_shopping_insight_data("keywords", common_body)
    if res_rank and 'results' in res_rank and res_rank['results']:
        result['category_ranking'] = [item['name'] for item in res_rank['results'][0]['data'][:10]]

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    """최종 탭 데이터 호출 함수"""
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid)
    if data:
        st.session_state[state_key] = data
        return data, data
    return None, None