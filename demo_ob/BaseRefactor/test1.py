import subprocess
import csv

output_file = "simulation_results.csv"

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Run", "Total Dirt Collected"])

    for i in range(30):
        print(f"Running simulation {i+1}/30...")
        
        result = subprocess.run(
            ['python', 'main.py'],
            capture_output=True, text=True
        )
        
        output = result.stdout
        if "total dirt collected in" in output:
            collected_data = output.split("total dirt collected in")[-1].split("is")
            moves = collected_data[0].strip()
            dirt_collected = collected_data[1].strip()
            writer.writerow([i+1, dirt_collected])

        else:
            print(f"Error: Could not find expected output in run {i+1}.")
    
print(f"Results saved to {output_file}")
