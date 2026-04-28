import streamlit as st

def render_result():
    st.header("✨ 생성된 포스팅 결과")
    
    tab1, tab2, tab3 = st.tabs(["📸 Instagram", "💬 Threads", "🐦 X (Twitter)"])
    
    with tab1:
        st.subheader("Instagram 포스팅")
        st.text_area("내용", st.session_state.results.get('instagram', ''), height=300, key="ig_res")
        
    with tab2:
        st.subheader("Threads 포스팅")
        st.text_area("내용", st.session_state.results.get('threads', ''), height=300, key="th_res")
        
    with tab3:
        st.subheader("X (Twitter) 포스팅")
        st.caption("주의: X는 280자 제한이 있습니다.")
        x_content = st.session_state.results.get('x', '')
        st.text_area("내용", x_content, height=200, key="x_res")
        st.caption(f"글자 수: {len(x_content)}자")
