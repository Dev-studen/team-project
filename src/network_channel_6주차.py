import random

class VirtualNetworkChannel:
    """
    네트워크 대역폭 변동, 패킷 손실, RTT 지연 등을 모사하는 가상 채널 클래스입니다.
    """
    
    def __init__(self, bandwidth: float, packet_loss: float, rtt: float):
        # 통신 값들이 물리적으로 불가능한 수치(예: 음수)가 되지 않도록 방어 로직 적용
        self.bandwidth = max(0.1, bandwidth) 
        self.packet_loss = max(0.0, min(1.0, packet_loss)) # 0.0(0%) ~ 1.0(100%) 사이 유지
        self.rtt = max(1.0, rtt)

    def update_network_conditions(self, new_bandwidth: float, new_packet_loss: float, new_rtt: float):
        """
        [6주차 개발 1] 외부(UI 슬라이더 등)에서 명시적으로 네트워크 상태를 변경할 때 사용합니다.
        극단적인 값이 들어와도 프로그램이 다운되지 않도록 값을 필터링합니다.
        """
        self.bandwidth = max(0.1, new_bandwidth) 
        self.packet_loss = max(0.0, min(1.0, new_packet_loss))
        self.rtt = max(1.0, new_rtt)
        
        # 값이 변경되었음을 시스템(터미널)에 알림
        print(f"[상태 변경] 대역폭: {self.bandwidth:.2f}Mbps, 손실률: {self.packet_loss*100:.1f}%, RTT: {self.rtt:.1f}ms")

    def apply_random_fluctuation(self, volatility: float = 0.1):
        """
        [6주차 개발 2] 실제 무선 통신 환경의 불안정성(Jitter/Fluctuation)을 모사합니다.
        :param volatility: 변동폭 (기본값 0.1은 현재 값의 ±10% 내외로 흔들림을 의미)
        """
        # 1. 대역폭과 RTT에 미세한 무작위 변동폭 적용 (-10% ~ +10%)
        bw_change_ratio = random.uniform(-volatility, volatility)
        rtt_change_ratio = random.uniform(-volatility, volatility)
        
        new_bw = self.bandwidth * (1 + bw_change_ratio)
        new_rtt = self.rtt * (1 + rtt_change_ratio)
        
        # 2. 패킷 손실률 모사: 평소에는 유지되다가 간헐적으로 네트워크 혼잡(Spike)이 발생하는 상황
        new_loss = self.packet_loss
        if random.random() < 0.05:  # 5% 확률로 돌발적인 손실률 증가 발생
            new_loss += random.uniform(0.01, 0.05) # 1~5% 포인트 추가 손실
            print("[네트워크 경고] 돌발적인 패킷 손실이 발생했습니다!")
            
        # 계산된 새로운 값들을 안전하게 업데이트 함수로 넘김
        self.update_network_conditions(new_bw, new_loss, new_rtt)

    def calculate_throughput(self) -> float:
        pass  # 7주차: 수식 연산 (Mathis 방정식 등) 구현 예정

    def get_segment_download_time(self, segment_size: float) -> float:
        pass  # 7주차: 세그먼트 다운로드 시간 연산 구현 예정


# --- 로컬 테스트용 코드 (직접 실행해보기 위함) ---
if __name__ == "__main__":
    print("--- 6주차 가상 네트워크 채널 모사 테스트 ---")
    # 초기 환경: 10Mbps 속도, 패킷 손실 0%, RTT 50ms
    channel = VirtualNetworkChannel(bandwidth=10.0, packet_loss=0.0, rtt=50.0)
    
    print("\n[시간 흐름에 따른 자연스러운 대역폭 변동 모사]")
    for i in range(5):
        print(f"[{i+1}초 후]", end=" ")
        channel.apply_random_fluctuation(volatility=0.2) # 20% 변동폭 적용
