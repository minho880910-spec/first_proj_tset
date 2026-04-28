import streamlit as st
from modules.database import add_history
from modules.llm_engine import generate_content
from modules.trend_analyzer import get_trend_summary

def render_sidebar():
    with st.sidebar:
        st.title("✨ 지피지기")
        st.caption("포스팅 자동 생성기")
        st.write("---")

        categories = [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠"
        ]
        category = st.selectbox("카테고리", categories)
        title = st.text_area("프롬프트 입력", placeholder="예: 신제품 립스틱 출시 홍보를 위한 인스타그램 글 작성해줘\n(자세한 타겟 고객이나 강조할 특징을 함께 적어주시면 더 좋습니다.)", height=150)
        
        tone = st.selectbox("톤앤매너", ["전문적인", "친근한", "유머러스한", "감성적인"])
        
        st.write("---")
        
        # Buttons
        if st.button("📢 콘텐츠 제작", type="primary", use_container_width=True):
            if category and title:
                with st.spinner("콘텐츠를 생성 중입니다..."):
                    results = generate_content(category, title, tone)
                    st.session_state.results = results
                    st.session_state.current_view = 'result'
                    # Save to history
                    add_history(category, title, tone, results.get('instagram', ''), results.get('threads', ''), results.get('x', ''))
            else:
                st.warning("카테고리와 프롬프트를 모두 입력해주세요.")
                
        if st.button("📈 최신 트렌드", use_container_width=True):
            if category:
                with st.spinner("트렌드 데이터를 가져오는 중..."):
                    trend_data = get_trend_summary(category)
                    st.session_state.trend_data = trend_data
                    st.session_state.current_view = 'trends'
            else:
                st.warning("트렌드를 검색할 카테고리를 입력해주세요.")
                
        if st.button("🕒 히스토리", use_container_width=True):
            st.session_state.current_view = 'history'
