import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import re

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

# Modified function to plot downtime intervals with recovery times in seconds
def plot_downtime_with_recovery_seconds(ax, intervals, y_position, label, color):
    for start, end in intervals:
        recovery_time_seconds = (end - start).total_seconds()
        recovery_str = f"{recovery_time_seconds:.2f} sec"
        line = ax.hlines(y_position, start, end, colors=color, lw=4)
        ax.text(start, y_position, f'{label}\n{recovery_str}', color=color, fontsize=8, verticalalignment='bottom', zorder=5)
        line.set_zorder(1)

# Function to parse the new CSV file format for latency data
def parse_latency_data(file_path):
    # Reading CSV file
    df = pd.read_csv(file_path)

    # Converting 'TimeElapsed (s)' to a datetime format
    start_time = df_masternode['timestamp'].iloc[0]  # Assuming df_masternode is defined
    df['Timestamp'] = df['TimeElapsed (s)'].apply(lambda x: start_time + timedelta(seconds=x))

    # Selecting relevant latency columns
    df = df[['Timestamp', 
             'PublishLatencyValueAtPercentile50 (ms)', 
             'PublishLatencyValueAtPercentile75 (ms)', 
             'PublishLatencyValueAtPercentile95 (ms)', 
             'PublishLatencyValueAtPercentile99 (ms)', 
             'EndToEndLatencyValueAtPercentile50 (ms)', 
             'EndToEndLatencyValueAtPercentile75 (ms)', 
             'EndToEndLatencyValueAtPercentile95 (ms)', 
             'EndToEndLatencyValueAtPercentile99 (ms)']]
    return df

# File paths
file_path_masternode = 'data6/masternode_5000_monitoring.log'
file_path_slavenode0 = 'data6/slavenode0_5000_monitoring.log'
file_path_slavenode1 = 'data6/slavenode1_5000_monitoring.log'
file_path_latency = 'data6/results.csv'  # File path for latency data

# Parse each log file
df_masternode = parse_log(file_path_masternode)
df_slavenode0 = parse_log(file_path_slavenode0)
df_slavenode1 = parse_log(file_path_slavenode1)

# Calculating correct recovery times for each node
correct_recovery_intervals_masternode = calculate_correct_recovery_times(df_masternode)
correct_recovery_intervals_slavenode0 = calculate_correct_recovery_times(df_slavenode0)
correct_recovery_intervals_slavenode1 = calculate_correct_recovery_times(df_slavenode1)

# Parse latency data
df_latency = parse_latency_data(file_path_latency)

# Creating the plot for latency metrics with node activity
fig, ax1 = plt.subplots(figsize=(15, 8))

# Plotting downtime intervals for each node
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_masternode, 0.5, 'Master Node', 'red')
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_slavenode0, 0.3, 'Slave Node 0', 'blue')
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_slavenode1, 0.1, 'Slave Node 1', 'green')

# Plotting Publish Latency Metrics
ax1.plot(df_latency['Timestamp'], df_latency['PublishLatencyValueAtPercentile50 (ms)'], label='50th Percentile Publish Latency', color='orange')
ax1.plot(df_latency['Timestamp'], df_latency['PublishLatencyValueAtPercentile75 (ms)'], label='75th Percentile Publish Latency', color='brown')
ax1.plot(df_latency['Timestamp'], df_latency['PublishLatencyValueAtPercentile95 (ms)'], label='95th Percentile Publish Latency', color='pink')
ax1.plot(df_latency['Timestamp'], df_latency['PublishLatencyValueAtPercentile99 (ms)'], label='99th Percentile Publish Latency', color='cyan')

# Plotting End-to-End Latency Metrics
ax1.plot(df_latency['Timestamp'], df_latency['EndToEndLatencyValueAtPercentile50 (ms)'], label='50th Percentile End-to-End Latency', linestyle='dashed')
ax1.plot(df_latency['Timestamp'], df_latency['EndToEndLatencyValueAtPercentile75 (ms)'], label='75th Percentile End-to-End Latency', linestyle='dashed')
ax1.plot(df_latency['Timestamp'], df_latency['EndToEndLatencyValueAtPercentile95 (ms)'], label='95th Percentile End-to-End Latency', linestyle='dashed')
ax1.plot(df_latency['Timestamp'], df_latency['EndToEndLatencyValueAtPercentile99 (ms)'], label='99th Percentile End-to-End Latency', linestyle='dashed')

# Formatting the plot
ax1.set_title('RabbitMQ Nodes Downtime, Publish and End-to-End Latency Over Time')
ax1.set_xlabel('Time')
ax1.set_ylabel('Latency (milliseconds)', color='black')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')
ax1.grid(True)

# Show the combined plot
plt.tight_layout()
plt.show()
