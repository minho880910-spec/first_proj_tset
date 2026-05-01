import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fetch_naver_search_trend_api(keyword):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    url = "https://openapi.naver.com/v1/datalab/search"

    if not client_id or not client_secret:
        return None

    # 데이터 범위 설정 (최근 30일)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # API 요청 본문 (이미지처럼 키워드 하나를 집중 분석)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": keyword, "keywords": [keyword]}
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
                
                # 시계열 데이터 생성
                df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
                
                # 나머지 비중 데이터는 현재 API 구조에 맞춰 형태만 유지
                return {
                    'time_series': df_time,
                    'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 30}, {'device': '모바일', 'value': 70}]),
                    'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 60}, {'gender': '남성', 'value': 40}]),
                    'age_ratio': pd.DataFrame([
                        {'age': '10-20대', 'value': 20}, {'age': '30대', 'value': 45}, 
                        {'age': '40대', 'value': 20}, {'age': '50대+', 'value': 15}
                    ]),
                    'top_queries': [f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 근황"]
                }
        return None
    except Exception:
        return None

def fetch_trend_data(tab_name, main_keyword, category=None):
    """
    render() 함수에서 호출하는 메인 데이터 로더
    """
    state_main_data = f"main_trend_data_{tab_name}"
    
    # Naver 탭일 경우 위에서 만든 검색 트렌드 API 호출
    if tab_name == "Naver":
        data = fetch_naver_search_trend_api(main_keyword)
        st.session_state[state_main_data] = data
        return data, None
    
    return None, None