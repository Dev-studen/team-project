import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 및 전체 레이아웃 설정
st.set_page_config(page_title="ABR 시뮬레이터", layout="wide")

# 2. 좌측: 대역폭 조절용 슬라이더 바 구현
with st.sidebar:
    st.header("네트워크 환경 제어")
    st.markdown("---")
    
    # 사용자 조작에 따라 실시간으로 값이 변동되는 슬라이더
    bandwidth = st.slider("대역폭 (Mbps)", min_value=0.5, max_value=20.0, value=10.0, step=0.5)
    packet_loss = st.slider("패킷 손실률 (%)", min_value=0, max_value=20, value=0, step=1)
    rtt_delay = st.number_input("RTT 지연 (ms)", min_value=20, max_value=500, value=50, step=10)
    
    # 예외 처리 가드 (시뮬레이션 안정성 확보)
    if bandwidth <= 1.0 or packet_loss >= 15:
        st.error("경고: 네트워크 상태가 매우 불안정합니다. 버퍼링이 발생할 수 있습니다.")
    else:
        st.success("네트워크 상태가 안정적입니다.")

# 3. 우측 메인: 대시보드 및 버퍼 레이아웃 구현
st.title("실시간 적응형 비디오 스트리밍 모니터링")

# 상단: 3분할 텍스트 메트릭 레이아웃
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("현재 화질 (Target Bitrate)", "1080p", "안정적")
metric_col2.metric("유효 대역폭 (Throughput)", f"{bandwidth * 0.9:.1f} Mbps", "-")
metric_col3.metric("현재 버퍼 용량 (Buffer Level)", "15.0 초", "+0.5 초")

st.markdown("---")

# 중단: 버퍼 상태 시각화 전용 레이아웃
st.subheader("실시간 버퍼 상태")
buffer_level = 15.0  # 향후 백엔드에서 받아올 잔여 버퍼 데이터 (초기값 15초)
max_buffer = 30.0    # 최대 버퍼 용량 (30초)

# 버퍼 용량을 한눈에 파악할 수 있는 시각적 프로그레스 바 레이아웃
progress_ratio = min(buffer_level / max_buffer, 1.0)
st.progress(progress_ratio, text=f"현재 버퍼 잔여량: {buffer_level}초 / 최대 {max_buffer}초 (목표 버퍼 유지 중)")

st.markdown("---")

# 하단: 2분할 동적 그래프 레이아웃
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**실시간 비트레이트 변동 내역**")
    # 대역폭 슬라이더 값에 연동되어 변화하는 더미 데이터
    dummy_bitrate = pd.DataFrame(np.random.randn(15, 1) * 2 + bandwidth, columns=['Bitrate (Mbps)'])
    st.line_chart(dummy_bitrate)

with chart_col2:
    st.markdown("**실시간 버퍼 용량 증감 내역**")
    dummy_buffer = pd.DataFrame(np.random.randn(15, 1) + 15, columns=['Buffer (sec)'])
    st.line_chart(dummy_buffer)