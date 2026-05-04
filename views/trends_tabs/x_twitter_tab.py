import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data


# --------------------------------------
# 🔥 데이터 강제 보정 함수 (핵심)
# --------------------------------------
def normalize_x_data(main_data, keyword):
    if not main_data or not isinstance(main_data, dict):
        main_data = {}

    # x_sentiment 구조 확보
    x_ai = main_data.get("x_sentiment", {})

    if not isinstance(x_ai, dict):
        x_ai = {}

    # sentiment_stats
    if not isinstance(x_ai.get("sentiment_stats"), list):
        x_ai["sentiment_stats"] = [65, 20, 10, 5]

    # emotional_words
    if not x_ai.get("emotional_words"):
        x_ai["emotional_words"] = [
            f"{keyword}후기", f"{keyword}추천", f"{keyword}꿀팁",
            f"{keyword}논란", f"{keyword}반응",
            "실시간", "트렌드", "인기", "이슈", "공유"
        ]

    # satisfaction_score
    if not isinstance(x_ai.get("satisfaction_score"), (int, float)):
        x_ai["satisfaction_score"] = 80

    # tips (무조건 3개)
    tips = x_ai.get("tips")
    if not tips or not isinstance(tips, list) or len(tips) < 3:
        x_ai["tips"] = [
            {
                "title": f"{keyword} 활용법",
                "highlight": f"{keyword} 빠르게 이해",
                "desc": f"{keyword} 관련 정보는 실시간 반응을 먼저 확인하세요."
            },
            {
                "title": f"{keyword} 체크포인트",
                "highlight": f"{keyword} 핵심 포인트",
                "desc": f"리뷰와 트렌드를 함께 보면 정확도가 올라갑니다."
            },
            {
                "title": f"{keyword} 꿀팁",
                "highlight": f"{keyword} 활용 전략",
                "desc": f"이슈 타이밍에 맞춰 검색하면 효과가 좋습니다."
            }
        ]

    # 다시 넣기
    main_data["x_sentiment"] = x_ai

    return main_data


# --------------------------------------
# 🔥 메인 렌더 함수
# --------------------------------------
def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    keyword = global_main_keyword

    # --------------------------------------
    # 1. 데이터 가져오기
    # --------------------------------------
    try:
        main_data, _ = fetch_trend_data(tab_name, keyword)
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
        main_data = {}

    # 🔥 무조건 데이터 보정
    main_data = normalize_x_data(main_data, keyword)

    # 🔥 디버깅 (필요하면 켜라)
    # st.write("DEBUG:", main_data)

    x_ai = main_data["x_sentiment"]

    # --------------------------------------
    # 2. 레이아웃
    # --------------------------------------
    left_col, right_col = st.columns([2, 1], gap="large")

    # ======================================
    # 🔵 LEFT
    # ======================================
    with left_col:

        st.markdown(f"### <span style='color:#4fc3f7'>{keyword}</span> 트렌드 추이", unsafe_allow_html=True)

        df_time = main_data.get("time_series")

        if isinstance(df_time, pd.DataFrame) and not df_time.empty:
            chart = alt.Chart(df_time).mark_area(
                line={'color': '#00E5FF'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#00E5FF', offset=0),
                        alt.GradientStop(color='transparent', offset=1)
                    ],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('clicks:Q')
            ).properties(height=300)

            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("트렌드 데이터 없음")

        st.markdown("<br>", unsafe_allow_html=True)

        # --------------------------------------
        # 감성 분석
        # --------------------------------------
        st.markdown("#### 정보 공유 및 감성 분석 지도")

        s_stats = x_ai["sentiment_stats"]
        e_words = x_ai["emotional_words"]
        s_score = x_ai["satisfaction_score"]

        sc1, sc2, sc3 = st.columns([1, 1.8, 1])

        # -----------------------
        # 성향
        # -----------------------
        with sc1:
            st.markdown("##### 게시물 성향")

            st.markdown(f"""
            <div style='width:100px;height:100px;margin:auto;border-radius:50%;
            background:conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% 85%, #448aff 85% 100%);
            display:flex;align-items:center;justify-content:center;'>

            <div style='width:70px;height:70px;background:#1a1b26;border-radius:50%;
            display:flex;align-items:center;justify-content:center;color:#00E5FF;font-weight:bold;'>

            {s_stats[0]}%
            </div></div>
            """, unsafe_allow_html=True)

        # -----------------------
        # 감성 클러스터
        # -----------------------
        with sc2:
            st.markdown("##### 감성 클러스터")

            bubble_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;justify-content:center;'>"

            colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6"]

            for i, word in enumerate(e_words[:10]):
                c = colors[i % 4]
                bubble_html += f"<span style='color:{c};border:1px solid {c};padding:4px 8px;border-radius:12px;font-size:12px'>{word}</span>"

            bubble_html += "</div>"

            st.markdown(bubble_html, unsafe_allow_html=True)

        # -----------------------
        # 만족도
        # -----------------------
        with sc3:
            st.markdown("##### 만족도")

            st.metric("Score", f"{s_score}점")

    # ======================================
    # 🟣 RIGHT
    # ======================================
    with right_col:

        st.markdown("#### 베스트 꿀팁 💡")

        for t in x_ai["tips"]:
            st.markdown(f"""
            <div style='background:#1a1b26;padding:10px;border-radius:10px;margin-bottom:10px'>
                <b>{t['highlight']}</b><br>
                <span style='font-size:12px;color:#888'>{t['desc']}</span>
            </div>
            """, unsafe_allow_html=True)