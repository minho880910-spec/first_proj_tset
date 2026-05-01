import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    # 1. 레이아웃 분할
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        st.divider()
        st.markdown("#### 📂 카테고리 선택", unsafe_allow_html=True)
        cat_col, _ = st.columns([1, 0.1])
        with cat_col:
            # AI 분류 결과 반영
            auto_cat = st.session_state.get(f"trend_category_{tab_name}", categories[0])
            try:
                # 선택된 카테고리가 목록에 없을 경우를 위한 안전장치
                default_idx = categories.index(auto_cat) if auto_cat in categories else 0
            except:
                default_idx = 0
            
            category = st.selectbox(
                "카테고리 선택", 
                categories, 
                index=default_idx, 
                key=f"sb_{tab_name}", 
                label_visibility="collapsed"
            )
            st.caption("네이버 쇼핑인사이트 기준")

    # 2. 데이터 가져오기
    main_keyword = global_main_keyword if prompt_input else category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, category)

    if main_data:
        # [에러 처리] 매핑 실패 시 경고 노출 후 연관어만 출력하고 종료
        if main_data.get('error') == 'mapping_failed':
            with col1:
                st.warning(f"⚠️ '{category}' 카테고리 매핑에 실패했습니다.")
                st.info("trend_state_manager.py의 매핑 테이블에 해당 카테고리명이 정확히 등록되어 있는지 확인해주세요.")
            
            with col2:
                st.markdown(f"#### 🔍 {main_keyword} 연관어", unsafe_allow_html=True)
                queries = main_data.get('top_queries', [])
                if queries:
                    html = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                    for i, q in enumerate(queries):
                        html += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                    st.markdown(html + "</div>", unsafe_allow_html=True)
                st.caption("매핑 실패로 인해 랭킹 정보를 불러올 수 없습니다.")
            return

        # 3. 정상 데이터 렌더링 (좌측 영역)
        with col1:
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1개월 기준</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'),
                    tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            st.write("") 
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.caption("💻 기기별 (PC/모바일)")
                df_dev = main_data.get('device_ratio')
                if df_dev is not None:
                    c = alt.Chart(df_dev).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("device:N", scale=alt.Scale(range=['#00c853', '#ff9800'])), tooltip=['device', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol2:
                st.caption("👫 성별 비중")
                df_gen = main_data.get('gender_ratio')
                if df_gen is not None:
                    c = alt.Chart(df_gen).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("gender:N", scale=alt.Scale(range=['#448aff', '#ff5252'])), tooltip=['gender', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol3:
                st.caption("🎂 연령별 비중")
                df_age = main_data.get('age_ratio')
                if df_age is not None:
                    c = alt.Chart(df_age).mark_bar(color='#448aff').encode(
                        x=alt.X('age:N', title=None, axis=alt.Axis(labelAngle=0)), # 연령대 age 제목 제거 및 수평 고정
                        y=alt.Y('value:Q', axis=None), 
                        tooltip=['age', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)

        # 4. 우측 실시간 정보 (연관어 및 랭킹)
        with keyword_related_container:
            st.markdown(f"#### 🔍 {main_keyword} 연관어", unsafe_allow_html=True)
            rel_queries = main_data.get('top_queries', [])
            if rel_queries:
                html = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(rel_queries):
                    html += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)

        with col2:
            st.write("") 
            ranking = main_data.get('category_ranking', [])
            if ranking:
                st.markdown(f"#### 🏆 {category} 인기순", unsafe_allow_html=True)
                html2 = "<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html2 += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html2 + "</div>", unsafe_allow_html=True)
            else:
                st.info(f"'{category}' 랭킹 정보가 없습니다.")