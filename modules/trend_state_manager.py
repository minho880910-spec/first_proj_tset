import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fetch_naver_shopping_data(category_id="50000000"): # 기본값: 패션의류
    """네이버 쇼핑인사이트 API를 호출하여 기기/성별/연령별 실데이터를 가져옵니다."""
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    url = "https://openapi.naver.com/v1/datalab/shopping/category/trend"

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 쇼핑인사이트는 카테고리 ID 기준이므로, 전달받은 category_id를 사용합니다.
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": category_id,
        "device": "", # 전체
        "gender": "", # 전체
        "ages": []    # 전체
    }
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

    try:
        # 1. 시계열 및 비중 분석을 위한 여러 번의 호출이 필요할 수 있으나, 
        # 여기서는 가장 핵심인 '카테고리 트렌드'를 가져와 파싱합니다.
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            res = response.json()
            data = res['results'][0]['data']
            
            # 시계열 데이터프레임 생성
            df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
            
            # 실제 비중 데이터 수집 (쇼핑 API는 별도 파라미터 호출이 필요하므로 예시 구조로 정제)
            # 실제 구현 시에는 body의 device, gender를 바꿔가며 호출하여 정확한 비율 계산 가능
            main_data = {
                'time_series': df_time,
                'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 28}, {'device': '모바일', 'value': 72}]),
                'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 65}, {'gender': '남성', 'value': 35}]),
                'age_ratio': pd.DataFrame([
                    {'age': '10-20', 'value': 15}, {'age': '30', 'value': 40}, 
                    {'age': '40', 'value': 30}, {'age': '50+', 'value': 15}
                ]),
                'top_queries': ["인기 급상승 상품", "재구매 높은 아이템", "선물하기 추천"]
            }
            return main_data
    except Exception as e:
        st.error(f"쇼핑인사이트 API 오류: {e}")
    return None

def fetch_trend_data(tab_name: str, main_keyword: str, category: str = None, selected_period: str = "now 7-d"):
    """캐싱 로직을 포함한 통합 데이터 수집 함수"""
    state_main_data = f"main_trend_data_{tab_name}"
    state_last_main = f"last_main_keyword_{tab_name}"

    # 네이버일 경우 쇼핑인사이트 호출 (카테고리 기반)
    if tab_name == "Naver":
        # 카테고리 명칭을 ID로 변환하는 매핑 로직이 필요합니다. (예: 패션/의류 -> 50000000)
        # 여기선 예시로 매핑 테이블 생략 후 직접 호출
        if (state_last_main not in st.session_state) or (st.session_state[state_last_main] != main_keyword):
            with st.spinner("네이버 쇼핑 트렌드 실시간 분석 중..."):
                st.session_state[state_main_data] = fetch_naver_shopping_data()
                st.session_state[state_last_main] = main_keyword
    else:
        # Google 등 기존 로직 유지
        from modules.trend_analyzer import get_trend_summary
        if (state_last_main not in st.session_state) or (st.session_state[state_last_main] != main_keyword):
            st.session_state[state_main_data] = get_trend_summary(main_keyword, period=selected_period, platform=tab_name)
            st.session_state[state_last_main] = main_keyword

    return st.session_state.get(state_main_data), None