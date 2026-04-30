import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data
import base64

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword if prompt_input else "화장품/뷰티"
    
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

    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#448aff'>{main_keyword}</span> 트렌드 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            x_format = '%m-%d'
            df_time = main_data['time_series']
            chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=2).encode(
                x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)

        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#448aff'>{main_keyword}</span> 급상승 관련 검색어", unsafe_allow_html=True)
            
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                text_color = "color: #a9b1d6;"
                num_color = "#448aff"
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color} margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries[:7]):
                    if q:
                        count_html = f"<span style='color: #888888;'>{mock_counts[i % len(mock_counts)]}</span>"
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{q}</span></div> {count_html}</div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        with map_container:
            try:
                map_path = r"C:\Users\Donga\.gemini\antigravity\brain\c8658fd3-d8ee-4fcf-9575-be78ad0f6083\korea_map_heatmap_1777449063355.png"
                with open(map_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    st.markdown(f"<img src='data:image/png;base64,{encoded_string}' style='width: 100%; border-radius: 10px;'>", unsafe_allow_html=True)
            except Exception as e:
                st.info("지도 이미지를 불러올 수 없습니다.")

        with rankings_container:
            region_ranking = main_data.get('region_ranking')
            if region_ranking is not None and not region_ranking.empty:
                rank_html = f"<div style='background-color: transparent; padding: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                for i, row in region_ranking.iterrows():
                    icon = "🔥 핫" if row['score'] > 75 else "☁️ 쿨"
                    rank_html += f"<div style='display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{row['region']} ({row['score']})</span></div> <span style='font-size: 12px;'>{icon}</span></div>"
                rank_html += "</div>"
                st.markdown(rank_html, unsafe_allow_html=True)

        with faqs_container:
            faqs = main_data.get('faqs', [])
            if faqs:
                faq_html = f"<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 350px; overflow-y: auto; color: #a9b1d6;'>"
                for faq in faqs:
                    faq_html += f"<div style='margin-bottom: 25px; font-size: 15px; display: flex; justify-content: space-between; align-items: center;'><span>• {faq}</span></div>"
                faq_html += "</div>"
                st.markdown(faq_html, unsafe_allow_html=True)
            else:
                st.info("FAQ 데이터가 없습니다.")
    elif main_data:
        st.write(main_data)
