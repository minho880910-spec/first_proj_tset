import streamlit as st
from modules.database import get_all_history, delete_history

def render_history():
    st.header("🕒 히스토리 내역")
    df = get_all_history()
    
    if df.empty:
        st.info("저장된 히스토리가 없습니다.")
    else:
        for index, row in df.iterrows():
            with st.expander(f"[{row['created_at']}] {row['category']} - {row['title']} ({row['tone']})"):
                st.write("**Instagram:**", row['instagram_content'])
                st.write("**Threads:**", row['threads_content'])
                st.write("**X:**", row['x_content'])
                
                if st.button("🗑️ 삭제", key=f"del_{row['id']}"):
                    delete_history(row['id'])
                    st.rerun()
