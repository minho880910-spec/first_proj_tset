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
    related = get_naver_related_keywords(keyword)
    
    # 1. 시계열 데이터는 어제 날짜 기준으로 시도
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
    
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

    # 2. 쇼핑 인사이트 (랭킹 및 통계) - 데이터가 나올 때까지 날짜를 뒤로 밀며 시도
    # 어제(1일 전)부터 최대 7일 전까지 탐색
    for delay in range(1, 8):
        target_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
        common_body = {"startDate": target_date, "endDate": target_date, "timeUnit": "date", "category": category_id}
        
        url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
        try:
            resp = requests.post(url, json=common_body, headers=get_naver_headers()).json()
            data = resp.get('results', [{}])[0].get('data', [])
            if data:
                result['category_ranking'] = [item.get('name') for item in data if 'name' in item][:10]
                
                # 랭킹을 찾았다면 해당 날짜 기준으로 통계 데이터도 가져옴
                for ep in ["device", "gender", "age"]:
                    s_url = f"https://openapi.naver.com/v1/datalab/shopping/category/{ep}"
                    s_res = requests.post(s_url, json=common_body, headers=get_naver_headers()).json()
                    s_data = s_res.get('results', [{}])[0].get('data', [])
                    if s_data:
                        df = pd.DataFrame(s_data).rename(columns={'group': ep, 'ratio': 'value'})
                        if ep == "device": df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
                        if ep == "gender": df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
                        result[f'{ep}_ratio'] = df
                break # 데이터 찾기 성공 시 루프 종료
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