# 적응형 비디오 스트리밍(ABR) 시뮬레이터 (데이터 통신 12팀)

실시간 네트워크 대역폭 변동, 패킷 손실률, RTT 지연 환경에서 비디오 화질(Bitrate)과 버퍼 상태를 동적으로 제어하는 Python 기반 적응형 비디오 스트리밍(Adaptive Bitrate Streaming, ABR) 시뮬레이터입니다.

## 1. 주요 기능
- **가상 네트워크 채널 모사 (`src/network_channel.py`)**: 대역폭(0.5 ~ 20.0 Mbps), 패킷 손실률(0 ~ 20%), RTT 지연(20 ~ 500 ms)을 반영해 실시간 유효 처리량(Throughput)을 연산합니다.
- **ABR 제어 엔진 (`src/abr_engine.py`)**: 유효 처리량과 잔여 버퍼 레벨(Target Buffer: 10 ~ 30초)을 기반으로 4단계 화질(240p / 480p / 720p / 1080p)을 자동 전환하고, 재생 상태 머신(`PLAYING`, `REBUFFERING`, `DROP`)을 제어합니다.
- **실시간 시각화 대시보드 (`src/app_ui_week7.py`)**: Streamlit 기반으로 네트워크 조건 조절 슬라이더, 실시간 버퍼 잔여량 표시, 1초 주기 비트레이트 및 버퍼 변동 동적 그래프를 렌더링합니다.
- **이벤트 로깅 (`src/logger.py`)**: 세그먼트 요청/응답 시각 및 화질 전환 이벤트를 실시간으로 기록합니다.

## 2. 프로젝트 폴더 구조
```text
team-project/
├── ai/                  # AI 활용 기록 및 참고 자료
├── data/                # 시뮬레이션 입력 및 테스트 데이터
├── docs/                # 수행계획서, 중간/최종 보고서 등 문서
├── results/             # 실행 로그(CSV) 및 성능 분석 결과
├── src/
│   ├── abr_engine.py        # ABR 제어 알고리즘 및 버퍼 상태 머신
│   ├── app_ui_week7.py      # Streamlit 대시보드 UI
│   ├── logger.py            # 이벤트 로깅 모듈
│   └── network_channel.py   # 가상 네트워크 채널 및 수식 연산 모듈
├── main.py              # 로컬 시연 모드(--mode demo) 실행 진입점
├── requirements.txt     # 필수 Python 라이브러리 목록
└── README.md            # 실행 매뉴얼
```

## 3. 개발 및 실행 환경
- **Python**: 3.11 권장
- **주요 라이브러리**: `streamlit`, `pandas`, `numpy` (상세 목록은 `requirements.txt` 참조)

## 4. 설치 방법
1. 저장소를 클론(복제)하고 프로젝트 폴더로 이동합니다.
```bash
git clone [https://github.com/Dev-studen/team-project.git](https://github.com/Dev-studen/team-project.git)
cd team-project
```

2. (권장) Python 가상환경을 생성하고 활성화합니다.
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

3. 필수 패키지를 일괄 설치합니다.
```bash
pip install -r requirements.txt
```

## 5. 실행 방법
### 방법 A: 로컬 시연 모드 실행 (발표 및 라이브 데모용)
외부 네트워크 의존성 없이 로컬 환경에서 시연 파이프라인을 실행합니다.
```bash
python main.py --mode demo
```

### 방법 B: Streamlit 대시보드 단독 실행
```bash
streamlit run src/app_ui_week7.py
```
실행 후 웹 브라우저에서 `http://localhost:8501`에 접속해 좌측 사이드바 슬라이더로 대역폭·패킷 손실률·RTT를 조절하며 화질 및 버퍼 변동을 확인할 수 있습니다.

## 6. 팀원 및 역할 분담 (데이터통신 12팀)
| 역할 | 이름 | 담당 업무 |
| :--- | :--- | :--- |
| 팀장 (백엔드) | 나승주 | ABR 제어 엔진, 버퍼 상태 머신, GitHub 관리 및 시연 CLI 구축 |
| 팀원 (통신/보고서) | 허재민 | 가상 네트워크 채널 수식 연산, 예외 처리 가드, 최종 보고서 작성 |
| 팀원 (UI/매뉴얼) | 신승준 | Streamlit 대시보드 UI, 실시간 동적 그래프, `README.md` 및 `requirements.txt` 작성 |
| 팀원 (테스터/시연) | 정희영 | 이벤트 로깅 모듈, 통합 테스트, 시연 시나리오 및 OBS 백업 영상 제작 |
