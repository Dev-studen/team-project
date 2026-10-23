import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="ABR Simulator CLI")
    parser.add_argument("--mode", type=str, default="normal", help="Execution mode (e.g., demo)")
    args = parser.parse_args()

    if args.mode == "demo":
        print("Demo mode activated. 3가지 시나리오 통합 테스트를 시작합니다...\n")
        os.system("python src/test_scenarios.py")
    else:
        print("Normal mode activated.")

if __name__ == "__main__":
    main()