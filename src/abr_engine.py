class ABREngine:
    def __init__(self):
        # 지원하는 화질 옵션 목록 및 초기 화질 설정
        self.bitrate_options = [360, 480, 720, 1080]
        self.current_bitrate = 720
        self.state = "PLAYING"  # 7주차: 스트리밍 상태 추적 (PLAYING, REBUFFERING 등)

    def decide_bitrate(self, throughput, buffer_level):
        """
        [7주차 상태 머신 및 Rule-based ABR 알고리즘 구현]
        - throughput: 네트워크 대역폭 (Mbps)
        - buffer_level: 비디오 잔여 버퍼 시간 (초)
        """
        # 1. 버퍼 고갈(0초) 또는 위험 수준 예외 처리 (REBUFFERING 상태 전환)
        if buffer_level <= 0.0:
            self.state = "REBUFFERING"
            self.current_bitrate = 360
            return self.current_bitrate

        # 버퍼가 회복되면 다시 PLAYING 상태로 복귀
        if self.state == "REBUFFERING" and buffer_level >= 3.0:
            self.state = "PLAYING"

        # 2. 기본 Rule-based 화질 결정 로직
        if buffer_level < 5.0:
            target_bitrate = 360
        elif buffer_level >= 10.0 and throughput > 10.0:
            target_bitrate = 1080
        elif buffer_level >= 7.0 and throughput > 5.0:
            target_bitrate = 720
        else:
            target_bitrate = 480

        # 3. 7주차: 급격한 화질 변동을 방지하기 위한 안정성(Smoothing) 로직 적용
        # (화질이 한 번에 너무 크게 튀지 않도록 인접 단계로 제한)
        current_index = self.bitrate_options.index(self.current_bitrate)
        target_index = self.bitrate_options.index(target_bitrate)

        if target_index > current_index + 1:
            # 화질을 한 단계씩만 안전하게 상향
            self.current_bitrate = self.bitrate_options[current_index + 1]
        elif target_index < current_index - 1:
            # 버퍼가 급감할 때는 빠르게 낮춤 (리버퍼링 방지)
            self.current_bitrate = target_bitrate
        else:
            self.current_bitrate = target_bitrate

        return self.current_bitrate
