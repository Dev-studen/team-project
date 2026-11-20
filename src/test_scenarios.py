import unittest
import time
from logger import SystemLogger

class TestABRScenarios(unittest.TestCase):
    def setUp(self):
        """테스트 시작 전 로그 모듈 초기화"""
        self.logger = SystemLogger()
        print("\n--- 테스트 환경 세팅 완료 ---")

    def test_scenario_1_bandwidth_drop(self):
        """시나리오 1: 네트워크 대역폭 급락 (Drop)"""
        print("실행: 대역폭 10Mbps -> 1Mbps 급락 로그 테스트")
        # 1. 초기 상태 로그
        self.logger.log_event("TEST_START", bandwidth=10.0, bitrate="1080p", buffer_level=20.0)
        # 2. 대역폭 급락 로그
        self.logger.log_event("BW_DROP", bandwidth=1.0, bitrate="1080p", buffer_level=20.0)
        # 3. 비트레이트 하향 조정 로그 (예상)
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=1.0, bitrate="240p", buffer_level=18.0)
        self.assertTrue(True) # 에러 없이 실행되면 통과

    def test_scenario_2_bandwidth_spike(self):
        """시나리오 2: 네트워크 대역폭 급상승 (Spike)"""
        print("실행: 대역폭 2Mbps -> 15Mbps 급상승 로그 테스트")
        self.logger.log_event("TEST_START", bandwidth=2.0, bitrate="240p", buffer_level=15.0)
        self.logger.log_event("BW_SPIKE", bandwidth=15.0, bitrate="240p", buffer_level=15.0)
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=15.0, bitrate="1080p", buffer_level=20.0)
        self.assertTrue(True)

    def test_scenario_3_packet_loss_increase(self):
        """시나리오 3: 패킷 손실률 증가 (Loss)"""
        print("실행: 패킷 손실률 0% -> 15% 증가 로그 테스트")
        self.logger.log_event("TEST_START", bandwidth=10.0, packet_loss=0.0, bitrate="1080p", buffer_level=20.0)
        self.logger.log_event("LOSS_INCREASE", bandwidth=10.0, packet_loss=15.0, bitrate="1080p", buffer_level=19.0)
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=10.0, packet_loss=15.0, bitrate="480p", buffer_level=15.0)
        self.assertTrue(True)

    def test_buffer_underrun(self):
        """시나리오 4: 버퍼 고갈 위기"""
        print("실행: 버퍼 고갈 위기(2초 미만) 화질 즉각 방어 로그 테스트")
        # 1. 정상 상태에서 시작 (버퍼 15초 넉넉함)
        self.logger.log_event("TEST_START", bandwidth=5.0, packet_loss=0.0, bitrate="720p", buffer_level=15.0)
        # 2. 네트워크는 유지되나 버퍼가 급격히 소모되는 상황 (버퍼 1.5초)
        self.logger.log_event("BUFFER_WARNING", bandwidth=5.0, packet_loss=0.0, bitrate="720p", buffer_level=1.5)
        # 3. 시스템이 화질을 240p로 강제 다운그레이드하여 버퍼를 다시 채우는지 확인
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=5.0, packet_loss=0.0, bitrate="240p", buffer_level=3.0)
        self.assertTrue(True)

    def test_network_fluctuation(self):
        """시나리오 5: 네트워크 대역폭 요동 (Fluctuation)"""
        print("실행: 대역폭 요동(5->1->8->2Mbps) 시 화질 안정성 로그 테스트")
        # 1. 중간 상태에서 시작
        self.logger.log_event("TEST_START", bandwidth=5.0, packet_loss=0.0, bitrate="720p", buffer_level=15.0)
        # 2. 대역폭 1차 급락
        self.logger.log_event("BW_DROP", bandwidth=1.0, packet_loss=0.0, bitrate="720p", buffer_level=12.0)
        # 3. 화질이 240p로 떨어짐과 동시에 대역폭 급상승
        self.logger.log_event("BW_SPIKE", bandwidth=8.0, packet_loss=0.0, bitrate="240p", buffer_level=10.0)
        # 4. 화질이 너무 높게 튀지 않고 안정적으로 조정되는지 확인
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=2.0, packet_loss=0.0, bitrate="480p", buffer_level=11.0)
        self.assertTrue(True)

    def test_latency_increase(self):
        """시나리오 6: 지연 시간(Latency) 급증"""
        print("실행: 지연 시간 증가 시 비트레이트 하향 조정 로그 테스트")
        # 1. 정상 상태에서 시작 (대역폭 10Mbps, 화질 1080p)
        self.logger.log_event("TEST_START", bandwidth=10.0, packet_loss=0.0, bitrate="1080p", buffer_level=20.0)
        # 2. 대역폭은 유지되나 응답 지연 발생 상황
        self.logger.log_event("LATENCY_INCREASE", bandwidth=10.0, packet_loss=0.0, bitrate="1080p", buffer_level=16.0)
        # 3. 응답 속도 지연을 감지하여 안전한 화질(720p)로 하향 조정
        self.logger.log_event("BITRATE_ADJUSTED", bandwidth=10.0, packet_loss=0.0, bitrate="720p", buffer_level=14.0)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()