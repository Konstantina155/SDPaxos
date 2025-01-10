import subprocess
import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def run_analysis(filename, requests):
    path = f"./logs-3-replicas-{filename}"

    command = ["python3", f"analysis.py", f"{path}/{filename}-S3-C20-r{requests}-b1-c0--client0.out"]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def parse_output(output):
    throughput_match = re.search(r"Throughput \(reqs/sec\): (\d+\.\d+)", output)
    #median_match = re.search(r"Median latency: (\d+\.\d+)ms", output)
    #percentile_match = re.search(r"99th percentile latency: (\d+\.\d+)ms", output)
    if throughput_match:
        return float(throughput_match.group(1)) #, float(median_match.group(1)), float(percentile_match.group(1))
    else:
        raise ValueError("Failed to parse latency output")

def create_plots(system, output, requests):
    throughput = parse_output(output)
    df = pd.DataFrame({
        'Throughput': [throughput],
        'System': [system],
        'Requests': [requests]
    })
    return df

def thousands_formatter(x):
    if x == 0:
        return "0"
    elif x < 1000:
        return ""
    else:
        return f"{int(x / 1000)}K"

systems = ["Multi-Paxos", "Mencius", "EPaxos", "SDPaxos"]
file_names = ["paxos0", "mencius0", "epaxos0", "sdpaxos0"]
requests = [5000, 20000]

dfs = []
for system, file_name in zip(systems, file_names):
    for request in requests:
        output = run_analysis(file_name, request)
        df = create_plots(system, output, request)
        dfs.append(df)

result_df = pd.concat(dfs, ignore_index=True)

custom_palette = sns.color_palette(["#FF5733", "#33FF57", "#3357FF", "#F333FF"])
plt.figure(figsize=(8, 6))
unique_requests = sorted(result_df['Requests'].unique())
bar_width = 0.1
positions = {
    request: np.arange(len(systems)) * (bar_width + 0.015) + idx * (len(systems) + 1) * bar_width
    for idx, request in enumerate(unique_requests)
}

for idx, system in enumerate(systems):
    for request in unique_requests:
        position = positions[request][idx]
        subset = result_df[(result_df['Requests'] == request) & (result_df['System'] == system)]
        throughput = subset['Throughput'].values[0] if not subset.empty else 0
        plt.bar(
            position,
            throughput,
            width=bar_width,
            color=custom_palette[idx],
            edgecolor="black",
            label=system if request == unique_requests[0] else ""  # Add legend only once
        )

yticks_values = plt.gca().get_yticks()
formatted_yticks = [thousands_formatter(value) for value in yticks_values]
previous_value = ""
for idx, value in enumerate(formatted_yticks):
    if value == "":
        continue
    else:
        if previous_value == value:
            formatted_yticks[idx] = ""
        else:
            formatted_yticks[idx] = value
    previous_value = formatted_yticks[idx]
plt.yticks(yticks_values, formatted_yticks, fontsize=18)

plt.xticks(
    [np.mean(positions[request]) for request in unique_requests],
    [f"{request} Requests" for request in unique_requests], fontsize=18
)
plt.ylabel("Throughput (reqs/sec)", fontsize=20)
plt.title("Writes", fontsize=20)
plt.legend(loc="upper right", fontsize=20)
plt.tight_layout()
plt.savefig('../plots/No_conflicts_all_systems.pdf', format='pdf')
