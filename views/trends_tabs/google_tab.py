import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data
import base64
import os

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        
    with bot_col1:
        st.markdown("#### 지역별 관심도 분석 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        map_col, rank_col = st.columns([1, 1.2])
        with rank_col:
            st.markdown("#### 전국 랭킹 Top 5 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            rankings_container = st.container()
        with map_col:
            map_container = st.container()
            
    with bot_col2:
        st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓")
        faqs_container = st.container()

    # 데이터 가져오기
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#448aff'>{main_keyword}</span> 트렌드 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None:
                chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # 지도 이미지 로딩
        with map_container:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                map_path = os.path.join(project_root, "assets", "korea_map.png")

                if os.path.exists(map_path):
                    with open(map_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                        st.markdown(
                            f"<img src='data:image/png;base64,{encoded_string}' style='width: 100%; border-radius: 10px;'>", 
                            unsafe_allow_html=True
                        )
                else:
                    st.warning("📍 assets/korea_map.png 파일을 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"이미지 로딩 오류: {e}")

        # 지역 랭킹 렌더링
        with rankings_container:
            region_ranking = main_data.get('region_ranking')
            if region_ranking is not None and not region_ranking.empty:
                rank_html = "<div style='padding: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                for i, row in region_ranking.iterrows():
                    icon = "🔥 핫" if row['score'] > 75 else "☁️ 쿨"
                    rank_html += f"<div style='display: flex; justify-content: space-between; margin-bottom: 15px;'><div style='display:flex;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{row['region']} ({row['score']})</span></div> <span>{icon}</span></div>"
                rank_html += "</div>"
                st.markdown(rank_html, unsafe_allow_html=True)

        # FAQ 렌더링
        with faqs_container:
            faqs = main_data.get('faqs', [])
            if faqs:
                faq_html = "<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 350px; overflow-y: auto; color: #a9b1d6;'>"
                for faq in faqs:
                    faq_html += f"<div style='margin-bottom: 20px;'>• {faq}</div>"
                faq_html += "</div>"
                st.markdown(faq_html, unsafe_allow_html=True)