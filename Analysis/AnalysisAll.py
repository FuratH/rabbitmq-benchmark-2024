import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

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

# Function to plot downtime intervals with recovery times in seconds
def plot_downtime_with_recovery_seconds(ax, intervals, y_position, label, color, start_time, z_order):
    for start, end in intervals:
        start_offset = (start - start_time).total_seconds() / 60
        end_offset = (end - start_time).total_seconds() / 60
        recovery_time_seconds = (end - start).total_seconds()
        recovery_str = f"{recovery_time_seconds:.2f} sec"
        ax.hlines(y_position, start_offset, end_offset, colors=color, lw=4, zorder=z_order)
        ax.text(start_offset, y_position + 0.05, f'{label}\n{recovery_str}', color=color, fontsize=10, verticalalignment='bottom', zorder=z_order + 1)

# Modified function to parse the new CSV file format for messages data
def parse_messages_data(file_path, start_time):
    df = pd.read_csv(file_path)
    df['Timestamp'] = df['TimeElapsed (s)'].apply(lambda x: x / 60)  # Convert to minutes
    df = df[['Timestamp', 'MessageSentCount', 'MessageReceivedCount', 'masternode']]
    return df

# Function to check if a node was a master during its downtime
def was_master_during_downtime(intervals, df_messages, node_name, start_time):
    master_downtimes = []
    for start, end in intervals:
        start_minutes = (start - start_time).total_seconds() / 60
        end_minutes = (end - start_time).total_seconds() / 60

        if any((df_messages['Timestamp'] >= start_minutes) & (df_messages['Timestamp'] <= end_minutes) & (df_messages['masternode'] == node_name)):
            master_downtimes.append((start_minutes, end_minutes))
    return master_downtimes

# File paths
file_path_node0 = 'run1/node0_5000_monitoring.log'
file_path_node1 = 'run1/node1_5000_monitoring.log'
file_path_node2 = 'run1/node2_5000_monitoring.log'
file_path_messages = 'run1/results.csv'

# Parse each log file and get start times
df_node0, start_time_node0 = parse_log(file_path_node0)
df_node1, start_time_node1 = parse_log(file_path_node1)
df_node2, start_time_node2 = parse_log(file_path_node2)

# Calculating correct recovery times for each node
correct_recovery_intervals_node0 = calculate_correct_recovery_times(df_node0)
correct_recovery_intervals_node1 = calculate_correct_recovery_times(df_node1)
correct_recovery_intervals_node2 = calculate_correct_recovery_times(df_node2)

# Reading CSV file for messages data
df_messages = parse_messages_data(file_path_messages, start_time_node0)

# Creating the combined plot
fig, ax1 = plt.subplots(figsize=(15, 8))

# Plotting messages sent and received
ax2 = ax1.twinx()
ax2.plot(df_messages['Timestamp'], df_messages['MessageSentCount'], label='Messages Sent', color='#caeace', alpha=1, zorder=2)
ax2.plot(df_messages['Timestamp'], df_messages['MessageReceivedCount'], label='Messages Received', color='#9290a4', alpha=1, zorder=2)
ax2.set_ylabel('Message Count', color='black')

# Plotting downtime intervals with correct recovery times in seconds for each node
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node0, 0.7, 'Node0', '#637173', start_time_node0, 5)
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node1, 0.5, 'Node1', '#637173', start_time_node1, 5)
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node2, 0.1, 'Node2', '#637173', start_time_node2, 5)

# Calculate and highlight master downtimes
master_downtime_node0 = was_master_during_downtime(correct_recovery_intervals_node0, df_messages, 'node0', start_time_node0)
master_downtime_node1 = was_master_during_downtime(correct_recovery_intervals_node1, df_messages, 'node1', start_time_node1)
master_downtime_node2 = was_master_during_downtime(correct_recovery_intervals_node2, df_messages, 'node2', start_time_node2)

# Highlighting master node downtimes
for start, end in master_downtime_node0:
    ax1.axvspan(start, end, alpha=0.5, color='#eae5ca', label='Node0 Master Down' if 'Node0 Master Down' not in ax1.get_legend_handles_labels()[1] else None, zorder=3)
for start, end in master_downtime_node1:
    ax1.axvspan(start, end, alpha=0.5, color='#caeace', label='Node1 Master Down' if 'Node1 Master Down' not in ax1.get_legend_handles_labels()[1] else None, zorder=3)
for start, end in master_downtime_node2:
    ax1.axvspan(start, end, alpha=0.5, color='#cdd0ea', label='Node2 Master Down' if 'Node2 Master Down' not in ax1.get_legend_handles_labels()[1] else None, zorder=3)

# Formatting the plot
ax1.set_ylim(0, 1)
ax1.set_yticks([])
ax1.set_title('RabbitMQ Nodes Downtime and Message Activity Over Time')
ax1.set_xlabel('Time (minutes since start)')
ax1.set_ylabel('Downtime', color='black')
ax1.xaxis.set_major_locator(plt.MultipleLocator(5))
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f} min'))
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True)

# Adjusting legends to incorporate both axes
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

plt.tight_layout()
plt.show()
