import argparse
import os
import time

def main():
    parser = argparse.ArgumentParser(description="ABR Simulator CLI")
    parser.add_argument("--mode", type=str, default="normal", help="Execution mode (e.g., demo)")
    args = parser.parse_args()

    if args.mode == "demo":
        print("3가지 시나리오 통합 테스트 파이프라인을 시작합니다...\n")
        
        # [9주차 핵심] 데모 모드 진입 시 팀원들과 연동된 테스트/시나리오 스크립트 실행
        os.system("python src/test_scenarios.py")
        
        # [10~11주차 확장 포인트]
        # 향후 발표 시연 시간에 맞춘 세부 호흡 조절 및 로그 연출 코드가 
        # 팀원들과의 조율을 거쳐 이 위치나 내부 함수로 확장될 예정입니다.
        
        print("\n=== [DEMO MODE] 파이프라인 실행 완료 ===")
    else:
        print("Normal mode activated.")

if __name__ == "__main__":
    main()
