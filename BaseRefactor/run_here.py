import subprocess
import csv


output_file = "logging/most_dirty_heu_simulation_results.csv"
milestones = [100, 200, 300, 400, 500]

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 添加里程碑列
    header = ["Run", "Total Dirt Collected"] + [f"Dirt at {m} moves" for m in milestones]
    writer.writerow(header)
    # writer.writerow(["Run", "Total Dirt Collected"])

    for i in range(30):
        print(f"Running simulation {i + 1}/30...")

        result = subprocess.run(
            ['python', 'main.py'],
            capture_output=True, text=True
        )

        output = result.stdout
        # 解析里程碑数据
        milestone_data = {}
        for line in output.split('\n'):
            if line.startswith("Move "):
                parts = line.split(": Collected ")
                move = int(parts[0].replace("Move ", ""))
                dirt = int(parts[1].replace(" dirt", ""))
                milestone_data[move] = dirt

        # 获取最终结果
        total_dirt = 0
        if "total dirt collected in" in output:
            total_dirt = int(output.split("total dirt collected in")[-1].split("is")[1].strip())

        # 写入CSV
        row = [i + 1, total_dirt] + [milestone_data.get(m, -1) for m in milestones]
        writer.writerow(row)


        # output = result.stdout
        # if "total dirt collected in" in output:
        #     collected_data = output.split("total dirt collected in")[-1].split("is")
        #     moves = collected_data[0].strip()
        #     dirt_collected = collected_data[1].strip()
        #     writer.writerow([i + 1, dirt_collected])
        #
        # else:
        #     print(f"Error: Could not find expected output in run {i + 1}.")

print(f"Results saved to {output_file}")
