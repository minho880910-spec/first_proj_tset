import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_json(prompt):
    """OpenAI API를 통해 구조화된 JSON 데이터를 생성하는 공통 유틸리티"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI JSON Generation Error: {e}")
        return None

def get_google_tab_ai_data(keyword):
    """Google 탭 전용: 전국 지역별 관심도와 FAQ 생성"""
    prompt = f"""
    키워드 '{keyword}'에 대한 한국 트렌드 분석 JSON을 생성해줘. 
    {{
      "region_ranking": [
        {{"region": "서울", "score": 100}},
        {{"region": "경기", "score": 85}},
        {{"region": "부산", "score": 70}},
        {{"region": "인천", "score": 60}},
        {{"region": "대구", "score": 50}}
      ],
      "faqs": ["질문1", "질문2", "질문3", "질문4", "질문5"]
    }}
    """
    data = generate_ai_json(prompt)
    if data and "region_ranking" in data and "faqs" in data:
        return data
    return {
        "region_ranking": [{"region": "서울", "score": 100}], 
        "faqs": [f"{keyword}의 주요 특징은?", f"{keyword} 관련 가장 인기 있는 정보는?"]
    }

def get_naver_tab_ai_data(keyword, category_name):
    """Naver 탭 전용: 기기/성별/연령별 인구통계 비중 생성"""
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category_name}'의 한국 내 검색 사용자 비중 JSON 생성.
    {{
      "demographics": {{
        "device": {{"mo": 75, "pc": 25}},
        "gender": {{"f": 55, "m": 45}},
        "age": {{"10": 10, "20": 25, "30": 30, "40": 20, "50": 10, "60": 5}}
      }}
    }}
    """
    data = generate_ai_json(prompt)
    # demographics 키가 있고 그 안에 필수 하위 키들이 있는지 확인
    if data and "demographics" in data:
        demo = data["demographics"]
        if all(k in demo for k in ["device", "gender", "age"]):
            return data
    return {
        "demographics": {
            "device": {"mo": 70, "pc": 30}, 
            "gender": {"f": 50, "m": 50}, 
            "age": {"20": 40, "30": 60}
        }
    }

def get_instagram_tab_ai_data(keyword, category_name):
    """Instagram 탭 전용: 해시태그를 제외한 미디어/성별/연령 비중 데이터만 생성"""
    prompt = f"""
    키워드 '{keyword}'와 인스타그램 카테고리 '{category_name}' 분석 JSON 생성.
    해시태그 데이터는 제외하고, 오직 아래의 인구통계 비중만 생성할 것:
    {{
      "demographics": {{
        "media_type": {{"image": 40, "video": 50, "carousel": 10}},
        "gender": {{"f": 60, "m": 40}},
        "age": {{"10": 15, "20": 35, "30": 25, "40": 15, "50": 10}}
      }}
    }}
    """
    data = generate_ai_json(prompt)
    if data and "demographics" in data:
        demo = data["demographics"]
        if all(k in demo for k in ["media_type", "gender", "age"]):
            return data
    return {
        "demographics": {
            "media_type": {"image": 40, "video": 40, "carousel": 20},
            "gender": {"f": 50, "m": 50},
            "age": {"20": 50, "30": 50}
        }
    }

def get_threads_tab_ai_data(keyword):
    """Threads 탭 전용: 텍스트 중심의 대화 및 인플루언서 분석"""
    prompt = f"""
    키워드 '{keyword}'에 대한 Threads(스레드) 반응 분석 JSON 생성.
    {{
      "hot_discussions": [
        {{"title": "핫토픽", "replies": 100, "quotes": 50, "handle": "@user", "author": "이름", "content": "내용"}}
      ],
      "top_influencers": [
        {{"rank": 1, "handle": "@id", "name": "이름", "mentions": 100, "followers": "10K"}}
      ]
    }}
    """
    data = generate_ai_json(prompt)
    if data and "hot_discussions" in data and "top_influencers" in data:
        return data
    return {"hot_discussions": [], "top_influencers": []}

def get_x_tab_ai_data(keyword):
    """X(Twitter) 탭 전용: 실시간성 분석 및 감성/꿀팁 데이터 생성"""

    prompt = f"""
    당신은 X(트위터) 트렌드 분석가입니다.

    반드시 아래 JSON 형식으로만 응답하세요.
    절대 다른 텍스트 포함 금지.

    {{
      "hot_discussions": [],
      "x_sentiment": {{
        "sentiment_stats": [65, 20, 10, 5],
        "emotional_words": ["긍정", "부정"],
        "satisfaction_score": 85,
        "tips": [
          {{ "title": "제목", "highlight": "핵심", "desc": "설명" }},
          {{ "title": "제목", "highlight": "핵심", "desc": "설명" }},
          {{ "title": "제목", "highlight": "핵심", "desc": "설명" }}
        ]
      }}
    }}

    조건:
    - emotional_words: '{keyword}' 관련 실제 표현 10개
    - tips: 반드시 3개 생성
    """

    data = generate_ai_json(prompt)

    # ----------------------------------
    # 1. 전체 구조 강제 생성 (🔥 핵심)
    # ----------------------------------
    if not data or not isinstance(data, dict):
        data = {}

    if "x_sentiment" not in data:
        data["x_sentiment"] = {}

    x_ai = data["x_sentiment"]

    # ----------------------------------
    # 2. sentiment_stats 보정
    # ----------------------------------
    if not isinstance(x_ai.get("sentiment_stats"), list):
        x_ai["sentiment_stats"] = [65, 20, 10, 5]

    # ----------------------------------
    # 3. emotional_words 강제 생성
    # ----------------------------------
    bad_words = ["단어1", "단어2", "단어3"]

    e_words = x_ai.get("emotional_words")

    if not e_words or not isinstance(e_words, list) or any(w in bad_words for w in e_words):
        x_ai["emotional_words"] = [
            f"{keyword}후기", f"{keyword}추천", f"{keyword}꿀팁",
            f"{keyword}논란", f"{keyword}반응",
            "실시간", "트렌드", "인기", "이슈", "공유"
        ]

    # ----------------------------------
    # 4. satisfaction_score 보정
    # ----------------------------------
    if not isinstance(x_ai.get("satisfaction_score"), (int, float)):
        x_ai["satisfaction_score"] = 80

    # ----------------------------------
    # 5. tips 무조건 3개 보장 (🔥 핵심)
    # ----------------------------------
    tips = x_ai.get("tips")

    if not tips or not isinstance(tips, list) or len(tips) < 3:
        x_ai["tips"] = [
            {
                "title": f"{keyword} 활용법",
                "highlight": f"{keyword} 빠르게 이해",
                "desc": f"{keyword} 관련 정보는 실시간 반응을 먼저 확인하세요."
            },
            {
                "title": f"{keyword} 체크포인트",
                "highlight": f"{keyword} 핵심 포인트",
                "desc": f"리뷰와 트렌드 키워드를 함께 보면 정확도가 올라갑니다."
            },
            {
                "title": f"{keyword} 꿀팁",
                "highlight": f"{keyword} 활용 전략",
                "desc": f"이슈 타이밍에 맞춰 검색하면 효과가 좋습니다."
            }
        ]

    return data