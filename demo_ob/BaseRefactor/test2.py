import subprocess
import csv
import re
import sys

def run_simulations(main_script_path: str, runs: int = 30, output_csv: str = "simulation_outputs.csv"):
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Run", "Total Dirt Collected", "Moves"])

        for i in range(1, runs + 1):
            print(f"Running simulation {i}/{runs}...")
            proc = subprocess.run(
                [sys.executable, main_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            output = proc.stdout.decode("utf-8", errors="replace").strip()
            nums = re.findall(r"\d+", output)
            if len(nums) >= 2:
                dirt_collected, moves = nums[0], nums[1]
                writer.writerow([i, dirt_collected, moves])
            else:
                writer.writerow([i, "", ""])
                print(output)

    print(f"All simulations done. Results saved to '{output_csv}'.")

if __name__ == "__main__":
    run_simulations("main.py", runs=30, output_csv="simulation_results.csv")
