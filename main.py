import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="ABR Simulator CLI")
    parser.add_argument("--mode", type=str, default="normal", help="Execution mode (e.g., demo)")
    args = parser.parse_args()

    if args.mode == "demo":
        print("=== 데모 모드 구동 중 ===")
        print("시나리오 통합 테스트 파이프라인을 실행합니다...\n")
        
        try:
            # os.system 대신 subprocess를 사용하여 안정적인 실행 및 예외 포착
            subprocess.run([sys.executable, "src/test_scenarios.py"], check=True)
            print("\n=== 데모 모드가 성공적으로 완료되었습니다. ===")
        except subprocess.CalledProcessError as e:
            print(f"\n[오류] 시연 시나리오 실행 중 비정상 종료가 발생했습니다: {e}")
        except FileNotFoundError:
            print("\n[오류] 'src/test_scenarios.py' 경로를 찾을 수 없습니다. 파일 위치를 확인해주세요.")
            
    else:
        print("Normal mode activated.")

if __name__ == "__main__":
    main()
