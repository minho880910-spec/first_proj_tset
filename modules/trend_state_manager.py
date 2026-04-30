import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from modules.trend_analyzer import get_trend_summary 

load_dotenv()

def get_naver_category_id(category_name):
    mapping = {
        "패션/의류": "50000000", "화장품/뷰티": "50000002", "IT/가전": "50000003",
        "식품/건강": "50000006", "인테리어/가구": "50000004", "여행/숙박": "50000009",
        "게임/엔터": "50000005", "교육/도서": "50000008", "출산/육아": "50000001",
        "반려동물 용품": "50000007", "취미/스포츠": "50000005"
    }
    return mapping.get(category_name, "50000000")

def fetch_naver_shopping_api(keyword, category_name=None):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    # 🛠️ 1. 엔드포인트 URL (공식 가이드 기준)
    url = "https://openapi.naver.com/v1/datalab/shopping/categories"

    if not client_id or not client_secret:
        return None

    cat_id = get_naver_category_id(category_name if category_name else keyword)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": [
            {"name": category_name if category_name else keyword, "param": [cat_id]}
        ]
    }

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            res = response.json()
            if 'results' in res and res['results']:
                data = res['results'][0]['data']
                if not data: return None
                df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
                return {
                    'time_series': df_time,
                    'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 30}, {'device': '모바일', 'value': 70}]),
                    'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 60}, {'gender': '남성', 'value': 40}]),
                    'age_ratio': pd.DataFrame([
                        {'age': '10-20대', 'value': 20}, {'age': '30대', 'value': 45}, 
                        {'age': '40대', 'value': 20}, {'age': '50대+', 'value': 15}
                    ]),
                    'top_queries': [f"{keyword} 인기 상품", f"{keyword} 추천"]
                }
        else:
            # 404 등 발생 시 대체 엔드포인트 시도
            fallback_url = "https://openapi.naver.com/v1/datalab/shopping/category/trend"
            res_fb = requests.post(fallback_url, json=body, headers=headers)
            if res_fb.status_code == 200:
                res = res_fb.json()
                data = res['results'][0]['data']
                df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
                return {'time_series': df_time, 'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 30}]), 'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 60}]), 'age_ratio': pd.DataFrame([{'age': '30대', 'value': 100}]), 'top_queries': [f"{keyword} 검색"]}
            
            return None
    except Exception as e:
        return None

def fetch_trend_data(tab_name: str, main_keyword: str, category: str = None, selected_period: str = "now 7-d"):
    # --- 1. 메인 데이터 캐싱 ---
    state_main_data = f"main_trend_data_{tab_name}"
    state_last_main = f"last_main_keyword_{tab_name}"
    state_last_period = f"last_period_{tab_name}"

    if (state_last_main not in st.session_state) or \
       (st.session_state[state_last_main] != main_keyword) or \
       (st.session_state.get(state_last_period) != selected_period) or \
       not st.session_state.get(state_main_data):
        
        with st.spinner(f"'{main_keyword}' 분석 중..."):
            if tab_name == "Naver":
                st.session_state[state_main_data] = fetch_naver_shopping_api(main_keyword, category)
            else:
                st.session_state[state_main_data] = get_trend_summary(main_keyword, period=selected_period, platform=tab_name)
            
            st.session_state[state_last_main] = main_keyword
            st.session_state[state_last_period] = selected_period

    # --- 2. 카테고리 데이터 캐싱 (오른쪽 사이드바용) ---
    state_cat_data = f"category_trend_data_{tab_name}"
    state_last_cat = f"last_trend_category_{tab_name}"

    if category:
        if (state_last_cat not in st.session_state) or \
           (st.session_state[state_last_cat] != category) or \
           not st.session_state.get(state_cat_data):
            
            if tab_name == "Naver":
                st.session_state[state_cat_data] = fetch_naver_shopping_api(category)
            else:
                # Naver 외 탭에서 카테고리 별도 분석이 필요한 경우
                st.session_state[state_cat_data] = get_trend_summary(category, period=selected_period, platform=tab_name)
            st.session_state[state_last_cat] = category

    return st.session_state.get(state_main_data), st.session_state.get(state_cat_data)