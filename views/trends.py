import streamlit as st
from modules.keyword_extractor import extract_keyword
from modules.category_classifier import classify_category
from views.trends_tabs import naver_tab, google_tab, instagram_tab, threads_tab, x_twitter_tab

def render_trends():
    st.header("📈 최신 트렌드")
    
    categories_dict = {
        "Instagram": [
            "패션 및 스타일", "음식 및 음료", "여행", "엔터테인먼트", 
            "운동 및 건강", "예술 및 디자인", "반려동물", "비즈니스 및 기술", "해당 카테고리 없음"
        ],
        "default": [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠", "해당 카테고리 없음"
        ]
    }
    
    prompt_input = st.session_state.get("prompt_input", "").strip()
    global_main_keyword = None
    
    if prompt_input:
        if ('last_prompt_for_keyword' not in st.session_state) or (st.session_state.last_prompt_for_keyword != prompt_input):
            with st.spinner("프롬프트에서 핵심 키워드 및 카테고리 분석 중..."):
                extracted_keyword = extract_keyword(prompt_input)
                st.session_state.extracted_keyword = extracted_keyword
                
                mapped_categories = {}
                for key, cats in categories_dict.items():
                    mapped_categories[key] = classify_category(extracted_keyword, cats[:-1])
                
                for t in ["Naver", "Instagram"]:
                    cat_key = "Instagram" if t == "Instagram" else "default"
                    st.session_state[f"trend_category_{t}"] = mapped_categories[cat_key]
                    
                st.session_state.last_prompt_for_keyword = prompt_input
                
        global_main_keyword = st.session_state.extracted_keyword

    tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
    tabs = st.tabs(tab_names)
    
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            if tab_name == "Naver":
                naver_tab.render(tab_name, categories_dict["default"], prompt_input, global_main_keyword)
            elif tab_name == "Instagram":
                instagram_tab.render(tab_name, categories_dict["Instagram"], prompt_input, global_main_keyword)
            elif tab_name == "Google":
                google_tab.render(tab_name, prompt_input, global_main_keyword)
            elif tab_name == "Threads":
                threads_tab.render(tab_name, prompt_input, global_main_keyword)
            elif tab_name == "X (Twitter)":
                x_twitter_tab.render(tab_name, prompt_input, global_main_keyword)
