from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re


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

def parse_messages_data(file_path, start_time, warmup_minutes=10):
    df = pd.read_csv(file_path)
    df['masternode'] = df['masternode'].ffill()
    df['Timestamp'] = df['TimeElapsed (s)'].apply(lambda x: x / 60)      
    df = df[~((df['MessageSentThroughput (KB/s)'] == 0) & (df['Timestamp'] < warmup_minutes))]
    return df




def was_master_during_downtime(intervals, df_messages, node_name, start_time):
    master_downtimes = []
    for start, end in intervals:
        start_minutes = (start - start_time).total_seconds() / 60
        end_minutes = (end - start_time).total_seconds() / 60

        if any((df_messages['Timestamp'] >= start_minutes) & (df_messages['Timestamp'] <= end_minutes) & (df_messages['masternode'] == node_name)):
            master_downtimes.append((start_minutes, end_minutes))
    return master_downtimes


file_path_node0 = 'run3/node0_5000_monitoring.log'
file_path_node1 = 'run3/node1_5000_monitoring.log'
file_path_node2 = 'run3/node2_5000_monitoring.log'
file_path_messages = 'run3/results.csv'


df_node0, start_time_node0 = parse_log(file_path_node0)
df_node1, start_time_node1 = parse_log(file_path_node1)
df_node2, start_time_node2 = parse_log(file_path_node2)


correct_recovery_intervals_node0 = calculate_correct_recovery_times(df_node0)
correct_recovery_intervals_node1 = calculate_correct_recovery_times(df_node1)
correct_recovery_intervals_node2 = calculate_correct_recovery_times(df_node2)


df_messages = parse_messages_data(file_path_messages, start_time_node0)

def plot_downtime_with_recovery_seconds(ax, intervals, y_position, label, color, start_time, z_order):
    for start, end in intervals:
        start_offset = (start - start_time).total_seconds() / 60
        end_offset = (end - start_time).total_seconds() / 60

        recovery_time_seconds = (end - start).total_seconds()
        recovery_str = f"{recovery_time_seconds:.2f} sec"
        line = ax.hlines(y_position, start_offset, end_offset, colors=color, lw=4, zorder=z_order)
        ax.text(start_offset, y_position + 0.01, f'{label}\n{recovery_str}', color=color, fontsize=10, verticalalignment='bottom', zorder=(z_order + 10))


def check_all_nodes_down_with_same_masternode(recovery_intervals_node0, recovery_intervals_node1, recovery_intervals_node2, df_messages):

    all_intervals = sorted(recovery_intervals_node0 + recovery_intervals_node1 + recovery_intervals_node2, key=lambda x: x[0])
    
    system_wide_downtimes = []
    for i in range(len(all_intervals)):
        start, end = all_intervals[i]
        overlaps_with_node1 = any(start <= end1 and end >= start1 for start1, end1 in recovery_intervals_node1)
        overlaps_with_node2 = any(start <= end2 and end >= start2 for start2, end2 in recovery_intervals_node2)
        
        if overlaps_with_node1 and overlaps_with_node2:
            before_downtime = df_messages[df_messages['Timestamp'] < (start - start_time_node0).total_seconds() / 60]['masternode'].iloc[-1]
            after_downtime = df_messages[df_messages['Timestamp'] > (end - start_time_node0).total_seconds() / 60]['masternode'].iloc[0]
            if before_downtime == after_downtime:
                system_wide_downtimes.append(((start - start_time_node0).total_seconds() / 60, (end - start_time_node0).total_seconds() / 60))
    
    return system_wide_downtimes

system_wide_down_with_same_masternode = check_all_nodes_down_with_same_masternode(
    correct_recovery_intervals_node0, correct_recovery_intervals_node1, correct_recovery_intervals_node2, df_messages)



def find_detailed_masternode_changes(df_messages):
    changes = []
    prev_node = df_messages.iloc[0]['masternode']
    for index, row in df_messages.iterrows():
        if row['masternode'] != prev_node:
            changes.append((row['Timestamp'], prev_node, row['masternode']))  
            prev_node = row['masternode']
    return changes

detailed_masternode_changes = find_detailed_masternode_changes(df_messages)

node_color_map = {
    'node0': 'red',
    'node1': 'blue',
    'node2': 'green'
}


detailed_masternode_changes = [
    (timestamp, prev_node, new_node) for timestamp, prev_node, new_node in detailed_masternode_changes
    if pd.notna(new_node) and new_node in node_color_map
]

fig, ax1 = plt.subplots(figsize=(15, 8))

ax2 = ax1.twinx()
ax2.plot(df_messages['Timestamp'], df_messages['EndToEndLatencyValueAtPercentile50 (ms)'], label='50th Percentile', color='#9CBEC4', alpha=0.5, zorder=1)
ax2.plot(df_messages['Timestamp'], df_messages['EndToEndLatencyValueAtPercentile75 (ms)'], label='75th Percentile', color='#F2C879', alpha=0.5, zorder=1)
ax2.plot(df_messages['Timestamp'], df_messages['EndToEndLatencyValueAtPercentile95 (ms)'], label='95th Percentile', color='#8A2A23', alpha=0.5, zorder=1)
ax2.plot(df_messages['Timestamp'], df_messages['EndToEndLatencyValueAtPercentile99 (ms)'], label='99th Percentile', color='#D9C5B4', alpha=0.5, zorder=1)


ax2.set_ylabel('Latency', color='black')


plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node0, 0.4, 'Node0', 'red', start_time_node0, 5)
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node1, 0.3, 'Node1', 'blue', start_time_node1, 5)
plot_downtime_with_recovery_seconds(ax1, correct_recovery_intervals_node2, 0.2, 'Node2', 'green', start_time_node2, 5)


for timestamp, prev_node, new_node in detailed_masternode_changes:
    ax1.axvline(x=timestamp, color=node_color_map[new_node], linestyle=':', linewidth=2, label=f'Masternode Change to {new_node.capitalize()}' if f'Masternode Change to {new_node.capitalize()}' not in ax1.get_legend_handles_labels()[1] else None, zorder=3)


for start, end in system_wide_down_with_same_masternode:
    masternode_during_downtime = df_messages[(df_messages['Timestamp'] >= start) & (df_messages['Timestamp'] <= end)]['masternode'].iloc[0]
    if pd.notna(masternode_during_downtime) and masternode_during_downtime in node_color_map:
        ax1.axvline(x=start, color=node_color_map[masternode_during_downtime], linestyle='--', linewidth=2, label=f'System-wide Downtime (Masternode: {masternode_during_downtime.capitalize()})' if f'System-wide Downtime (Masternode: {masternode_during_downtime.capitalize()})' not in ax1.get_legend_handles_labels()[1] else None, zorder=2)


ax1.set_ylim(0, 1)
ax1.set_yticks([])
ax1.set_title('RabbitMQ Nodes Downtime and EndToEnd Latency Over Time')
ax1.set_xlabel('Time (minutes since start)')
ax1.set_ylabel('Downtime', color='black')
ax1.xaxis.set_major_locator(plt.MultipleLocator(5))
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f} min'))
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True)


handles, labels = ax1.get_legend_handles_labels()
unique_labels = list(dict.fromkeys(labels))
unique_handles = [handles[labels.index(label)] for label in unique_labels]
ax1.legend(unique_handles, unique_labels, loc='upper left')


handles, labels = ax2.get_legend_handles_labels()
unique_labels = list(dict.fromkeys(labels))
unique_handles = [handles[labels.index(label)] for label in unique_labels]
ax2.legend(unique_handles, unique_labels, loc='upper right')


plt.tight_layout()
plt.show()
