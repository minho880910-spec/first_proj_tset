import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data
import base64
import os

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    # 1. 레이아웃 설정
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        
    with bot_col1:
        st.markdown("#### 지역별 관심도 분석 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        map_col, rank_col = st.columns([1, 1.2])
        with rank_col:
            st.markdown("#### 전국 랭킹 Top 5", unsafe_allow_html=True)
            rankings_container = st.container()
        with map_col:
            map_container = st.container()
            
    with bot_col2:
        st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓", unsafe_allow_html=True)
        faqs_container = st.container()

    # 2. 데이터 가져오기
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        # --- [상단 왼쪽] 트렌드 추이 ---
        with col1:
            st.markdown(f"### <span style='color:#448aff'>{main_keyword}</span> 트렌드 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None:
                chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 급상승 관련 검색어 ---
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#448aff'>{main_keyword}</span> 급상승 관련어", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                html_content = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                for i, q in enumerate(main_queries[:7]):
                    html_content += f"<div style='display: flex; margin-bottom: 10px; font-size: 15px;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{q}</span></div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("연관 검색어가 없습니다.")

        # --- [하단 왼쪽] 지도 로딩 (경로 수정됨) ---
        with map_container:
            try:
                # 현재 파일: /mount/src/first_proj_test/views/google_tab.py
                current_dir = os.path.dirname(os.path.abspath(__file__)) # views 폴더
                project_root = os.path.dirname(current_dir) # first_proj_test (최상단)
                map_path = os.path.join(project_root, "assets", "korea_map.png")

                if os.path.exists(map_path):
                    with open(map_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode()
                        st.markdown(f"<img src='data:image/png;base64,{encoded}' style='width: 100%; border-radius: 10px;'>", unsafe_allow_html=True)
                else:
                    st.error(f"지도를 찾을 수 없습니다.")
                    # 디버깅용 (필요 없으면 삭제하세요)
                    st.caption(f"시도한 경로: {map_path}")
            except Exception as e:
                st.error("지도 로드 실패")

        # --- [하단 중앙] 전국 랭킹 ---
        with rankings_container:
            region_ranking = main_data.get('region_ranking')
            if region_ranking is not None and not region_ranking.empty:
                rank_html = "<div style='padding: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                for i, row in region_ranking.iterrows():
                    icon = "🔥 핫" if row['score'] > 75 else "☁️ 쿨"
                    rank_html += f"<div style='display: flex; justify-content: space-between; margin-bottom: 15px;'><div style='display:flex;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{row['region']} ({row['score']})</span></div> <span>{icon}</span></div>"
                rank_html += "</div>"
                st.markdown(rank_html, unsafe_allow_html=True)
            else:
                st.info("랭킹 데이터가 없습니다.")

        # --- [하단 오른쪽] FAQ ---
        with faqs_container:
            faqs = main_data.get('faqs', [])
            if faqs:
                faq_html = "<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 350px; overflow-y: auto; color: #a9b1d6;'>"
                for faq in faqs:
                    faq_html += f"<div style='margin-bottom: 20px;'>• {faq}</div>"
                faq_html += "</div>"
                st.markdown(faq_html, unsafe_allow_html=True)
            else:
                st.info("FAQ 데이터가 없습니다.")