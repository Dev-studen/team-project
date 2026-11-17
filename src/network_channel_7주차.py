import random
import math

class VirtualNetworkChannel:
    def __init__(self, bandwidth: float, packet_loss_percent: float, rtt: float):
        self.bandwidth = max(0.1, bandwidth) 
        # UI에서 퍼센트(%)로 들어오는 값을 0.0~1.0 비율로 변환하여 저장
        self.packet_loss = max(0.0, min(1.0, packet_loss_percent / 100.0))
        self.rtt = max(1.0, rtt)

    def update_network_conditions(self, new_bandwidth: float, new_packet_loss_percent: float, new_rtt: float):
        self.bandwidth = max(0.1, new_bandwidth) 
        # UI 슬라이더 값(%)을 소수점 비율로 자동 변환 연동
        self.packet_loss = max(0.0, min(1.0, new_packet_loss_percent / 100.0))
        self.rtt = max(1.0, new_rtt)

    def apply_random_fluctuation(self, volatility: float = 0.1):
        bw_change_ratio = random.uniform(-volatility, volatility)
        rtt_change_ratio = random.uniform(-volatility, volatility)
        
        new_bw = self.bandwidth * (1 + bw_change_ratio)
        new_rtt = self.rtt * (1 + rtt_change_ratio)
        
        new_loss = self.packet_loss
        if random.random() < 0.05:
            new_loss += random.uniform(0.01, 0.05)
            
        # 변동된 상태 업데이트
        self.bandwidth = max(0.1, new_bw)
        self.packet_loss = max(0.0, min(1.0, new_loss))
        self.rtt = max(1.0, new_rtt)

    def calculate_throughput(self) -> float:
        """
        Mathis 방정식을 이용한 실시간 유효 처리량 연산 (UI 연동용)
        """
        safe_rtt = max(1.0, self.rtt)
        
        if self.packet_loss <= 0.0:
            return self.bandwidth
        
        # Mathis 방정식 적용 (시뮬레이터 UI 수치 스케일에 맞춘 상수 100.0 적용)
        mathis_throughput = 100.0 / (safe_rtt * math.sqrt(self.packet_loss))
        
        return min(self.bandwidth, mathis_throughput)

    def get_segment_download_time(self, segment_size: float) -> float:
        throughput = self.calculate_throughput()
        safe_throughput = max(0.01, throughput)
        return (segment_size / safe_throughput) + (self.rtt / 1000.0)
