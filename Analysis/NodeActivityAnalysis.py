import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Function to load and parse the log file
def load_and_parse_log(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        timestamp, status = line.strip().split(' - RabbitMQ status: ')
        data.append([timestamp, status])
    df = pd.DataFrame(data, columns=['timestamp', 'status'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Function to plot the activity timeline for a node
def plot_activity_timeline(df, node_name):
    df['status_val'] = df['status'].map({'active': 1, 'unknown': 0})
    plt.figure(figsize=(12, 2))
    plt.plot(df['timestamp'], df['status_val'], drawstyle='steps-post', label=node_name)
    plt.fill_between(df['timestamp'], df['status_val'], step='post', alpha=0.3)
    plt.ylim(-0.2, 1.2)
    plt.yticks([0, 1], ['Down', 'Active'])
    plt.title(f'Activity Timeline of {node_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Status')
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

# Function to calculate average recovery time for a node
def calculate_recovery_times(df):
    df['prev_status'] = df['status'].shift(1)
    recovery_rows = df[(df['status'] == 'active') & (df['prev_status'] == 'unknown')]
    recovery_rows['recovery_time'] = recovery_rows['timestamp'].diff().dt.total_seconds()
    valid_recovery_times = recovery_rows['recovery_time'].iloc[1:]
    return valid_recovery_times.mean()

# File paths (update these with your actual file paths)

file_masternode = 'data3/masternode_5000_monitoring.log'
file_slavenode0 = 'data3/slavenode0_5000_monitoring.log'
file_slavenode1 = 'data3/slavenode1_5000_monitoring.log'
file_messages = 'data3/results.txt'
# Loading and parsing each log file
df_masternode = load_and_parse_log(file_masternode)
df_slavenode0 = load_and_parse_log(file_slavenode0)
df_slavenode1 = load_and_parse_log(file_slavenode1)

# Plotting the activity timeline for each node
plot_activity_timeline(df_masternode, "Master Node")
plot_activity_timeline(df_slavenode0, "Slave Node 0")
plot_activity_timeline(df_slavenode1, "Slave Node 1")

plt.tight_layout()
plt.show()

# Calculating the average recovery time for each node
avg_recovery_time_masternode = calculate_recovery_times(df_masternode)
avg_recovery_time_slavenode0 = calculate_recovery_times(df_slavenode0)
avg_recovery_time_slavenode1 = calculate_recovery_times(df_slavenode1)

print("Average Recovery Time (in seconds):")
print(f"Master Node: {avg_recovery_time_masternode}")
print(f"Slave Node 0: {avg_recovery_time_slavenode0}")
print(f"Slave Node 1: {avg_recovery_time_slavenode1}")
