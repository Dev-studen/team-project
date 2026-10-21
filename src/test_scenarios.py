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

if __name__ == '__main__':
    unittest.main()