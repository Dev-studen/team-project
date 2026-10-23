import streamlit as st
import pandas as pd
import numpy as np
import time

# 1. 페이지 기본 설정 (가장 넓은 화면 사용)
st.set_page_config(page_title="ABR 시뮬레이터", layout="wide")

# 2. 좌측 사이드바 (네트워크 환경 제어)
st.sidebar.header("네트워크 환경 제어 ")
st.sidebar.markdown("발표 시연 시 아래 슬라이더를 조작하세요.")

# 계획서 요구사항에 맞춘 파라미터 극한값 가드 반영
bandwidth = st.sidebar.slider("대역폭 (Mbps)", min_value=0.5, max_value=20.0, value=10.0, step=0.5)
packet_loss = st.sidebar.slider("패킷 손실률 (%)", min_value=0, max_value=20, value=0, step=1)
rtt_delay = st.sidebar.number_input("RTT 지연 (ms)", min_value=20, max_value=500, value=50, step=10)

# 예외 처리 가드 (시연 중 프로그램 다운 방지용 경고)
if bandwidth <= 1.0 or packet_loss >= 15:
    st.sidebar.warning("!! 네트워크 상태 불량: 버퍼링이 발생할 수 있습니다 !!")

# 3. 우측 메인 화면 (출력 및 시각화)
st.title("적응형 비디오 스트리밍(ABR) 시뮬레이터 ")

# 핵심 지표 표시 (더미 텍스트 적용)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="현재 스트리밍 화질", value="1080p", delta="Stable")
with col2:
    st.metric(label="현재 버퍼 용량", value="15.0 초", delta="-0.5 초")
with col3:
    st.metric(label="유효 처리량 (Throughput)", value=f"{bandwidth * 0.9:.1f} Mbps")

st.divider()

# 4. 실시간 시각화 렌더링 그래프 (더미 데이터 적용)
st.subheader(" 실시간 네트워크 및 스트리밍 상태 모니터링")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write(" 실시간 비트레이트 변동")
    # 향후 팀원 2의 데이터를 받을 빈 차트 틀 (현재는 임의의 난수로 형태만 표시)
    dummy_bitrate_data = pd.DataFrame(np.random.randn(20, 1) * 2 + bandwidth, columns=['Bitrate (Mbps)'])
    st.line_chart(dummy_bitrate_data)

with chart_col2:
    st.write(" 실시간 버퍼 용량 변동")
    # 향후 10초~30초 사이의 버퍼량을 띄워줄 틀
    dummy_buffer_data = pd.DataFrame(np.random.randn(20, 1) + 15, columns=['Buffer (sec)'])
    st.line_chart(dummy_buffer_data)

st.caption("※ 현재 화면은 5주 차 UI 뼈대 코드이며, 차트 데이터는 더미(가짜) 값입니다.")

