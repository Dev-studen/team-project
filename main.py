import argparse
import os
import time
import sys

# src 폴더 내의 모듈을 불러오기 위한 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    import test_scenarios
except ImportError:
    test_scenarios = None

def main():
    parser = argparse.ArgumentParser(description="ABR Simulator CLI")
    parser.add_argument("--mode", type=str, default="normal", help="Execution mode (e.g., demo)")
    args = parser.parse_args()

    if args.mode == "demo":
        print("=== [10주차 DEMO MODE] 실시간 시나리오 및 로그 동기화 구동 ===")
        print("시나리오별 단계(steps)와 대기 시간(sleep_times)에 맞춰 라이브 시연을 시작합니다...\n")
        
        # test_scenarios 모듈과 내부에 정의된 SCENARIOS 데이터가 존재하는 경우 연동
        if test_scenarios and hasattr(test_scenarios, 'SCENARIOS'):
            scenarios = test_scenarios.SCENARIOS
            
            for idx, sc in enumerate(scenarios, 1):
                print(f"\n────────────────────────────────────────")
                print(f"▶ [시나리오 {idx}] {sc.get('title', '통합 테스트')}")
                print(f"────────────────────────────────────────")
                
                steps = sc.get('steps', [])
                sleep_times = sc.get('sleep_times', [])
                
                for step_idx, step in enumerate(steps):
                    # 단계별 실시간 이벤트 및 네트워크 상태 로그 출력
                    print(f"  - [LOG] 이벤트: {step.get('event')}")
                    print(f"    상태 정보 -> 대역폭: {step.get('bw')}Mbps | 패킷손실: {step.get('loss')}% | 버퍼: {step.get('buffer')}초")
                    print(f"    설명: {step.get('desc')}")
                    
                    # 시연 호흡 조절 (설정된 sleep_time 반영, 발표 속도에 맞춰 필요시 조절 가능)
                    if step_idx < len(sleep_times):
                        wait_time = sleep_times[step_idx]
                        # 너무 길면 시연이 지연되므로 적절히 축소하거나 그대로 적용
                        time.sleep(min(wait_time, 2.0)) 
                    else:
                        time.sleep(1.0)
                        
            print("\n=== [10주차 DEMO MODE] 모든 실시간 시나리오 연동 및 시연 완료 ===")
        else:
            # Fallback: 만약 데이터 구조가 다르다면 기존 방식(스크립트 통째 실행)으로 우회
            print("[INFO] test_scenarios 내부 데이터를 찾지 못해 기본 실행 스크립트로 대체합니다.")
            os.system("python src/test_scenarios.py")
            
    else:
        print("Normal mode activated.")

if __name__ == "__main__":
    main()
