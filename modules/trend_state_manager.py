import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def get_naver_category_id(category_name):
    mapping = {
        "패션의류": "50000000", "패션잡화": "50000001", "화장품/미용": "50000002",
        "디지털/가전": "50000003", "가구/인테리어": "50000004", "출산/육아": "50000005",
        "식품": "50000006", "스포츠/레저": "50000007", "생활/건강": "50000008",
        "여가/생활편의": "50000009", "면세점": "50000010", "도서": "50000011"
    }
    return mapping.get(category_name)

def get_naver_related_keywords(keyword):
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

def fetch_naver_all_data(keyword, category_id):
    # 1. 공통 정보 세팅
    related = get_naver_related_keywords(keyword)
    
    # [수정] 랭킹 데이터를 가장 잘 가져오는 7일간의 범위로 설정
    end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d')
    
    # 검색 추이 (시계열)
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date",
                   "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]}
    try:
        res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
        df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except:
        df_time = pd.DataFrame()

    result = {
        'time_series': df_time, 'top_queries': related,
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None, 'category_ranking': []
    }

    if not category_id:
        result['error'] = 'mapping_failed'
        return result

    # 2. 쇼핑 인사이트 호출 (기기, 성별, 연령, 키워드랭킹)
    common_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "category": category_id}
    
    for ep in ["device", "gender", "age", "keywords"]:
        url = f"https://openapi.naver.com/v1/datalab/shopping/category/{ep}"
        try:
            resp = requests.post(url, json=common_body, headers=get_naver_headers(), timeout=10).json()
            if 'results' in resp and len(resp['results']) > 0:
                data = resp['results'][0].get('data', [])
                if not data: continue

                if ep == "device":
                    df = pd.DataFrame(data).rename(columns={'group': 'device', 'ratio': 'value'})
                    df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
                    result['device_ratio'] = df
                elif ep == "gender":
                    df = pd.DataFrame(data).rename(columns={'group': 'gender', 'ratio': 'value'})
                    df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
                    result['gender_ratio'] = df
                elif ep == "age":
                    result['age_ratio'] = pd.DataFrame(data).rename(columns={'group': 'age', 'ratio': 'value'})
                elif ep == "keywords":
                    # [핵심] 키워드 랭킹 추출 로직: name 필드를 리스트로 생성
                    result['category_ranking'] = [item.get('name') for item in data if 'name' in item][:10]
        except:
            continue

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid)
    if data:
        st.session_state[state_key] = data
        return data, data
    return None, None