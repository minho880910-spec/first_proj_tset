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
    # 프롬프트를 더 명확하고 강제성 있게 수정
    prompt = f"""
    당신은 X(트위터) 트렌드 분석가입니다. 키워드 '{keyword}'에 대해 분석한 결과물만 JSON으로 응답하세요.
    
    1. 'emotional_words': '{keyword}'와 직접적으로 관련된 유저의 실제 형용사/명사 10개 (예: 맛있다, 비싸다, 품절 등)
    2. 'tips': '{keyword}' 이용자들에게 실질적으로 도움이 되는 팁 3개
    3. JSON 외에 다른 설명은 절대 하지 마세요.

    {{
      "hot_discussions": [],
      "x_sentiment": {{
        "sentiment_stats": [65, 20, 10, 5],
        "emotional_words": [],
        "satisfaction_score": 85,
        "tips": [
          {{ "title": "", "highlight": "", "desc": "" }},
          {{ "title": "", "highlight": "", "desc": "" }},
          {{ "title": "", "highlight": "", "desc": "" }}
        ]
      }}
    }}
    """
    
    data = generate_ai_json(prompt)
    
    # 1. 데이터가 아예 없을 때만 최소한의 기본 틀 생성
    if not data or not isinstance(data, dict):
        data = {"x_sentiment": {}}

    # 2. x_sentiment 구조 보장
    if "x_sentiment" not in data:
        data["x_sentiment"] = {}
    
    x_ai = data["x_sentiment"]

    # 3. [핵심] 감성 단어가 없거나 기본값이면 현재 검색어로 강제 생성
    # AI가 '단어1' 처럼 보냈거나 비어있을 경우를 대비
    bad_words = ["단어1", "단어2", "단어3", "단어4", "단어5"]
    e_words = x_ai.get("emotional_words", [])
    
    if not e_words or any(w in e_words for w in bad_words):
        x_ai["emotional_words"] = [
            f"{keyword}후기", f"{keyword}추천", f"{keyword}꿀팁", f"{keyword}이슈", 
            "실시간", "반응", "인기", "트렌드", "공유", "궁금"
        ]

    # 4. tips가 없으면 최소한 키워드 관련 문구라도 넣어서 유지 (전체 데이터를 버리지 않음)
    if not x_ai.get("tips") or not isinstance(x_ai.get("tips"), list):
        x_ai["tips"] = [
            {
                "title": f"{keyword} 정보 안내", 
                "highlight": f"{keyword} 분석 중", 
                "desc": f"'{keyword}'에 대한 실시간 유저 노하우를 AI가 정밀 분석하고 있습니다."
            }
        ]
        
    return data