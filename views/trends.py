import streamlit as st

def render_trends():
    st.header("📈 키워드 트렌드 분석")
    st.write(st.session_state.trend_data)
