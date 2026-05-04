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
    
    # AI가 단순히 예시를 복사하지 않고 실제 유저 반응을 분석하도록 프롬프트 강화
    prompt = f"""
    키워드 '{keyword}'에 대한 X(트위터) 실시간 반응 분석 JSON을 생성해줘.
    
    [중요 지시사항]
    1. 'emotional_words' 배열에는 반드시 '{keyword}'와 관련된 실제 유저들의 리뷰, 감정, 장단점, 핵심 특징을 나타내는 단어를 10개 채울 것.
    2. '좋음', '나쁨' 같은 단순한 단어보다 '노이즈캔슬링', '발열', '조리시간', '디자인' 등 검색어 특화 키워드를 우선할 것.
    3. 예시로 제공된 형식을 그대로 복사(예: {keyword}특징1)하지 말고, 실제 분석된 단어로 교체할 것.

    {{
      "hot_discussions": [
        {{
          "title": "실시간 트렌드 토픽",
          "replies": 150,
          "quotes": 80,
          "handle": "@trend_searcher",
          "author": "트렌드분석가",
          "content": "실제 트위터에서 논의되는 '{keyword}' 관련 내용을 요약해서 작성"
        }}
      ],
      "x_sentiment": {{
        "sentiment_stats": [60, 20, 15, 5],
        "emotional_words": ["키워드관련단어1", "단어2", "단어3", "단어4", "단어5", "단어6", "단어7", "단어8", "단어9", "단어10"],
        "satisfaction_score": 85,
        "tips": [
          {{
            "title": "실시간 유저 팁",
            "highlight": "구매/사용 시 핵심 포인트",
            "desc": "유저들이 입을 모아 말하는 구체적인 노하우"
          }},
          {{
            "title": "연관 노하우",
            "highlight": "놓치기 쉬운 꿀팁",
            "desc": "제품이나 서비스를 더 효과적으로 사용하는 방법"
          }}
        ]
      }}
    }}
    """
    
    data = generate_ai_json(prompt)
    
    # 데이터 검증 및 Fallback(기본값) 로직 - 키워드 맞춤형 기본값 생성
    if not data or "x_sentiment" not in data or "tips" not in data.get("x_sentiment", {}):
        return {
            "hot_discussions": [],
            "x_sentiment": {
                "sentiment_stats": [40, 30, 20, 10],
                # 기본값도 오밀조밀한 클러스터를 위해 10개 구성
                "emotional_words": [f"{keyword}리뷰", "성능", "디자인", "가성비", "추천", "이슈", "실사용후기", "필수템", "꿀팁", "반응"],
                "satisfaction_score": 80,
                "tips": [
                    {
                        "title": "데이터 분석 중", 
                        "highlight": f"{keyword} 정보 수집 중", 
                        "desc": "실시간 트렌드 데이터를 처리하고 있습니다. 잠시만 기다려주세요."
                    }
                ]
            }
        }
    return data