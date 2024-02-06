import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime, timedelta

# Function to parse a log file and extract intervals, and return the minimum timestamp
def parse_log(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()

    regex = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}) - RabbitMQ status: (\w+)'
    timestamps = []
    statuses = []
    for line in data:
        match = re.match(regex, line)
        if match:
            timestamps.append(datetime.fromisoformat(match.group(1)))
            statuses.append(match.group(2))

    df = pd.DataFrame({'timestamp': timestamps, 'status': statuses})
    min_time = df['timestamp'].min()
    return df, min_time

# Function to accurately calculate the recovery or runtime intervals
def calculate_intervals(df, status_start, status_end):
    intervals = []
    in_interval = False
    for i in range(1, len(df)):
        if df.iloc[i-1]['status'] == status_start and df.iloc[i]['status'] == status_end:
            start = df.iloc[i]['timestamp']
            in_interval = True
        elif in_interval and df.iloc[i]['status'] == status_start:
            end = df.iloc[i]['timestamp']
            intervals.append((start, end))
            in_interval = False
    return intervals

# Function to calculate the average time from a list of intervals
def calculate_average_time(intervals):
    total_time = sum([(end - start).total_seconds() for start, end in intervals])
    return total_time / len(intervals) if intervals else 0

# Function to determine intervals during which a node was a master
def determine_master_intervals(intervals, df_messages, node_name, start_time):
    master_intervals = []
    for start, end in intervals:
        start_minutes = (start - start_time).total_seconds() / 60
        end_minutes = (end - start_time).total_seconds() / 60
        
        if any((df_messages['TimeElapsed (s)'] >= start_minutes * 60) & 
               (df_messages['TimeElapsed (s)'] <= end_minutes * 60) & 
               (df_messages['masternode'] == node_name)):
            master_intervals.append((start, end))
    return master_intervals

# File paths for the original and second set of log files and results.csv
file_paths = {
    'node0': ['data17/node0_5000_monitoring.log', 'data18/node0_5000_monitoring.log', 'data19/node0_5000_monitoring.log'],
    'node1': ['data17/node1_5000_monitoring.log', 'data18/node1_5000_monitoring.log', 'data19/node1_5000_monitoring.log'],
    'node2': ['data17/node2_5000_monitoring.log', 'data18/node2_5000_monitoring.log',  'data19/node2_5000_monitoring.log']
}
file_path_messages = ['data17/results.csv', 'data18/results.csv', 'data19/results.csv']

# Parse log files and combine DataFrames
dfs_nodes = {}
start_times = {}
for node, paths in file_paths.items():
    dfs = [parse_log(path) for path in paths]
    combined_df = pd.concat([df for df, _ in dfs], ignore_index=True)
    min_time = min([min_time for _, min_time in dfs])
    dfs_nodes[node] = combined_df
    start_times[node] = min_time

# Combine messages DataFrames
df_messages_combined = pd.concat([pd.read_csv(f) for f in file_path_messages], ignore_index=True)
df_messages_combined['masternode'] = df_messages_combined['masternode'].ffill()

# Calculate runtime intervals and average runtimes for each node
runtime_intervals = {}
average_runtimes = {}
for node, df_node in dfs_nodes.items():
    runtime_intervals[node] = calculate_intervals(df_node, 'active', 'unknown')
    average_runtimes[node] = calculate_average_time(runtime_intervals[node])

# Determine master and non-master runtimes
master_intervals = []
non_master_intervals = []
for node, intervals in runtime_intervals.items():
    master_int = determine_master_intervals(intervals, df_messages_combined, node, start_times[node])
    non_master_int = [i for i in intervals if i not in master_int]
    master_intervals.extend(master_int)
    non_master_intervals.extend(non_master_int)

avg_runtime_master = calculate_average_time(master_intervals)
avg_runtime_non_master = calculate_average_time(non_master_intervals)

# Plotting the average runtimes with annotations
fig, ax = plt.subplots(figsize=(10, 6))
categories = ['Master', 'Non-Master']
averages = [avg_runtime_master, avg_runtime_non_master]
bars = ax.bar(categories, averages, color=['#a48d9b', '#cdd0ea'])

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center')

ax.set_title('Average Recovery Time per Node Type for 3 runs')
ax.set_xlabel('Node Type')
ax.set_ylabel('Average Recovery Time (seconds) for 3 runs')
plt.show()
