import statistics
import re
import sys
import concurrent.futures

# calculate the analysis the same way the Rabia authors did to compare with their results

#example: np_paxos-S3-C2-r20000-b1-c0--client0.out
def extract_configurations():
    filename_info = re.findall(r'-S(\d+)-C(\d+)-r(\d+)-b(\d+)-c(-?\d+)--client(\d+)', filename)
    if filename_info:
        replicas = int(filename_info[0][0])
        clients = int(filename_info[0][1])
        reqs = int(filename_info[0][2])
        batch_size = int(filename_info[0][3])
        conflicts = int(filename_info[0][4])
        client_num = int(filename_info[0][5])
        return replicas, clients, reqs, batch_size, conflicts, client_num
    else:
        print("Unable to extract server and client numbers from the filename.")
        return None, None, None, None, None, None

def calculate_metrics(client_filename):
    latencies = []  # in ms
    result = {}
    with open(client_filename) as f:
        lines = f.readlines()

    for line in lines:
        if "Round took" in line:
            match = re.search(r'Round took (\d+\.\d+)', line)
            if match:
                latencies.append(float(match.group(1).strip()[:-2]) * 1000)
            else:
                return {}
    latencies = latencies[int(len(latencies) * 0.1): int(len(latencies) * 0.9)]
    latencies = sorted(latencies)
    if len(latencies) == 0:
        return {}

    result["duration"] = sum(latencies)
    result["requests"] = len(latencies)
    result["median"] = latencies[int(len(latencies) * 0.5)]
    result["p99"] = latencies[int(len(latencies) * 0.99)]
    return result

def analyze_throughput_latency():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        metrics = []
        for i in range(clients):
            client_filename = filename.replace(f"client{client_num}", f"client{i}")
            metrics.append(executor.submit(calculate_metrics, client_filename))
        futures_res = [f.result() for f in metrics if f.result() != {}]
        
        median_latency = round(sum([d["median"] for d in futures_res]) / len(futures_res), 2)
        p99_latency = round(sum([d["p99"] for d in futures_res]) / len(futures_res), 2)
        throughput = round(sum([d['requests'] * batch_size / (d['duration'] / 1000) for d in futures_res]), 2)
        print(f"Throughput (reqs/sec): {throughput}")

def calculate_duration_and_ops(client_filename):
    with open(client_filename, 'r') as f:
        lines = f.readlines()
    duration, operations = 0, 0
    for line in lines:
        if "Test took" in line:
            match = re.search(r'Test took (\d+\.\d+)', line)
            if match:
                duration = round(float(match.group(1)), 2)
            else:
                return None, None
        if "Successful:" in line:
            match = re.search(r'Successful:\s*(\d+)', line)
            if match:
                operations = int(match.group(1))
            else:
                return None, None
    return duration, operations

def analyze_throughput_for_each_client():
    durations = []
    for i in range(clients):
        client_filename = filename.replace(f"client{client_num}", f"client{i}")
        duration, operations = calculate_duration_and_ops(client_filename)
        #print(f"Client {i}: Duration: {duration}, Operations: {operations}")
        assert operations == reqs, f"client {i}'s successful operations != num of requests per client"
        durations.append(duration)
    assert len(durations) == clients, "actual number of clients != parameter"

    total_requests = clients * reqs
    throughput = round(total_requests / max(durations), 2)
    print(f"Throughput (reqs/sec): {throughput}")

# My addition, the Rabia github does not provide a latency analysis when open-loop
def analyze_latency_for_each_client():
    latencies = []
    for i in range(clients):
        client_filename = filename.replace(f"client{client_num}", f"client{i}")
        with open(client_filename, 'r') as f:
            lines = f.readlines()

        client_latencies = []
        for line in lines:
            if "Round took" in line:
                match = re.search(r'Round took (\d+\.\d+)', line)
                if match:
                    client_latencies.append(float(match.group(1).strip()[:-2]) * 1000)
        latencies.extend(client_latencies)

    if latencies:
        median_latency = statistics.median(latencies)
        percentile_latency = statistics.quantiles(latencies, n=100, method='inclusive')[-1]

        print(f"Median latency: {median_latency}ms")
        print(f"99th percentile latency: {percentile_latency}ms")
    else:
        print("No latency data found in any of the client files.")


# start NP (table1) implementation for analysis (probably not gonna use it)
def extract_time(line):
    words = line.split(" ")
    if len(words) != 3 or words[1] != "took":
        return None

    match = re.search(r'\d+\.\d+', line)
    if match:
        return float(match.group())
    else:
        return None
    
def analyze_latency():
    with open(filename, 'r') as f:
        lines = f.readlines()

    latencies = []
    for line in lines:
        words = line.split(" ")
        if len(words) != 3 or words[0] != "Round":
            continue

        match = re.search(r'\d+\.\d+', line)
        if match:
            milliseconds = float(match.group()) * 1000
            latencies.append(milliseconds)

    if latencies:
        median_latency = statistics.median(latencies)
        percentile_latency = statistics.quantiles(latencies, n=100, method='inclusive')[-1]

        print(f"Median latency: {median_latency}ms")
        print(f"99th percentile latency: {percentile_latency}ms")
    else:
        print("No latency data found in the file.")

def analyze_throughput():
    with open(filename, 'r') as f:
        lines = f.readlines()

    start_time = 0
    end_time = 0
    flag = False
    for line in lines:
        time = extract_time(line)
        if time is not None:
            if flag:
                end_time = time
            else:
                start_time = time
                flag = True

    if flag:
        time_in_s = end_time - start_time
        throughput = (clients * reqs) / time_in_s

        print("Throughput (reqs/sec):", throughput)
    else:
        print("No throughput data found in the file.")
# end NP (table1) implementation for analysis



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3.8 analysis.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    replicas, clients, reqs, batch_size, conflicts, client_num = extract_configurations()
    # analyze_throughput_latency() when close loop (batching)
    # open loop (rounds = reqs / bacth_size = 1)
    analyze_throughput_for_each_client()
    # analyze_latency_for_each_client()