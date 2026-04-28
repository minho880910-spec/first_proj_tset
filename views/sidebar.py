import streamlit as st
from modules.database import add_history
from modules.llm_engine import generate_content
from modules.trend_analyzer import get_trend_summary

def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <style>
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) {
                display: none;
            }
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button {
                background: transparent !important;
                border: transparent !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                justify-content: flex-start !important;
            }
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button:hover {
                background: transparent !important;
                border: transparent !important;
                box-shadow: none !important;
            }
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button:focus:not(:active) {
                border-color: transparent !important;
                box-shadow: none !important;
                color: inherit !important;
            }
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button p {
                font-size: 1.85rem !important;
                font-weight: 600 !important;
                margin: 0 !important;
                padding: 1.25rem 0px 1rem 0px !important;
                color: inherit;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="logo-btn-marker"></div>', unsafe_allow_html=True)
        if st.button("✨ 지피지기", key="logo_btn"):
            st.session_state.current_view = 'home'
        st.caption("포스팅 자동 생성기")
        st.write("---")

        categories = [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠"
        ]

        title = st.text_area("프롬프트 입력", placeholder="예: 신제품 립스틱 출시 홍보를 위한 인스타그램 글 작성해줘\n(자세한 타겟 고객이나 강조할 특징을 함께 적어주시면 더 좋습니다.)", height=150, key="prompt_input")

        st.write("---")
<<<<<<< Updated upstream
=======

        
        # Buttons
        if st.button("🏠 첫 화면으로", use_container_width=True):
            st.session_state.current_view = 'home'
            
        if st.button("📢 콘텐츠 제작", type="primary", use_container_width=True):
            if category and title:
                with st.spinner("콘텐츠를 생성 중입니다..."):
                    try:
                        st.session_state.last_keyword = title
                        results = generate_content(category, title, tone)
                        st.session_state.results = results
                        st.session_state.current_view = 'result'
                        # Save to history
                        add_history(category, title, tone, results.get('instagram', ''), results.get('threads', ''), results.get('x', ''))
                    except Exception as e:
                        if "AuthenticationError" in str(type(e)) or "Incorrect API key" in str(e):
                            st.error("OpenAI API 키가 올바르지 않습니다. .env 파일에 실제 API 키를 입력해주세요.")
                        else:
                            st.error(f"콘텐츠 생성 중 오류가 발생했습니다: {e}")
            else:
                st.warning("카테고리와 프롬프트를 모두 입력해주세요.")
                
        if st.button("📈 최신 트렌드", use_container_width=True):
            search_keyword = st.session_state.get('last_keyword', title)
            if search_keyword:
                with st.spinner(f"'{search_keyword}' 트렌드 데이터를 가져오는 중..."):
                    trend_data = get_trend_summary(search_keyword)
                    st.session_state.trend_data = trend_data
                    st.session_state.current_view = 'trends'
            else:
                st.warning("트렌드를 검색할 키워드를 입력하거나 콘텐츠를 먼저 생성해주세요.")
                

>>>>>>> Stashed changes
        st.markdown("### 📌 메뉴")
        if st.button("📢 콘텐츠 제작", use_container_width=True):
            st.session_state.current_view = 'result'
            if st.session_state.get("prompt_input"):
                st.session_state.auto_generate = True
            
        if st.button("🔥 인기 포스팅", use_container_width=True):
            st.session_state.current_view = 'popular'
            
        if st.button("📈 최신 트렌드", use_container_width=True):
            st.session_state.current_view = 'trends'

        if st.button("🕒 히스토리", use_container_width=True):
            st.session_state.current_view = 'history'
