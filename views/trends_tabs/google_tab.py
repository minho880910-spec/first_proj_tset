import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    # 메인 키워드 설정
    main_keyword = global_main_keyword
    
    # 레이아웃 분할 (상단: 그래프와 연관어 / 하단: 지역별 순위와 FAQ)
    col1, col2 = st.columns([2.5, 1])
    st.write("---") # 구분선
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    # 통합 매니저로부터 데이터 호출
    # fetch_trend_data는 구글 실데이터가 없을 경우 네이버 검색 추이를 백업으로 가져옵니다.
    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if main_data:
        # --- [상단 왼쪽] 구글/네이버 관심도 변화 그래프 ---
        with col1:
            st.markdown(f"### <span style='color:#4285F4'>{main_keyword}</span> 관심도 변화 <span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1달</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#4285F4', strokeWidth=3).encode(
                    x=alt.X('date:T', title='날짜'),
                    y=alt.Y('clicks:Q', title='관심도 수치'),
                    tooltip=['date', 'clicks']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("시계열 데이터를 분석 중입니다.")

        # --- [상단 오른쪽] 연관 검색어 리스트 ---
        with col2:
            st.markdown(f"#### 🔍 {main_keyword} 연관 키워드")
            top_queries = main_data.get('top_queries', [])
            if top_queries:
                for i, q in enumerate(top_queries[:10]):
                    st.write(f"{i+1}. {q}")
            else:
                st.caption("연관된 키워드가 없습니다.")

        # --- [하단 왼쪽] 전국 지역별 관심도 랭킹 (AI 분석 데이터) ---
        with bot_col1:
            st.markdown(f"#### 📍 {main_keyword} 전국 랭킹 Top 5")
            df_region = main_data.get('region_ranking')
            
            if isinstance(df_region, pd.DataFrame) and not df_region.empty:
                # AI가 분석한 지역별 스코어를 차트로 렌더링합니다.
                region_chart = alt.Chart(df_region.head(5)).mark_bar(color='#FBBC05').encode(
                    x=alt.X('score:Q', title='관심도 점수'),
                    y=alt.Y('region:N', sort='-x', title='지역명'),
                    tooltip=['region', 'score']
                ).properties(height=250)
                st.altair_chart(region_chart, use_container_width=True)
            else:
                st.info("전국 지역별 트렌드 수치를 계산 중입니다.")

        # --- [하단 오른쪽] 함께 많이 찾는 질문 (FAQ) ---
        with bot_col2:
            st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓")
            # AI가 생성한 질문 리스트를 클릭 기능 없이 바로 노출합니다.
            faqs = main_data.get('faqs', [])
            if faqs:
                for i, faq in enumerate(faqs):
                    st.markdown(f"**Q{i+1}.** {faq}")
            else:
                st.info("관련 질문 데이터를 생성 중입니다.")
    else:
        st.warning("데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")