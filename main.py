import argparse

def main():
    parser = argparse.ArgumentParser(description="ABR Simulator CLI")
    # --mode demo 플래그 처리 구조
    parser.add_argument("--mode", type=str, default="normal", help="Execution mode (e.g., demo)")
    args = parser.parse_args()

    if args.mode == "demo":
        print("Demo mode activated.")
    else:
        print("Normal mode activated.")

if __name__ == "__main__":
    main()
