class ABREngine:
    def __init__(self):
        # 초기 비트레이트 설정 예시 (1080p, 720p, 480p, 360p 등)
        self.current_bitrate = 1080

    def decide_bitrate(self, throughput, buffer_level):
        """
        네트워크 대역폭(Throughput) 및 버퍼 상태(Buffer Level)에 따라
        비디오 화질을 동적으로 결정하는 ABR 알고리즘 뼈대
        """
        # TODO: 6주차에 Rule-based 제어 로직 구현 예정
        return self.current_bitrate
