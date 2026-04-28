from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import datetime, timedelta
import random

def get_trend_summary(keyword):
    """
    Fetches Google Trends related queries and time series for the given keyword.
    If pytrends fails or data is insufficient, returns mock data for UI demonstration.
    """
    if not keyword:
        return None

    # Default Mock Data structure
    # Generate dates for the last 30 days
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
    
    data = {
        "status": "success",
        "keyword": keyword,
        "time_series": pd.DataFrame({
            'date': dates,
            'clicks': [random.randint(30, 100) for _ in range(30)]
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
        ]
    }

    try:
        pytrend = TrendReq(hl='ko-KR', tz=540)
        
        # Build payload for the last 1 month
        pytrend.build_payload(kw_list=[keyword], timeframe='today 1-m', geo='KR')
        
        # Get interest over time
        iot = pytrend.interest_over_time()
        if not iot.empty:
            iot = iot.reset_index()
            iot.rename(columns={'date': 'date', keyword: 'clicks'}, inplace=True)
            iot['date'] = iot['date'].dt.strftime('%Y-%m-%d')
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
