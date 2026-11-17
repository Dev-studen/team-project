import streamlit as st
import pandas as pd
import numpy as np
import time


# 1. 페이지 기본 설정
st.set_page_config(page_title="ABR 시뮬레이터 (7주차)", layout="wide")


# [초기화] 실시간 그래프 렌더링을 위한 세션 상태(Session State) 설정
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame({
        "Tick": list(range(1, 21)),
        " 선택 비트레이트 (Mbps)": [5.0] * 20,
        "유효 처리량 (Mbps)": [9.0] * 20,
        "버퍼 잔여량 (sec)": [15.0] * 20
    })
    
if "current_buffer" not in st.session_state:
    st.session_state.current_buffer = 15.0
if "tick_count" not in st.session_state:
    st.session_state.tick_count = 20
if "prev_quality" not in st.session_state:
    st.session_state.prev_quality = "1080p"





# [연동 인터페이스 함수] (8주차 병합 시 백엔드 모듈과 연결할 부분)

def simulate_step(bandwidth, packet_loss, rtt_delay, current_buffer):
    """
    네트워크 환경 입력값을 바탕으로 유효 처리량, 화질(Bitrate), 버퍼 증감을 계산합니다.
    (향후 network_channel.py 및 abr_engine.py 함수 호출로 대체 가능)
    """
    # 1) 유효 처리량(Throughput) 계산 (손실률 및 RTT 지연 패널티 반영)
    loss_factor = max(0.0, 1.0 - (packet_loss / 100.0) * 2.5)
    rtt_factor = max(0.2, 1.0 - ((rtt_delay - 20) / 600.0))
    effective_tp = round(max(0.1, bandwidth * loss_factor * rtt_factor), 2)



    # 2) 유효 처리량 및 현재 버퍼 기반 4단계 화질 동적 결정 (240p ~ 1080p)
    if effective_tp >= 6.0 and current_buffer >= 10.0:
        quality, bitrate_mbps = "1080p", 5.0
    elif effective_tp >= 3.0 and current_buffer >= 6.0:
        quality, bitrate_mbps = "720p", 2.5
    elif effective_tp >= 1.2 and current_buffer >= 3.0:
        quality, bitrate_mbps = "480p", 1.0
    else:
        quality, bitrate_mbps = "240p", 0.4



    # 3) 실시간 버퍼 잔여량 증감 계산 (최대 30초, 최소 0초 가드)
    # 1초 동안 다운로드된 영상 길이 - 1초 재생 소모량
    buffer_delta = round((effective_tp / max(0.4, bitrate_mbps)) - 1.0, 2)
    buffer_delta = max(-2.5, min(2.0, buffer_delta))  # 급격한 변동 완화
    new_buffer = round(max(0.0, min(30.0, current_buffer + buffer_delta)), 1)


    # 4) 재생 상태 머신 결정 (PLAYING vs REBUFFERING)
    if new_buffer <= 0.5 or (effective_tp < 0.4 and packet_loss >= 15):
        state = "REBUFFERING"
    else:
        state = "PLAYING"

    return effective_tp, quality, bitrate_mbps, new_buffer, buffer_delta, state





# 2. 좌측 사이드바: 네트워크 환경 제어 슬라이더
with st.sidebar:
    st.header("네트워크 환경 제어")
    st.markdown("---")

    # 실시간 자동 시뮬레이션 토글 (1초 주기 동적 렌더링 제어)
    auto_play = st.checkbox("실시간 동적 렌더링 자동 재생 (1초 주기)", value=True)


    st.markdown("### 채널 파라미터 조절")
    bandwidth = st.slider("대역폭 (Mbps)", min_value=0.5, max_value=20.0, value=10.0, step=0.5)
    packet_loss = st.slider("패킷 손실률 (%)", min_value=0, max_value=20, value=0, step=1)
    rtt_delay = st.number_input("RTT 지연 (ms)", min_value=20, max_value=500, value=50, step=10)


    if st.button("그래프 및 버퍼 초기화"):
        st.session_state.current_buffer = 15.0
        st.session_state.tick_count = 20
        st.session_state.history = pd.DataFrame({
            "Tick": list(range(1, 21)),
            " 선택 비트레이트 (Mbps)": [5.0] * 20,
            "유효 처리량 (Mbps)": [9.0] * 20,
            "버퍼 잔여량 (sec)": [15.0] * 20
        })



    st.markdown("---")
    # 극한값 예외 처리 가드 알림
    if bandwidth <= 1.5 or packet_loss >= 15 or rtt_delay >= 350:
        st.error("경고: 네트워크 혼잡! 화질을 낮추어 버퍼링을 방어합니다.")

    elif bandwidth <= 4.0 or packet_loss >= 8:
        st.warning("주의: 대역폭 감소 감지. 적응형 화질 제어가 작동 중입니다.")
    else:
        st.success("네트워크 상태가 안정적입니다.")





# ==========================================

# [실시간 스텝 연산 및 시계열 데이터 업데이트]

# ==========================================

effective_tp, current_quality, bitrate_mbps, new_buffer, buffer_delta, play_state = simulate_step(
    bandwidth, packet_loss, rtt_delay, st.session_state.current_buffer
)


# 세션 상태 업데이트 (최근 20개 스텝 유지하며 그래프가 흐르도록 처리)
st.session_state.current_buffer = new_buffer
st.session_state.tick_count += 1



new_row = pd.DataFrame({
    "Tick": [st.session_state.tick_count],
    " 선택 비트레이트 (Mbps)": [bitrate_mbps],
    "유효 처리량 (Mbps)": [effective_tp],
    "버퍼 잔여량 (sec)": [new_buffer]

})
st.session_state.history = pd.concat([st.session_state.history.iloc[1:], new_row], ignore_index=True)



# 화질 변화 텍스트 계산
quality_status = "유지 중"
if current_quality != st.session_state.prev_quality:
    quality_status = f"전환 ({st.session_state.prev_quality} → {current_quality})"
    st.session_state.prev_quality = current_quality





# ==========================================
# 3. 우측 메인 화면: 플레이어 모사 & 동적 그래프
# ==========================================
st.title("실시간 적응형 비디오 스트리밍(ABR) 모니터링")



# [상단] 3분할 핵심 메트릭 (슬라이더에 따라 실시간 변화)

m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("현재 스트리밍 화질 (Quality)", f"{current_quality} ({bitrate_mbps} Mbps)", quality_status)
m_col2.metric("유효 처리량 (Throughput)", f"{effective_tp:.1f} Mbps", f"설정 대역폭: {bandwidth} Mbps")
m_col3.metric("현재 버퍼 잔여량 (Buffer Level)", f"{new_buffer:.1f} 초", f"{buffer_delta:+.1f} 초/s")



st.markdown("---")

# [중단] 비디오 스트리밍 재생 모사 화면 & 실시간 버퍼 프로그레스 바

player_col, buffer_col = st.columns([1, 1])


with player_col:
    st.subheader("비디오 스트리밍 재생 모사 화면")
    # 화질 및 재생 상태에 따른 시각적 배지 색상 지정
    color_map = {"1080p": "#1E88E5", "720p": "#43A047", "480p": "#FB8C00", "240p": "#E53935"}
    bg_color = color_map.get(current_quality, "#1E88E5")
    state_icon = "PLAYING (정상 재생 중)" if play_state == "PLAYING" else "⏳ REBUFFERING (버퍼링 발생!)"



    st.markdown(
        f"""
        <div style="background-color:{bg_color}; padding:22px; border-radius:12px; color:white; text-align:center;">

            <h3 style="margin:0; color:white;">{state_icon}</h3>

            <p style="font-size:20px; margin:8px 0 0 0;">현재 출력 해상도: <b>{current_quality}</b> | 요구 비트레이트: <b>{bitrate_mbps} Mbps</b></p>
        </div>
        """,
        unsafe_allow_html=True

    )



with buffer_col:
    st.subheader("실시간 버퍼 상태 (Target: 10~30초)")
    max_buffer = 30.0
    progress_ratio = min(max(new_buffer / max_buffer, 0.0), 1.0)
    buffer_msg = "안정권 (목표 버퍼 유지 중)" if new_buffer >= 10.0 else ("주의 (버퍼 소진 중)" if new_buffer > 0.5 else "위험 (버퍼 고갈 - 재생 멈춤)")
    st.write(f"버퍼 상태: **{buffer_msg}**")
    st.progress(progress_ratio, text=f"잔여 버퍼: {new_buffer:.1f}초 / 최대 {max_buffer:.0f}초")



st.markdown("---")


# [하단] 실시간 동적 그래프 렌더링 (시계열 업데이트)

chart_col1, chart_col2 = st.columns(2)

chart_data = st.session_state.history.set_index("Tick")


with chart_col1:
    st.markdown("*실시간 비트레이트 및 유효 처리량 변동 (Mbps)**")
    st.line_chart(chart_data[[" 선택 비트레이트 (Mbps)", "유효 처리량 (Mbps)"]])



with chart_col2:
    st.markdown("**실시간 버퍼 잔여량 변동 (초)**")
    st.line_chart(chart_data[["버퍼 잔여량 (sec)"]])



# 4. 1초 주기 실시간 동적 리렌더링 루프
if auto_play:
    time.sleep(1.0)
    if hasattr(st, "rerun"):
        st.rerun()

    else:

        st.experimental_rerun()
