import os
import json
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def get_fixed_category_ranking(category_name):
    """API 데이터 부재 시 출력할 카테고리별 고정 랭킹 데이터"""
    fixed_data = {
        "패션의류": ["원피스", "바람막이", "블라우스", "티셔츠", "올리비아로렌", "에고이스트", "남자반팔티", "잇미샤원피스", "럭키슈에뜨", "써스데이아일랜드"],
        "패션잡화": ["크록스", "슬리퍼", "나이키운동화", "양산", "백팩", "운동화", "크로스백", "안전화", "뉴발란스운동화", "아디다스운동화"],
        "화장품/미용": ["ahc아이크림", "선스틱", "헤라블랙쿠션", "선크림", "마데카크림", "설화수", "아모스컬링에센스", "세포랩", "샴푸", "썬크림"],
        "디지털/가전": ["냉장고", "노트북", "닌텐도스위치2", "모니터", "선풍기", "공기청정기", "제습기", "무선청소기", "음식물처리기", "키캡"],
        "가구/인테리어": ["화장대", "쇼파", "식탁의자", "침대프레임", "침대", "책상", "앞치마", "책상의자", "행거", "서랍장"],
        "출산/육아": ["레고", "포켓몬카드", "물티슈", "크록스키즈", "어린이날선물", "카네이션만들기", "키즈바람막이", "베베드피노", "돌반지", "다마고치"],
        "식품": ["쌀20kg", "닭가슴살", "오메가3", "쌀10kg", "마늘쫑", "참외", "창억떡", "콜라겐", "사과", "마그네슘"],
        "스포츠/레저": ["전기자전거", "등산화", "자전거", "트레킹화", "캠핑의자", "로드자전거", "원터치텐트", "파라솔", "자외선차단마스크", "무릎보호대"],
        "생활/건강": ["텀블러", "요소수", "스타벅스텀블러", "비데", "강아지사료", "빨래건조대", "어버이날이벤트", "카네이션", "식기건조대", "도시락통"],
        "여가/생활편의": ["부산요트투어", "대마도배편", "카네이션생화", "구글기프트카드", "혜화연극", "신세계상품권", "본죽메뉴", "이월드자유이용권", "크루즈여행", "메가커피메뉴"],
        "면세점": [],
        "도서": ["포켓몬생태도감", "베스트셀러", "흔한남매22", "자몽살구클럽", "안녕이라그랬어", "프로젝트헤일메리책", "열혈강호95권", "위버멘쉬", "엄마가유령이되었어", "니체의초월자"]
    }
    return fixed_data.get(category_name, [])

def generate_ai_estimates(keyword, category):
    """실데이터 부재 시 AI를 통해 논리적 예측 수치 생성 (UI 문구 미포함)"""
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category}'의 한국 트렌드를 분석해서 
    가장 개연성 있는 통계 데이터를 JSON으로 작성해줘. 
    15, 15, 15와 같은 고정값은 절대 사용하지 말고, 키워드 타겟층에 맞춰 비중을 조절해.
    예: '단팥빵'이라면 중장년층(40-50대) 비중을 높게 설정.
    
    형식:
    {{
        "device": {{"mo": 70, "pc": 30}},
        "gender": {{"f": 55, "m": 45}},
        "age": {{"10": 5, "20": 20, "30": 25, "40": 25, "50": 15, "60": 10}}
    }}
    * 모든 비중의 합은 100이어야 함.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "너는 한국 소비자 시장 데이터 분석가야."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

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

def fetch_naver_all_data(keyword, category_id, category_name):
    # 1. 공통 데이터 초기화
    related = get_naver_related_keywords(keyword)
    end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=32)).strftime('%Y-%m-%d')
    
    result = {'time_series': pd.DataFrame(), 'top_queries': related, 
              'device_ratio': None, 'gender_ratio': None, 'age_ratio': None, 'category_ranking': []}

    # 2. 검색 추이(시계열) 데이터 로드
    try:
        search_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", 
                       "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]}
        res_search = requests.post("https://openapi.naver.com/v1/datalab/search", 
                                   json=search_body, headers=get_naver_headers()).json()
        result['time_series'] = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except: pass

    # 3. 실시간 쇼핑 데이터 탐색 (3~10일 전 범위)
    found_real = False
    if category_id:
        for delay in range(3, 11):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            common_body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": category_id}
            try:
                r_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", 
                                      json=common_body, headers=get_naver_headers()).json()
                items = r_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    # 실데이터가 있으면 통계 정보도 로드
                    for ep in ["device", "gender", "age"]:
                        s_res = requests.post(f"https://openapi.naver.com/v1/datalab/shopping/category/{ep}", 
                                              json=common_body, headers=get_naver_headers()).json()
                        s_data = s_res.get('results', [{}])[0].get('data', [])
                        if s_data:
                            df = pd.DataFrame(s_data).rename(columns={'group': ep, 'ratio': 'value'})
                            if ep == "device": df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
                            if ep == "gender": df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
                            result[f'{ep}_ratio'] = df
                    found_real = True
                    break
            except: continue

    # 4. 실데이터 부재 시 처리 (AI 예측 수치 + 사용자 고정 랭킹)
    if not found_real or result['device_ratio'] is None:
        # (1) 랭킹은 사용자님이 지정하신 고정 리스트 사용
        result['category_ranking'] = get_fixed_category_ranking(category_name)
        
        # (2) 기기/성별/연령 비중은 AI가 논리적으로 생성
        ai_data = generate_ai_estimates(keyword, category_name)
        if ai_data:
            result['device_ratio'] = pd.DataFrame([
                {'device': '모바일', 'value': ai_data['device']['mo']},
                {'device': 'PC', 'value': ai_data['device']['pc']}
            ])
            result['gender_ratio'] = pd.DataFrame([
                {'gender': '여성', 'value': ai_data['gender']['f']},
                {'gender': '남성', 'value': ai_data['gender']['m']}
            ])
            result['age_ratio'] = pd.DataFrame([
                {'age': f"{k}대", 'value': v} for k, v in ai_data['age'].items()
            ])
    
    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid, category_name)
    st.session_state[state_key] = data
    return data, data