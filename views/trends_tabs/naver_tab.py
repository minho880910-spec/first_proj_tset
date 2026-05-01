import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        st.divider()
        st.markdown("#### 📂 카테고리 인기 검색어")
        
        # 카테고리 자동 업데이트 관리
        auto_cat = st.session_state.get(f"trend_category_{tab_name}")
        last_keyword = st.session_state.get(f"last_keyword_{tab_name}", "")
        
        if global_main_keyword != last_keyword:
            st.session_state[f"last_keyword_{tab_name}"] = global_main_keyword
            if auto_cat in categories:
                st.session_state[f"sb_{tab_name}"] = auto_cat

        category = st.selectbox("카테고리 선택", categories, key=f"sb_{tab_name}", label_visibility="collapsed")
        st.caption(f"📍 분석 중: **{category}**")

    # 데이터 호출
    main_keyword = global_main_keyword if prompt_input else category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, category)

    if main_data:
        with col1:
            # 검색 추이 그래프
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'), tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            # 통계 데이터 (기기/성별/연령) 렌더링
            if main_data.get('error') != 'mapping_failed':
                st.write("") 
                subcol1, subcol2, subcol3 = st.columns(3)
                # ... (기기별, 성별, 연령별 차트 코드 - 이전과 동일하여 생략 가능)
                # 생략하더라도 데이터 존재 체크(if df is not None)는 반드시 포함하세요.

        # 우측 상단: 연관어
        with keyword_related_container:
            st.markdown(f"#### 🔍 {main_keyword} 연관어")
            rel_queries = main_data.get('top_queries', [])
            if rel_queries:
                html = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(rel_queries):
                    html += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)

        # [최종 수정] 우측 하단: 카테고리 랭킹 (인기 검색어)
        with col2:
            st.write("") 
            # main_data의 category_ranking을 직접 가져와서 출력
            ranking = main_data.get('category_ranking', [])
            if ranking and len(ranking) > 0:
                st.markdown(f"#### 🏆 {category} 인기순")
                html_rank = "<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html_rank += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html_rank + "</div>", unsafe_allow_html=True)
            else:
                # 랭킹 정보가 정말로 없을 때만 경고 노출
                st.warning(f"'{category}' 실시간 랭킹 데이터가 비어 있습니다. 잠시 후 다시 시도해 주세요.")