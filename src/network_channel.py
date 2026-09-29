class VirtualNetworkChannel:
  
    """
    네트워크 대역폭 변동, 패킷 손실, RTT 지연 등을 모사하는 가상 채널 클래스입니다.
    """
    
    def __init__(self, bandwidth: float, packet_loss: float, rtt: float):
        """
        초기 네트워크 상태를 설정합니다.
        :param bandwidth: 초기 대역폭 (Mbps)
        :param packet_loss: 패킷 손실률 (0.0 ~ 1.0)
        :param rtt: 왕복 지연 시간 (ms)
        """
        self.bandwidth = bandwidth
        self.packet_loss = packet_loss
        self.rtt = rtt

    def update_network_conditions(self, new_bandwidth: float, new_packet_loss: float, new_rtt: float):
        """
        시간 흐름이나 특정 시나리오에 따라 네트워크 상태를 동적으로 변경합니다.
        """
        pass  # 6주차에 세부 로직 구현 예정

    def calculate_throughput(self) -> float:
        """
        현재의 대역폭, 패킷 손실률, RTT를 수학적 모델(예: Mathis equation)에 대입하여 
        유효 처리량(Throughput)을 계산하고 반환합니다.
        """
        pass  # 7주차 수식 연산 고도화 시 구현 예정

    def get_segment_download_time(self, segment_size: float) -> float:
        """
        요청된 비디오 세그먼트 크기와 현재 계산된 Throughput을 바탕으로 
        다운로드에 걸리는 물리적 시간을 산출합니다.
        """
        pass  # 7주차 수식 연산 고도화 시 구현 예정
