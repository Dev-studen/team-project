class ABREngine:
    def __init__(self):
        # 지원하는 화질 옵션 목록 및 초기 화질 설정
        self.bitrate_options = [360, 480, 720, 1080]
        self.current_bitrate = 720

    def decide_bitrate(self, throughput, buffer_level):
        """
        [6주차 Rule-based ABR 알고리즘 구현]
        - throughput: 네트워크 대역폭 (Mbps)
        - buffer_level: 비디오 잔여 버퍼 시간 (초)
        """
        # 1. 버퍼가 5초 미만이면 리버퍼링 방지를 위해 최소 화질로 낮춤
        if buffer_level < 5.0:
            self.current_bitrate = 360
        # 2. 버퍼와 대역폭이 모두 충분하면 최고 화질 선택
        elif buffer_level >= 10.0 and throughput > 10.0:
            self.current_bitrate = 1080
        # 3. 중간 상태 조건별 화질 선택
        elif buffer_level >= 7.0 and throughput > 5.0:
            self.current_bitrate = 720
        else:
            self.current_bitrate = 480

        return self.current_bitrate
