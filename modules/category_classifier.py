import os
from openai import OpenAI
import streamlit as st

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
# OpenAI 클라이언트 인스턴스 생성
client = OpenAI(api_key=api_key)

def classify_category(keyword: str, categories: list) -> str:
    if not keyword:
        return "해당 카테고리 없음"
        
    categories_str = ", ".join(categories)
    system_prompt = (
        f"당신은 검색어 키워드를 다음 주어진 카테고리 중 하나로 분류하는 전문가입니다.\n"
        f"카테고리 목록: [{categories_str}]\n"
        f"사용자의 키워드가 위 카테고리 중 어디에 속하는지 판단하여, 오직 해당 카테고리 이름만 정확하게 출력하세요.\n"
        f"만약 키워드가 어느 카테고리에도 명확히 속하지 않는다면, '해당 카테고리 없음'이라고 출력하세요.\n"
        f"어떠한 설명이나 추가 문구 없이 카테고리명만 출력해야 합니다."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": keyword}
            ],
            temperature=0.1
        )
        category = response.choices[0].message.content.strip()
        category = category.replace('"', '').replace("'", "").rstrip('.')
        
        if category in categories:
            return category
        return "해당 카테고리 없음"
    except Exception as e:
        print(f"Category classification error: {e}")
        return "해당 카테고리 없음"
