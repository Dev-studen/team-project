import logging
import csv
import os
from datetime import datetime

class SystemLogger:
    def __init__(self, log_dir="results"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 로그 파일명 (실행 시간 기준)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"simulation_log_{timestamp}.csv")
        
        # CSV 헤더 초기화
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Event_Type", "Bandwidth", "Packet_Loss", "Bitrate", "Buffer_Level"])
            
    def log_event(self, event_type, bandwidth, packet_loss, bitrate, buffer_level):
        """
        이벤트를 CSV 파일에 기록하는 메서드 (뼈대)
        event_type: 'NETWORK_CHANGE', 'BITRATE_CHANGE', 'BUFFER_WARNING' 등
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, event_type, bandwidth, packet_loss, bitrate, buffer_level])
            
        # 터미널에도 동시 출력 (추후 Streamlit UI 연동 전 확인용)
        print(f"[{timestamp}] {event_type} | BW: {bandwidth} | Loss: {packet_loss} | Bitrate: {bitrate} | Buffer: {buffer_level}")

# 단독 실행 테스트용 뼈대 코드
if __name__ == "__main__":
    logger = SystemLogger()
    logger.log_event("INIT", 10.0, 0.0, "1080p", 30.0)