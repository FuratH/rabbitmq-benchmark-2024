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

# Function to accurately calculate the recovery time
def calculate_correct_recovery_times(df):
    recovery_intervals = []
    in_downtime = False
    for i in range(1, len(df)):
        if df.iloc[i-1]['status'] == 'active' and df.iloc[i]['status'] == 'unknown':
            start = df.iloc[i]['timestamp']
            in_downtime = True
        elif in_downtime and df.iloc[i]['status'] == 'active':
            end = df.iloc[i]['timestamp']
            recovery_intervals.append((start, end))
            in_downtime = False
    return recovery_intervals

# Function to calculate the average recovery time from a list of intervals
def calculate_average_recovery_time(intervals):
    total_recovery_time = sum([(end - start).total_seconds() for start, end in intervals])
    return total_recovery_time / len(intervals) if intervals else 0

# Function to check if a node was a master during its downtime
def was_master_during_downtime(intervals, df_messages, node_name, start_time):
    master_downtimes = []
    for start, end in intervals:
        # Find the equivalent minutes since start for the interval
        start_minutes = (start - start_time).total_seconds() / 60
        end_minutes = (end - start_time).total_seconds() / 60
        
        # Check if the node was a master during this interval
        if any((df_messages['TimeElapsed (s)'] >= start_minutes * 60) & 
               (df_messages['TimeElapsed (s)'] <= end_minutes * 60) & 
               (df_messages['masternode'] == node_name)):
            master_downtimes.append((start, end))
    return master_downtimes

# File paths
file_path_node0 = 'run3/node0_5000_monitoring.log'
file_path_node1 = 'run3/node1_5000_monitoring.log'
file_path_node2 = 'run3/node2_5000_monitoring.log'
file_path_messages = 'run3/results.csv'

# Parse each log file and get start times
df_node0, start_time_node0 = parse_log(file_path_node0)
df_node1, start_time_node1 = parse_log(file_path_node1)
df_node2, start_time_node2 = parse_log(file_path_node2)

# Calculating correct recovery times for each node
correct_recovery_intervals_node0 = calculate_correct_recovery_times(df_node0)
correct_recovery_intervals_node1 = calculate_correct_recovery_times(df_node1)
correct_recovery_intervals_node2 = calculate_correct_recovery_times(df_node2)

# Reading CSV file for messages data
df_messages = pd.read_csv(file_path_messages)
df_messages['masternode'] = df_messages['masternode'].ffill()

# Calculate average recovery times for each node
avg_recovery_node0 = calculate_average_recovery_time(correct_recovery_intervals_node0)
avg_recovery_node1 = calculate_average_recovery_time(correct_recovery_intervals_node1)
avg_recovery_node2 = calculate_average_recovery_time(correct_recovery_intervals_node2)

# Calculate master downtimes for each node
master_downtime_node0 = was_master_during_downtime(correct_recovery_intervals_node0, df_messages, 'node0', start_time_node0)
master_downtime_node1 = was_master_during_downtime(correct_recovery_intervals_node1, df_messages, 'node1', start_time_node1)
master_downtime_node2 = was_master_during_downtime(correct_recovery_intervals_node2, df_messages, 'node2', start_time_node2)

# Calculate average recovery time for master and non-master intervals
master_intervals = master_downtime_node0 + master_downtime_node1 + master_downtime_node2
non_master_intervals = [
    interval for interval in correct_recovery_intervals_node0 + correct_recovery_intervals_node1 + correct_recovery_intervals_node2
    if interval not in master_intervals
]

avg_recovery_master = calculate_average_recovery_time(master_intervals)
avg_recovery_non_master = calculate_average_recovery_time(non_master_intervals)

# Plotting the average recovery times with annotations
fig, ax = plt.subplots(figsize=(10, 6))
nodes = ['Node0', 'Node1', 'Node2', 'Master', 'Non-Master']
averages = [avg_recovery_node0, avg_recovery_node1, avg_recovery_node2, avg_recovery_master, avg_recovery_non_master]
bars = ax.bar(nodes, averages, color=['#cae1ea', '#eae5ca', '#8da495', '#a48d9b', '#cdd0ea'])
#bars = ax.bar(nodes, averages, color=['red', 'blue', 'green', 'orange', 'purple'])
# Adding text annotations
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center')

ax.set_title('Average Recovery Time per Node')
ax.set_xlabel('Node Type')
ax.set_ylabel('Average Recovery Time (seconds)')
plt.show()
