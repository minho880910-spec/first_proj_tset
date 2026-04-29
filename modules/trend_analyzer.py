from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import datetime, timedelta
import random

def get_trend_summary(keyword, period='today 1-m', platform='Google'):
    """
    Fetches Google Trends related queries and time series for the given keyword.
    If pytrends fails or data is insufficient, returns mock data for UI demonstration.
    """
    if not keyword:
        return None

    # Default Mock Data structure
    end_date = datetime.now()
    
    if period == 'now 1-d':
        dates = [(end_date - timedelta(hours=i)).strftime('%Y-%m-%d %H:00:00') for i in range(23, -1, -1)]
        mock_len = 24
    elif period == 'now 7-d':
        dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d 00:00:00') for i in range(6, -1, -1)]
        mock_len = 7
    elif period == 'today 12-m':
        dates = [(end_date - timedelta(days=i*30)).strftime('%Y-%m-%d 00:00:00') for i in range(11, -1, -1)]
        mock_len = 12
    else: # 'today 1-m'
        dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d 00:00:00') for i in range(29, -1, -1)]
        mock_len = 30
        
    data = {
        "status": "success",
        "keyword": keyword,
        "time_series": pd.DataFrame({
            'date': dates,
            'clicks': [random.randint(30, 100) for _ in range(mock_len)]
        }),
        "device_ratio": pd.DataFrame({
            'device': ['Mobile', 'PC'],
            'value': [87, 13]
        }),
        "gender_ratio": pd.DataFrame({
            'gender': ['여성', '남성'],
            'value': [74, 26]
        }),
        "age_ratio": pd.DataFrame({
            'age': ['10대', '20대', '30대', '40대', '50대', '60대'],
            'value': [5, 20, 25, 40, 30, 15]
        }),
        "top_queries": [
            f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 신상", f"{keyword} 브랜드", f"{keyword} 비교",
            f"{keyword} 가격", f"{keyword} 후기", f"{keyword} 팁", f"{keyword} 세일", f"{keyword} 리뷰",
            f"인기 {keyword}", f"{keyword} 선물", f"{keyword} 트렌드", f"{keyword} 매장", f"{keyword} 이벤트",
            f"{keyword} 랭킹", f"가성비 {keyword}", f"{keyword} 방법", f"{keyword} 모음", f"{keyword} 신제품"
        ],
        "region_ranking": pd.DataFrame({
            'region': ['서울특별시', '경기도', '부산광역시', '대구광역시', '인천광역시'],
            'score': [100, 92, 81, 78, 74]
        }),
        "faqs": [
            f"{keyword}은(는) 어떤 맛인가요?",
            f"{keyword} 칼로리는 얼마나 되나요?",
            f"맛있는 {keyword}을(를) 만드는 레시피가 있나요?",
            f"서울에 유명한 {keyword} 맛집 추천해주세요.",
            f"{keyword}을(를) 에어프라이어로 구워 먹어도 되나요?"
        ],
        "hot_discussions": [
            {
                "title": f"{keyword} 맛의 비밀 (버터 vs 소금)",
                "replies": 385, "quotes": 120, "likes": 850,
                "handle": "@foodie_seoul", "author": "맛집 가이드",
                "content": f"그냥 짠이 왔던 {keyword} 없이 뇌가 짭짤 소금하는 요금만하게 지향합니다.",
                "time": "2일"
            },
            {
                "title": f"{keyword} 칼로리, 의외로 높다 vs 낮다",
                "replies": 310, "quotes": 95, "likes": 600,
                "handle": "@diet_honey", "author": "다이어트 정보",
                "content": f"{keyword} 칼로리, 의외로 높다 vs 낮다<br>기 잘다",
                "time": "2일"
            },
            {
                "title": f"줄 서서 먹을 가치가 있는가? (런베뮤 {keyword})",
                "replies": 250, "quotes": 80, "likes": 450,
                "handle": "@baking_king_t", "author": "베이킹 전문가",
                "content": f"줄 서서 먹을 가치가 있는가? (런베뮤 {keyword})<br>이 심쿵은 또 발뗐보네요.",
                "time": "22일"
            }
        ],
        "top_influencers": [
            {"rank": 1, "handle": "@baking_king_t", "name": "베이킹 전문가", "mentions": "450회", "followers": "2.5만"},
            {"rank": 2, "handle": "@foodie_seoul", "name": "맛집 가이드", "mentions": "380회", "followers": "1.8만"},
            {"rank": 3, "handle": "@diet_honey", "name": "다이어트 정보", "mentions": "290회", "followers": "1.2만"},
            {"rank": 4, "handle": "@dessert_tour", "name": "디저트 투어", "mentions": "210회", "followers": "9k"},
            {"rank": 5, "handle": "@k_culture_snack", "name": "한국 간식 문화", "mentions": "180회", "followers": "7k"}
        ]
    }

    if platform == 'Google':
        try:
            pytrend = TrendReq(hl='ko-KR', tz=540)
            
            # Build payload
            pytrend.build_payload(kw_list=[keyword], timeframe=period, geo='KR')
            
            # Get interest over time
            iot = pytrend.interest_over_time()
            if not iot.empty:
                iot = iot.reset_index()
                iot.rename(columns={'date': 'date', keyword: 'clicks'}, inplace=True)
                iot['date'] = iot['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                data["time_series"] = iot[['date', 'clicks']]
                
            # Get related queries
            related_queries = pytrend.related_queries()
            if keyword in related_queries and related_queries[keyword]['top'] is not None:
                top_df = related_queries[keyword]['top']
                top_queries = top_df['query'].tolist()[:20]
                if top_queries:
                    data["top_queries"] = top_queries + [""] * (20 - len(top_queries))
                    
        except Exception as e:
            # Fallback to mock data on error (like rate limit)
            pass

    return data
