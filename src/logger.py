import logging
import csv
import os
import time
from datetime import datetime

class SystemLogger:
    def __init__(self, log_dir="results"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"simulation_log_{timestamp}.csv")
        self.pending_requests = {}
        
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "Event_Type", "Segment_ID", "Req_Time", "Res_Time", "Download_Time(s)", 
                "Bandwidth(Mbps)", "Packet_Loss(%)", "Bitrate", "Buffer_Level(s)"
            ])
            
    def _write_to_csv(self, data_list):
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data_list)
            
    def log_event(self, event_type, bandwidth=0, packet_loss=0, bitrate="N/A", buffer_level=0):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._write_to_csv([timestamp, event_type, "-", "-", "-", "-", bandwidth, packet_loss, bitrate, buffer_level])
        print(f"[{timestamp}] {event_type} | BW: {bandwidth}Mbps | Loss: {packet_loss}% | Bitrate: {bitrate} | Buffer: {buffer_level}s")

    def log_segment_request(self, segment_id, bandwidth, bitrate, buffer_level):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        req_time = time.time()
        self.pending_requests[segment_id] = req_time
        
        self._write_to_csv([timestamp, "SEGMENT_REQUEST", segment_id, req_time, "-", "-", bandwidth, "-", bitrate, buffer_level])
        print(f"[{timestamp}] REQ Segment {segment_id} | Target Bitrate: {bitrate}")
        
    def log_segment_response(self, segment_id, bandwidth, packet_loss, bitrate, buffer_level):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        res_time = time.time()
        
        if segment_id in self.pending_requests:
            req_time = self.pending_requests.pop(segment_id)
            download_time = round(res_time - req_time, 3)
        else:
            req_time = "Unknown"
            download_time = "Unknown"
            
        self._write_to_csv([timestamp, "SEGMENT_RESPONSE", segment_id, req_time, res_time, download_time, bandwidth, packet_loss, bitrate, buffer_level])
        print(f"[{timestamp}] RES Segment {segment_id} 완료 | 소요 시간: {download_time}s | Buffer: {buffer_level}s")

# 6주차 단독 테스트 로직
if __name__ == "__main__":
    print("--- 6주차 로그 모듈 단독 테스트 시작 ---")
    logger = SystemLogger()
    logger.log_event("INIT", bandwidth=10.0, packet_loss=0.0, bitrate="720p", buffer_level=10.0)
    time.sleep(0.5)
    
    logger.log_segment_request(segment_id=1, bandwidth=10.0, bitrate="720p", buffer_level=10.0)
    time.sleep(1.2) # 네트워크 지연 1.2초 모사
    
    logger.log_segment_response(segment_id=1, bandwidth=9.5, packet_loss=1.5, bitrate="720p", buffer_level=12.0)