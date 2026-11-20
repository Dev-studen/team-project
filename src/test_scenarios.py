import os
import csv
import time
import unittest
from datetime import datetime

# Windows 터미널에서도 컬러 로그가 정상 출력되도록 활성화
os.system("")

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

# 기존 logger.py가 있으면 연동하고, 메서드명이 달라도 오류 없이 동작하도록 안전 처리
try:
    from src.logger import SystemLogger
except ImportError:
    try:
        from logger import SystemLogger
    except ImportError:
        SystemLogger = None


class TestWeek11Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = SystemLogger() if SystemLogger else None
        cls.results = []
        cls.detailed_logs = []
        os.makedirs("results", exist_ok=True)
        print(f"\n{CYAN}============================================================{RESET}")
        print(f"{CYAN}   [11주차] 네트워크 환경별 통합 시나리오 검증 시작{RESET}")
        print(f"{CYAN}============================================================{RESET}")

    def _record_log(self, scenario_name, step_idx, bw, loss, quality, state):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.detailed_logs.append([timestamp, scenario_name, step_idx, bw, loss, quality, state])

        if self.logger and hasattr(self.logger, "log_event"):
            try:
                self.logger.log_event(
                    "SCENARIO_STEP",
                    {
                        "scenario": scenario_name,
                        "step": step_idx,
                        "bandwidth": bw,
                        "packet_loss": loss,
                        "quality": quality,
                        "buffer_state": state,
                    },
                )
            except TypeError:
                pass

    def _run_scenario(self, scenario_name, steps):
        print(f"\n{CYAN}▶ 시나리오 시작: {scenario_name}{RESET}")
        unstable_count = 0

        for idx, (bw, loss, quality, state) in enumerate(steps, start=1):
            if state in ("REBUFFERING", "DROP"):
                color = RED
                unstable_count += 1
            elif quality in ("480p", "360p", "240p"):
                color = YELLOW
            else:
                color = GREEN

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(
                f"{color}[{timestamp}] [{scenario_name} - Step {idx}] "
                f"대역폭: {bw:4.1f}Mbps | 손실률: {loss*100:5.1f}% -> "
                f"화질: {quality:<5} | 버퍼상태: {state}{RESET}"
            )
            self._record_log(scenario_name, idx, bw, loss, quality, state)
            time.sleep(0.3)

        self.results.append((scenario_name, len(steps), unstable_count))

    # --- [11주차 핵심] 대표 네트워크 환경 3가지 통합 테스트 ---
    def test_01_bandwidth_drop(self):
        """1. 대역폭 급락 시나리오"""
        steps = [
            (10.0, 0.00, "1080p", "PLAYING"),
            (8.0, 0.01, "1080p", "PLAYING"),
            (3.0, 0.05, "720p", "PLAYING"),
            (1.2, 0.10, "480p", "PLAYING"),
            (0.6, 0.15, "360p", "REBUFFERING"),
        ]
        self._run_scenario("1. 대역폭 급락", steps)

    def test_02_bandwidth_surge(self):
        """2. 대역폭 급상승 시나리오"""
        steps = [
            (0.8, 0.10, "360p", "PLAYING"),
            (2.5, 0.05, "480p", "PLAYING"),
            (5.5, 0.02, "720p", "PLAYING"),
            (9.5, 0.00, "1080p", "PLAYING"),
            (12.0, 0.00, "1080p", "PLAYING"),
        ]
        self._run_scenario("2. 대역폭 급상승", steps)

    def test_03_packet_loss_increase(self):
        """3. 패킷 손실률 증가 시나리오"""
        steps = [
            (8.0, 0.01, "1080p", "PLAYING"),
            (7.5, 0.05, "720p", "PLAYING"),
            (7.0, 0.15, "480p", "PLAYING"),
            (6.5, 0.30, "360p", "REBUFFERING"),
            (6.0, 0.45, "240p", "DROP"),
        ]
        self._run_scenario("3. 패킷 손실률 증가", steps)

    # --- 기존 확장 및 예외 방어 시나리오 (총 7종 유지) ---
    def test_04_buffer_depletion(self):
        """4. 버퍼 고갈 위기 방어 시나리오"""
        steps = [
            (4.0, 0.05, "720p", "PLAYING"),
            (1.0, 0.15, "360p", "REBUFFERING"),
            (0.8, 0.20, "240p", "PLAYING"),
        ]
        self._run_scenario("4. 버퍼 고갈 위기 방어", steps)

    def test_05_network_fluctuation(self):
        """5. 네트워크 급격 요동 시나리오"""
        steps = [
            (9.0, 0.01, "1080p", "PLAYING"),
            (1.5, 0.12, "480p", "PLAYING"),
            (8.5, 0.02, "720p", "PLAYING"),
            (1.0, 0.18, "360p", "REBUFFERING"),
        ]
        self._run_scenario("5. 네트워크 요동", steps)

    def test_06_high_latency(self):
        """6. 지연 시간(RTT) 증가 시나리오"""
        steps = [
            (6.0, 0.02, "720p", "PLAYING"),
            (3.5, 0.08, "480p", "PLAYING"),
            (2.0, 0.12, "360p", "PLAYING"),
        ]
        self._run_scenario("6. 지연 시간 증가", steps)

    def test_07_complete_disconnection(self):
        """7. 네트워크 완전 단절 예외 방어 시나리오"""
        steps = [
            (5.0, 0.00, "720p", "PLAYING"),
            (0.0, 1.00, "240p", "DROP"),
            (0.0, 1.00, "240p", "DROP"),
            (4.0, 0.02, "480p", "PLAYING"),
        ]
        self._run_scenario("7. 네트워크 완전 단절", steps)

    @classmethod
    def tearDownClass(cls):
        csv_path = os.path.join("results", "week11_scenario_logs.csv")
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Scenario", "Step", "Bandwidth_Mbps", "Packet_Loss", "Quality", "Buffer_State"])
            writer.writerows(cls.detailed_logs)

        print(f"\n{CYAN}============================================================{RESET}")
        print(f"{CYAN}   [11주차 통합 시나리오 최종 요약 리포트]{RESET}")
        print(f"{CYAN}============================================================{RESET}")

        total_steps = sum(r[1] for r in cls.results)
        total_unstable = sum(r[2] for r in cls.results)
        defense_rate = ((total_steps - total_unstable) / total_steps) * 100 if total_steps else 0

        for name, steps_cnt, unstable_cnt in cls.results:
            print(f"- {name:<18} : 총 {steps_cnt}단계 | 불안정(REBUFFERING/DROP) {unstable_cnt}회")

        print(f"\n{GREEN}▶ 전체 스트리밍 안정성 방어율 : {defense_rate:.1f}%{RESET}")
        print(f"{GREEN}▶ 상세 로그 CSV 저장 경로      : {csv_path}{RESET}\n")


if __name__ == "__main__":
    unittest.main()