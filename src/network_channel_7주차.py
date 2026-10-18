import random
import math  # 7주차: 수식 연산(제곱근)을 위해 추가

class VirtualNetworkChannel:
    def __init__(self, bandwidth: float, packet_loss: float, rtt: float):
        self.bandwidth = max(0.1, bandwidth) 
        self.packet_loss = max(0.0, min(1.0, packet_loss))
        self.rtt = max(1.0, rtt)

    def update_network_conditions(self, new_bandwidth: float, new_packet_loss: float, new_rtt: float):
        self.bandwidth = max(0.1, new_bandwidth) 
        self.packet_loss = max(0.0, min(1.0, new_packet_loss))
        self.rtt = max(1.0, new_rtt)

    def apply_random_fluctuation(self, volatility: float = 0.1):
        bw_change_ratio = random.uniform(-volatility, volatility)
        rtt_change_ratio = random.uniform(-volatility, volatility)
        
        new_bw = self.bandwidth * (1 + bw_change_ratio)
        new_rtt = self.rtt * (1 + rtt_change_ratio)
        
        new_loss = self.packet_loss
        if random.random() < 0.05:
            new_loss += random.uniform(0.01, 0.05)
            
        self.update_network_conditions(new_bw, new_loss, new_rtt)

    def calculate_throughput(self) -> float:
        """
        [7주차 구현] Mathis 방정식을 이용한 유효 처리량(Throughput) 연산.
        극한값(예: 패킷 손실 0, RTT 0) 입력 시 프로그램 다운을 방지하는 오류 대응 가이드 적용.
        """
        # RTT가 0이 되어 0으로 나누는 오류(ZeroDivisionError) 방지
        safe_rtt = max(1.0, self.rtt)
        
        # 패킷 손실이 0일 경우 Mathis 방정식 분모가 0이 되므로, 물리적 최대 대역폭을 그대로 반환
        if self.packet_loss <= 0.0:
            return self.bandwidth
        
        # Mathis 방정식: (MSS / (RTT * sqrt(P_loss)))
        # 시뮬레이터 비율을 맞추기 위한 상수값(예: 100.0) 사용
        mathis_throughput = 100.0 / (safe_rtt * math.sqrt(self.packet_loss))
        
        # 계산된 처리량이 물리적 최대 대역폭을 초과할 수 없도록 제한
        return min(self.bandwidth, mathis_throughput)

    def get_segment_download_time(self, segment_size: float) -> float:
        """
        [7주차 구현] 영상 세그먼트 다운로드 소요 시간 산출.
        """
        throughput = self.calculate_throughput()
        
        # 처리량이 완전히 0으로 떨어져 무한루프나 다운이 발생하는 것을 방지
        safe_throughput = max(0.01, throughput)
        
        # 다운로드 시간(초) = (파일 크기 / 속도) + (왕복 지연 시간(초))
        download_time = (segment_size / safe_throughput) + (self.rtt / 1000.0)
        return download_time


# --- 7주차 수식 검증용 테스트 코드 ---
if __name__ == "__main__":
    print("--- 7주차 유효 처리량 연산 및 극한값 예외 처리 테스트 ---")
    channel = VirtualNetworkChannel(bandwidth=10.0, packet_loss=0.01, rtt=50.0)
    
    print(f"[초기 상태] 대역폭: 10Mbps, 손실률: 1%, RTT: 50ms")
    throughput = channel.calculate_throughput()
    print(f"-> 수식 계산된 유효 처리량: {throughput:.2f} Mbps")
    
    seg_size = 5.0 # 5Mb 크기의 영상 조각 요청
    dl_time = channel.get_segment_download_time(seg_size)
    print(f"-> 5Mb 세그먼트 다운로드 예상 시간: {dl_time:.3f} 초\n")
    
    print("[극한값 테스트] 네트워크 혼잡으로 손실률이 20%로 폭증할 때")
    channel.update_network_conditions(10.0, 0.20, 50.0)
    print(f"-> 수식 계산된 유효 처리량 급감: {channel.calculate_throughput():.2f} Mbps")
    print(f"-> 다운로드 예상 시간 지연: {channel.get_segment_download_time(seg_size):.3f} 초")
