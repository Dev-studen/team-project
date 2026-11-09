import datetime
import os
import csv

class SystemLogger:
    def __init__(self):
        # 터미널 출력용 ANSI 색상 코드 정의
        self.RESET = "\033[0m"
        self.RED = "\033[91m"     # 위기/경고
        self.GREEN = "\033[92m"   # 정상/시작
        self.YELLOW = "\033[93m"  # 조치/변경
        
        # 결과를 저장할 CSV 파일 (기존 로그 저장 기능 유지)
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"results/simulation_log_{timestamp}.csv"
        
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "Event", "Bandwidth(Mbps)", "Packet_Loss(%)", "Bitrate", "Buffer(s)"])

    def log_event(self, event_type, bandwidth, bitrate, buffer_level, packet_loss=0.0):
        time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # 이벤트 종류에 따라 색상 매칭
        if event_type == "TEST_START":
            color = self.GREEN
        elif event_type in ["BW_DROP", "LOSS_INCREASE", "BUFFER_WARNING", "LATENCY_INCREASE"]:
            color = self.RED
        elif event_type in ["BITRATE_ADJUSTED", "BW_SPIKE"]:
            color = self.YELLOW
        else:
            color = self.RESET

        # 1. 터미널에 컬러로 출력
        log_msg = f"[{time_str}] {color}{event_type}{self.RESET} | BW: {bandwidth:.1f}Mbps | Loss: {packet_loss}% | Bitrate: {bitrate} | Buffer: {buffer_level}s"
        print(log_msg)
        
        # 2. 백그라운드에서는 CSV 파일로 기록 저장
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str, event_type, bandwidth, packet_loss, bitrate, buffer_level])