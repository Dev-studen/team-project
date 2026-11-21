import time
from datetime import datetime
import pandas as pd
import streamlit as st

# 백엔드 모듈 임포트 (실행 경로에 관계없이 안전하게 로드)
try:
    from abr_engine import ABREngine
    from network_channel import VirtualNetworkChannel
    from logger import SystemLogger
except ImportError:
    from src.abr_engine import ABREngine
    from src.network_channel import VirtualNetworkChannel
    from src.logger import SystemLogger


# 1. 페이지 기본 설정
st.set_page_config(page_title="ABR 시뮬레이터 (12주차 통합 알파버전)", layout="wide")


# 해상도(int) <-> UI 표기 및 비트레이트(Mbps) 매핑
QUALITY_MAP = {
    1080: ("1080p", 5.0),
    720: ("720p", 2.5),
    480: ("480p", 1.0),
    360: ("360p", 0.5),
}

# 11주차 대표 네트워크 시나리오 (대역폭 Mbps, 패킷 손실률 %, RTT ms)
SCENARIO_PRESETS = {
    "수동 제어 (사이드바 슬라이더)": None,
    "시나리오 1: 대역폭 급락 (10.0 → 0.6 Mbps)": [
        (10.0, 0, 50),
        (8.0, 1, 60),
        (3.0, 5, 90),
        (1.2, 10, 140),
        (0.6, 15, 220),
    ],
    "시나리오 2: 대역폭 급상승 (0.8 → 12.0 Mbps)": [
        (0.8, 10, 150),
        (2.5, 5, 100),
        (5.5, 2, 70),
        (9.5, 0, 50),
        (12.0, 0, 40),
    ],
    "시나리오 3: 패킷 손실률 증가 (1% → 45%)": [
        (8.0, 1, 50),
        (7.5, 5, 70),
        (7.0, 15, 110),
        (6.5, 30, 180),
        (6.0, 45, 260),
    ],
    "시나리오 4: 버퍼 고갈 위기 방어": [
        (4.0, 5, 80),
        (1.0, 15, 180),
        (0.8, 20, 220),
        (2.5, 5, 90),
    ],
    "시나리오 5: 네트워크 급격 요동": [
        (9.0, 1, 50),
        (1.5, 12, 160),
        (8.5, 2, 60),
        (1.0, 18, 200),
    ],
    "시나리오 6: 지연 시간(RTT) 증가": [
        (6.0, 2, 60),
        (3.5, 8, 220),
        (2.0, 12, 420),
    ],
    "시나리오 7: 네트워크 완전 단절 예외 방어": [
        (5.0, 0, 50),
        (0.0, 100, 500),
        (0.0, 100, 500),
        (4.0, 2, 70),
    ],
}


# 2. 세션 상태(Session State) 초기화
def init_session_state():
    if "abr_engine" not in st.session_state:
        st.session_state.abr_engine = ABREngine()
    if "network_channel" not in st.session_state:
        st.session_state.network_channel = VirtualNetworkChannel(10.0, 0.0, 50.0)
    if "logger" not in st.session_state:
        st.session_state.logger = SystemLogger()
        st.session_state.logger.log_event("TEST_START", 10.0, "720p", 15.0, 0.0)
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame({
            "Tick": list(range(1, 21)),
            "선택 비트레이트 (Mbps)": [2.5] * 20,
            "유효 처리량 (Mbps)": [10.0] * 20,
            "버퍼 잔여량 (sec)": [15.0] * 20,
        })
    if "current_buffer" not in st.session_state:
        st.session_state.current_buffer = 15.0
    if "tick_count" not in st.session_state:
        st.session_state.tick_count = 20
    if "prev_quality" not in st.session_state:
        st.session_state.prev_quality = "720p"
    if "event_logs" not in st.session_state:
        st.session_state.event_logs = []
    if "scenario_step_idx" not in st.session_state:
        st.session_state.scenario_step_idx = 0
    if "last_scenario" not in st.session_state:
        st.session_state.last_scenario = "수동 제어 (사이드바 슬라이더)"


init_session_state()


# 3. 백엔드 통합 연산 함수 (VirtualNetworkChannel + ABREngine + SystemLogger 연동)
def run_integrated_step(bandwidth, packet_loss, rtt_delay, use_fluctuation=False):
    channel: VirtualNetworkChannel = st.session_state.network_channel
    engine: ABREngine = st.session_state.abr_engine
    logger: SystemLogger = st.session_state.logger
    current_buffer: float = st.session_state.current_buffer

    # 1) 네트워크 채널 파라미터 업데이트 및 유효 처리량(Mathis 방정식) 계산
    channel.update_network_conditions(bandwidth, packet_loss, rtt_delay)
    if use_fluctuation and bandwidth > 0.0:
        channel.apply_random_fluctuation(volatility=0.08)

    effective_tp = round(channel.calculate_throughput(), 2)

    # 2) ABR 엔진으로 목표 화질 및 재생 상태 결정
    selected_res = engine.decide_bitrate(effective_tp, current_buffer)
    quality_label, bitrate_mbps = QUALITY_MAP.get(selected_res, ("360p", 0.5))

    # 3) 세그먼트(1초 분량) 다운로드 시간 기반 버퍼 증감 계산
    if effective_tp <= 0.0:
        buffer_delta = -1.5
    else:
        download_time = channel.get_segment_download_time(segment_size=bitrate_mbps)
        downloaded_video_sec = 1.0 / max(0.2, download_time)
        buffer_delta = round(max(-2.5, min(2.0, downloaded_video_sec - 1.0)), 2)

    new_buffer = round(max(0.0, min(30.0, current_buffer + buffer_delta)), 1)

    # 4) 재생 상태 보정 (완전 단절 시 DROP, 버퍼 고갈 시 REBUFFERING)
    if bandwidth <= 0.0 or packet_loss >= 100:
        play_state = "DROP"
    elif new_buffer <= 0.5:
        play_state = "REBUFFERING"
    else:
        play_state = engine.state

    # 5) 이벤트 감지 및 SystemLogger / 화면 로그 기록
    event_type = "NORMAL_STREAMING"
    if play_state == "DROP":
        event_type = "NETWORK_DROP"
    elif play_state == "REBUFFERING" or new_buffer < 5.0:
        event_type = "BUFFER_WARNING"
    elif packet_loss >= 15:
        event_type = "LOSS_INCREASE"
    elif bandwidth <= 1.5:
        event_type = "BW_DROP"
    elif quality_label != st.session_state.prev_quality:
        event_type = "BITRATE_ADJUSTED"

    # 주요 이벤트이거나 매 3틱마다 로그 기록
    if event_type != "NORMAL_STREAMING" or st.session_state.tick_count % 3 == 0:
        logger.log_event(event_type, round(channel.bandwidth, 1), quality_label, new_buffer, round(packet_loss, 1))
        st.session_state.event_logs.insert(0, {
            "시간": datetime.now().strftime("%H:%M:%S"),
            "이벤트": event_type,
            "설정 대역폭": f"{channel.bandwidth:.1f} Mbps",
            "유효 처리량": f"{effective_tp:.2f} Mbps",
            "손실률": f"{packet_loss}%",
            "결정 화질": quality_label,
            "버퍼 잔여량": f"{new_buffer:.1f} 초",
            "상태": play_state,
        })
        st.session_state.event_logs = st.session_state.event_logs[:30]

    return effective_tp, quality_label, bitrate_mbps, new_buffer, buffer_delta, play_state


# 4. 좌측 사이드바: 시나리오 선택 및 네트워크 환경 제어
with st.sidebar:
    st.header("네트워크 환경 제어")
    st.markdown("---")

    auto_play = st.checkbox("실시간 동적 렌더링 자동 재생 (1초 주기)", value=True)

    st.markdown("### 11주차 시나리오 자동 시연")
    selected_scenario = st.selectbox(
        "시연 시나리오 선택",
        options=list(SCENARIO_PRESETS.keys()),
        index=0,
    )

    # 시나리오 변경 시 버퍼 및 엔진 상태를 시연에 알맞게 자동 리셋
    if selected_scenario != st.session_state.last_scenario:
        st.session_state.scenario_step_idx = 0
        st.session_state.last_scenario = selected_scenario
        st.session_state.abr_engine = ABREngine()
        st.session_state.prev_quality = "720p"
        st.session_state.current_buffer = 8.0 if SCENARIO_PRESETS[selected_scenario] is not None else 15.0

    st.markdown("### 채널 파라미터 조절")
    if SCENARIO_PRESETS[selected_scenario] is None:
        bandwidth = st.slider("대역폭 (Mbps)", min_value=0.0, max_value=20.0, value=10.0, step=0.5)
        packet_loss = st.slider("패킷 손실률 (%)", min_value=0, max_value=50, value=0, step=1)
        rtt_delay = st.number_input("RTT 지연 (ms)", min_value=20, max_value=500, value=50, step=10)
        use_fluctuation = st.checkbox("실제 채널 미세 요동 반영", value=False)
    else:
        steps = SCENARIO_PRESETS[selected_scenario]
        cur_idx = st.session_state.scenario_step_idx % len(steps)
        bandwidth, packet_loss, rtt_delay = steps[cur_idx]
        use_fluctuation = False
        st.info(
            f"**자동 시연 진행 중 ({cur_idx + 1}/{len(steps)} 단계)**\n\n"
            f"- 대역폭: `{bandwidth} Mbps`\n"
            f"- 패킷 손실률: `{packet_loss}%`\n"
            f"- RTT 지연: `{rtt_delay} ms`"
        )
        st.session_state.scenario_step_idx += 1

    if st.button("시뮬레이터 상태 초기화"):
        st.session_state.abr_engine = ABREngine()
        st.session_state.current_buffer = 15.0
        st.session_state.tick_count = 20
        st.session_state.prev_quality = "720p"
        st.session_state.scenario_step_idx = 0
        st.session_state.event_logs = []
        st.session_state.history = pd.DataFrame({
            "Tick": list(range(1, 21)),
            "선택 비트레이트 (Mbps)": [2.5] * 20,
            "유효 처리량 (Mbps)": [10.0] * 20,
            "버퍼 잔여량 (sec)": [15.0] * 20,
        })
        st.rerun()

    st.markdown("---")
    if bandwidth <= 1.5 or packet_loss >= 15 or rtt_delay >= 350:
        st.error("경고: 네트워크 혼잡! ABR 엔진이 화질을 하향 조정하여 버퍼링을 방어합니다.")
    elif bandwidth <= 4.0 or packet_loss >= 8:
        st.warning("주의: 대역폭 감소 감지. 적응형 화질 제어가 작동 중입니다.")
    else:
        st.success("네트워크 상태가 안정적입니다.")


# 5. 실시간 스텝 연산 및 시계열 데이터 업데이트
effective_tp, current_quality, bitrate_mbps, new_buffer, buffer_delta, play_state = run_integrated_step(
    bandwidth, packet_loss, rtt_delay, use_fluctuation
)

st.session_state.current_buffer = new_buffer
st.session_state.tick_count += 1

new_row = pd.DataFrame({
    "Tick": [st.session_state.tick_count],
    "선택 비트레이트 (Mbps)": [bitrate_mbps],
    "유효 처리량 (Mbps)": [effective_tp],
    "버퍼 잔여량 (sec)": [new_buffer],
})
st.session_state.history = pd.concat([st.session_state.history.iloc[1:], new_row], ignore_index=True)

quality_status = "유지 중"
if current_quality != st.session_state.prev_quality:
    quality_status = f"전환 ({st.session_state.prev_quality} → {current_quality})"
    st.session_state.prev_quality = current_quality


# 6. 우측 메인 대시보드 출력
st.title("실시간 적응형 비디오 스트리밍(ABR) 통합 모니터링")
st.caption(f"연동 모듈: ABREngine · VirtualNetworkChannel (Mathis) · SystemLogger ({st.session_state.logger.log_file})")

m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("현재 스트리밍 화질 (Quality)", f"{current_quality} ({bitrate_mbps} Mbps)", quality_status)
m_col2.metric("유효 처리량 (Throughput)", f"{effective_tp:.2f} Mbps", f"설정 대역폭: {bandwidth:.1f} Mbps")
m_col3.metric("현재 버퍼 잔여량 (Buffer Level)", f"{new_buffer:.1f} 초", f"{buffer_delta:+.2f} 초/s")

st.markdown("---")

# 중단: 플레이어 상태 배지 & 버퍼 게이지
player_col, buffer_col = st.columns([1, 1])

with player_col:
    st.subheader("비디오 스트리밍 재생 모사 화면")
    color_map = {"1080p": "#1E88E5", "720p": "#43A047", "480p": "#FB8C00", "360p": "#E53935"}
    bg_color = "#424242" if play_state == "DROP" else color_map.get(current_quality, "#1E88E5")

    if play_state == "DROP":
        state_icon = "⛔ DROP (네트워크 단절 - 수신 중단)"
    elif play_state == "REBUFFERING":
        state_icon = "⏳ REBUFFERING (버퍼 고갈 - 재버퍼링 중)"
    else:
        state_icon = "▶ PLAYING (정상 재생 중)"

    st.markdown(
        f"""
        <div style="background-color:{bg_color}; padding:22px; border-radius:12px; color:white; text-align:center;">
            <h3 style="margin:0; color:white;">{state_icon}</h3>
            <p style="font-size:20px; margin:8px 0 0 0;">현재 출력 해상도: <b>{current_quality}</b> | 요구 비트레이트: <b>{bitrate_mbps} Mbps</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with buffer_col:
    st.subheader("실시간 버퍼 상태 (Target: 10~30초)")
    max_buffer = 30.0
    progress_ratio = min(max(new_buffer / max_buffer, 0.0), 1.0)
    buffer_msg = (
        "안정권 (목표 버퍼 유지 중)"
        if new_buffer >= 10.0
        else ("주의 (버퍼 소진 중)" if new_buffer > 0.5 else "위험 (버퍼 고갈 - 재생 멈춤)")
    )
    st.write(f"버퍼 상태: **{buffer_msg}**")
    st.progress(progress_ratio, text=f"잔여 버퍼: {new_buffer:.1f}초 / 최대 {max_buffer:.0f}초")

st.markdown("---")

# 하단 1: 실시간 동적 그래프
chart_col1, chart_col2 = st.columns(2)
chart_data = st.session_state.history.set_index("Tick")

with chart_col1:
    st.markdown("**실시간 비트레이트 및 유효 처리량 변동 (Mbps)**")
    st.line_chart(chart_data[["선택 비트레이트 (Mbps)", "유효 처리량 (Mbps)"]])

with chart_col2:
    st.markdown("**실시간 버퍼 잔여량 변동 (초)**")
    st.line_chart(chart_data[["버퍼 잔여량 (sec)"]])

st.markdown("---")

# 하단 2: 실시간 이벤트 로그 출력 (SystemLogger 연동)
st.subheader("실시간 시스템 이벤트 로그")
if st.session_state.event_logs:
    log_df = pd.DataFrame(st.session_state.event_logs)
    st.dataframe(log_df, use_container_width=True, hide_index=True)
else:
    st.info("시뮬레이션이 진행되면서 화질 전환 및 버퍼 경고 로그가 여기에 실시간으로 기록됩니다.")


# 7. 1초 주기 실시간 동적 리렌더링 루프
if auto_play:
    time.sleep(1.0)
    st.rerun()