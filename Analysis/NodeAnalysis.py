import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Function to parse a log file and extract intervals
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
    return df

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

# Function to plot downtime intervals with recovery times
def plot_downtime_with_recovery_seconds(ax, intervals, y_position, label, color):
    for start, end in intervals:
        recovery_time_seconds = (end - start).total_seconds()
        recovery_str = f"{recovery_time_seconds:.2f} sec"
        ax.hlines(y_position, start, end, colors=color, lw=4)
        ax.text(start, y_position, f'{label}\n{recovery_str}', color=color, fontsize=8, verticalalignment='bottom')

# Function to calculate average recovery times
def calculate_average_recovery_time(intervals):
    total_time = sum([(end - start).total_seconds() for start, end in intervals])
    average_time = total_time / len(intervals) if intervals else 0
    return average_time

# File paths
file_path_masternode = 'data3/masternode_5000_monitoring.log'
file_path_slavenode0 = 'data3/slavenode0_5000_monitoring.log'
file_path_slavenode1 = 'data3/slavenode1_5000_monitoring.log'


# Parse each log file
df_masternode = parse_log(file_path_masternode)
df_slavenode0 = parse_log(file_path_slavenode0)
df_slavenode1 = parse_log(file_path_slavenode1)

# Calculating correct recovery times for each node
correct_recovery_intervals_masternode = calculate_correct_recovery_times(df_masternode)
correct_recovery_intervals_slavenode0 = calculate_correct_recovery_times(df_slavenode0)
correct_recovery_intervals_slavenode1 = calculate_correct_recovery_times(df_slavenode1)

# Calculating average recovery time for each node
avg_recovery_time_masternode = calculate_average_recovery_time(correct_recovery_intervals_masternode)
avg_recovery_time_slavenode0 = calculate_average_recovery_time(correct_recovery_intervals_slavenode0)
avg_recovery_time_slavenode1 = calculate_average_recovery_time(correct_recovery_intervals_slavenode1)

# Calculating overall average recovery time
all_intervals = correct_recovery_intervals_masternode + correct_recovery_intervals_slavenode0 + correct_recovery_intervals_slavenode1
avg_recovery_time_overall = calculate_average_recovery_time(all_intervals)

# Creating the plot for the downtime intervals
fig1, ax1 = plt.subplots(figsize=(15, 6))

# Plotting downtime intervals with correct recovery times in seconds for each node
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_masternode, 0.5, 'Master Node', 'red')
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_slavenode0, 0.3, 'Slave Node 0', 'blue')
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_slavenode1, 0.1, 'Slave Node 1', 'green')

# Formatting the downtime intervals plot
ax1.set_ylim(0, 1)
ax1.set_yticks([])
ax1.set_title('RabbitMQ Nodes Downtime Timeline with Corrected Recovery Times (Seconds)')
ax1.set_xlabel('Time')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True)

# Showing the downtime intervals plot
plt.tight_layout()
plt.show()

# Data for the bar chart
nodes = ['Master Node', 'Slave Node 0', 'Slave Node 1', 'Overall']
average_times = [avg_recovery_time_masternode, avg_recovery_time_slavenode0, avg_recovery_time_slavenode1, avg_recovery_time_overall]

# Creating the bar chart for average recovery times
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Plotting the bar chart
ax2.bar(nodes, average_times, color=['red', 'blue', 'green', 'purple'])
ax2.set_title('Average Recovery Times for Each Node')
ax2.set_ylabel('Average Recovery Time (Seconds)')
ax2.grid(True)

# Showing the bar chart
plt.tight_layout()
plt.show()
