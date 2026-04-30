import streamlit as st
import altair as alt
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
            st.markdown("#### 인기검색어", unsafe_allow_html=True)

    main_keyword = global_main_keyword if prompt_input else category
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword, category)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#0056b3'>{main_keyword}</span> 검색어 순위 근황 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            x_format = '%m-%d'
            df_time = main_data['time_series']
            chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=2).encode(
                x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
            st.markdown("#### 기기별 / 성별 / 연령별 비중 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            st.write("---")
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.caption("PC, 모바일")
                df_device = main_data['device_ratio'].copy()
                d1_range = ['#00c853', '#ff9800']
                device_chart = alt.Chart(df_device).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="value", type="quantitative"),
                    color=alt.Color(field="device", type="nominal", scale=alt.Scale(range=d1_range), legend=alt.Legend(title=None, orient="bottom")),
                    tooltip=['device', 'value']
                ).properties(height=250)
                st.altair_chart(device_chart, use_container_width=True)
                
            with subcol2:
                st.caption("성별")
                df_gender = main_data['gender_ratio']
                d2_range = ['#ff5252', '#448aff']
                gender_chart = alt.Chart(df_gender).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="value", type="quantitative"),
                    color=alt.Color(field="gender", type="nominal", scale=alt.Scale(range=d2_range), legend=alt.Legend(title=None, orient="bottom")),
                    tooltip=['gender', 'value']
                ).properties(height=250)
                st.altair_chart(gender_chart, use_container_width=True)
                
            with subcol3:
                st.caption("연령별")
                df_age = main_data['age_ratio']
                age_chart = alt.Chart(df_age).mark_bar(color='#448aff', size=15).encode(
                    x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0, grid=False)),
                    y=alt.Y('value:Q', title='', axis=None),
                    tooltip=['age', 'value']
                ).properties(height=250)
                st.altair_chart(age_chart, use_container_width=True)

        with keyword_related_container:
            st.markdown(f"#### <span style='color:#0056b3'>{main_keyword}</span> 연관 검색어 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #e8f5e9; border: 1px solid #c8e6c9;"
                text_color = "color: #333333;"
                num_color = "#2e7d32"
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color} margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries):
                    if q:
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{q}</span></div> </div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        with col2:
            queries = cat_data.get('top_queries', []) if cat_data and isinstance(cat_data, dict) else []
            
            if queries:
                html_bg2 = "background-color: #f9f9fc; border: 1px solid #e0e0e0;"
                num_color2 = "#0056b3"
                text_color = "color: #333333;"
                
                html_content = f"<div style='{html_bg2} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color}'>"
                for i, q in enumerate(queries):
                    if q:
                        html_content += f"<div style='margin-bottom: 10px; font-size: 15px;'><strong style='color: {num_color2}; width: 25px; display: inline-block;'>{i+1}</strong> <span>{q}</span></div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("인기 데이터가 없습니다.")
    elif main_data:
        st.write(main_data)
