import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        st.divider()
        cat_col, title_col = st.columns([1, 1])
        with cat_col:
            category = st.selectbox("카테고리 선택", categories, key=f"trend_category_{tab_name}", label_visibility="collapsed")
            st.caption("최근 1주일 기준")
        with title_col:
            st.markdown("#### 인기 해시태그", unsafe_allow_html=True)

    main_keyword = global_main_keyword if prompt_input else category
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword, category)

    # main_data가 존재하고 딕셔너리 형태일 때만 실행
    if main_data and isinstance(main_data, dict):
        # 매핑 실패 에러가 있을 경우 경고 표시
        if main_data.get('error') == 'mapping_failed':
            with col1:
                st.warning(f"⚠️ '{category}' 카테고리는 인스타그램 분석 매핑을 지원하지 않습니다.")

        with col1:
            st.markdown(f"### <span style='color:#00E5FF'>{main_keyword}</span> 해시태그 언급량 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            # 1. 시계열 차트 안전하게 그리기
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                x_format = '%m-%d'
                chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("언급량 데이터가 없습니다.")
            
            st.markdown("#### 인게이지먼트 / 성별 / 연령별 비중 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            st.write("---")
            subcol1, subcol2, subcol3 = st.columns(3)
            
            # 2. 미디어 유형 (device_ratio) 안전하게 그리기
            with subcol1:
                st.caption("미디어 유형")
                raw_device = main_data.get('device_ratio')
                if raw_device is not None and not raw_device.empty:
                    df_device = raw_device.copy()
                    # 데이터 개수가 맞지 않을 경우를 대비한 처리
                    labels = ['릴스', '사진/게시물']
                    df_device['device'] = labels[:len(df_device)]
                    d1_range = ['#00FF00', '#FF00FF']
                    device_chart = alt.Chart(df_device).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="device", type="nominal", scale=alt.Scale(range=d1_range), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=['device', 'value']
                    ).properties(height=250)
                    st.altair_chart(device_chart, use_container_width=True)
                else:
                    st.write("데이터 없음")
                
            # 3. 성별 (gender_ratio) 안전하게 그리기
            with subcol2:
                st.caption("성별")
                df_gender = main_data.get('gender_ratio')
                if df_gender is not None and not df_gender.empty:
                    d2_range = ['#FF00FF', '#448aff']
                    gender_chart = alt.Chart(df_gender).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="gender", type="nominal", scale=alt.Scale(range=d2_range), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=['gender', 'value']
                    ).properties(height=250)
                    st.altair_chart(gender_chart, use_container_width=True)
                else:
                    st.write("데이터 없음")
                
            # 4. 연령별 (age_ratio) 안전하게 그리기
            with subcol3:
                st.caption("연령별")
                df_age = main_data.get('age_ratio')
                if df_age is not None and not df_age.empty:
                    age_chart = alt.Chart(df_age).mark_bar(color='#00E5FF', size=15).encode(
                        x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0, grid=False)),
                        y=alt.Y('value:Q', title='', axis=None),
                        tooltip=['age', 'value']
                    ).properties(height=250)
                    st.altair_chart(age_chart, use_container_width=True)
                else:
                    st.write("데이터 없음")

        # 우측 레이아웃 렌더링
        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        
        with keyword_related_container:
            st.markdown(f"#### 📸 <span style='color:#00E5FF'>{main_keyword}</span> 연관 해시태그 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            if main_queries:
                html_bg = "background-color: transparent;"
                num_color = "#00E5FF"
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: inherit; margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries):
                    if q:
                        display_q = f"#{q.replace(' ', '')}"
                        count_html = f"<span style='color: #888888;'>{mock_counts[i % len(mock_counts)]}</span>"
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{display_q}</span></div> {count_html}</div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        with col2:
            st.write("")
            queries = cat_data.get('top_queries', []) if cat_data and isinstance(cat_data, dict) else []
            if queries:
                html_bg2 = "background-color: transparent;"
                num_color2 = "#00E5FF"
                html_content = f"<div style='{html_bg2} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: inherit;'>"
                for i, q in enumerate(queries):
                    if q:
                        display_q = f"#{q.replace(' ', '')}"
                        html_content += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color2}; width: 25px;'>{i+1}</strong> <span>{display_q}</span></div> </div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("인기 데이터가 없습니다.")

    elif main_data:
        # 데이터가 딕셔너리가 아닌 경우 예외 디스플레이
        st.write("데이터 형식이 올바르지 않습니다.")