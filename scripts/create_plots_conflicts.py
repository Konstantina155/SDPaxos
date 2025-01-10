import subprocess
import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def find_conflicts(filename):
    match = re.search(r'paxos(\d+)', filename)
    if match:
        return int(match.group(1))
    else:
        return -1
    
def run_analysis(filename, requests, replicas, conflicts):
    path = f"./logs-{replicas}-replicas-{filename}"
    
    command = ["python3", f"analysis.py", f"{path}/{filename}-S{replicas}-C20-r{requests}-b1-c{conflicts}--client0.out"]
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

def create_plots(system, output, requests, replicas, conflicts):
    throughput = parse_output(output)
    df = pd.DataFrame({
        'Throughput': [throughput],
        'System': [system],
        'Requests': [requests],
        'Conflicts': [conflicts],
        'Replicas': [replicas]
    })
    return df

systems = ["EPaxos 0%", "EPaxos 5%", "EPaxos 25%", "EPaxos 50%", "EPaxos 75%", "EPaxos 100%", "SDPaxos 0%", "SDPaxos 5%", "SDPaxos 25%", "SDPaxos 50%", "SDPaxos 75%", "SDPaxos 100%"]
file_names = ["epaxos0", "epaxos5", "epaxos25", "epaxos50", "epaxos75", "epaxos100", "sdpaxos0", "sdpaxos5", "sdpaxos25", "sdpaxos50", "sdpaxos75", "sdpaxos100"]
requests = [5000, 20000]
replicas = [3, 5]
markers=['o', 's', 'd', '*']

for request in requests:
    dfs = []
    for system, file_name in zip(systems, file_names):
        for replica in replicas:
            conflicts = find_conflicts(file_name)
            if conflicts == -1:
                print("Unable to extract conflicts from the filename.")
                exit(1)
    
            output = run_analysis(file_name, request, replica, conflicts)
            df = create_plots(system, output, request, replica, conflicts)
            dfs.append(df)

    result_df = pd.concat(dfs, ignore_index=True)

    request_df = result_df[result_df['Requests'] == request]
    
    plt.figure(figsize=(8, 6))
    for system in ["EPaxos", "SDPaxos"]:
        for replica in replicas:
            subset = request_df[
                (request_df['System'].str.startswith(system)) &
                (request_df['Replicas'] == replica)
            ]

            subset = subset.sort_values('Conflicts')
            marker_idx = (replicas.index(replica) + ["EPaxos", "SDPaxos"].index(system)) % len(markers)

            plt.plot(
                subset['Conflicts'],
                subset['Throughput'],
                marker=markers[marker_idx],
                label=f"{system}/{replica} replicas"
            )

    plt.xticks([0, 5, 25, 50, 75, 100], labels=["0", "5", "25", "50", "75", "100"], fontsize=16)
    yticks = np.arange(0, 8000, 1000)
    plt.yticks(yticks, labels=[f"{int(y/1000)}K" if y != 0 else "0" for y in yticks], fontsize=16)

    plt.title(f"{request} Requests", fontsize=20)
    plt.xlabel("Conflict Rate (%)", fontsize=18)
    plt.ylabel("Throughput (reqs/sec)", fontsize=18)
    plt.legend(loc="upper right", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"../plots/Conflicts_{request}_requests.pdf", format='pdf')
