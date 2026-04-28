import streamlit as st
from modules.database import get_all_history, delete_history, clear_all_history

def render_history():
    st.header("포스팅 생성 내역")
    
    # 데이터베이스에서 전체 내역을 불러옵니다.
    df = get_all_history()

    if df.empty:
        st.info("저장된 포스팅 생성 내역이 없습니다.")
    else:
        # 상단 영역: 전체 삭제 버튼 배치
        col1, col2 = st.columns([8, 2])
        with col2:
            # 실수 방지를 위해 '전체 내역 삭제'는 눈에 띄는 빨간색(primary)으로 설정
            if st.button("전체 내역 삭제", type="primary", use_container_width=True):
                clear_all_history()
                st.success("모든 내역이 삭제되었습니다.")
                st.rerun()

        st.divider()

        # 개별 히스토리 리스트 출력 
        for index, row in df.iterrows():
            # 날짜와 제목을 조합하여 아코디언 메뉴(Expander) 생성
            with st.expander(f"[{row['created_at']}] {row['category']} - {row['title']} ({row['tone']})"):
                
                # 1. 인스타그램 섹션
                st.markdown("#### 📸 Instagram")
                # st.code는 우측 상단에 자동으로 '복사 버튼'이 생성됩니다.
                st.code(row['instagram_content'], language=None)

                st.divider()

                # 2. 스레드 섹션
                st.markdown("#### 🧵 Threads")
                st.code(row['threads_content'], language=None)

                st.divider()

                # 3. X(트위터) 섹션
                st.markdown("#### 🐦 X (Twitter)")
                st.code(row['x_content'], language=None)

                st.divider()
                
                # 개별 삭제 버튼: 특정 ID의 기록만 삭제
                if st.button("이 기록 삭제", key=f"del_{row['id']}", help="해당 기록을 영구적으로 삭제합니다."):
                    delete_history(row['id'])
                    st.rerun()