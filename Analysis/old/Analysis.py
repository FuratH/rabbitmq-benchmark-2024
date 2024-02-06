import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Reading the log file
file_path = 'results.txt'
with open(file_path, 'r') as file:
    log_content = file.read()

# Regular expression pattern for data extraction
pattern = r"time: (\d+)s; Messages sent: (\d+); Messages received: (\d+); min/median/75th/95th/99th consumer latency: (\d+)/(\d+)/(\d+)/(\d+)/(\d+) ns"

# Extracting data from the log content
data = {
    'time_sec': [],
    'messages_sent': [],
    'messages_received': [],
    'min_latency_ns': [],
    'median_latency_ns': [],
    '75th_latency_ns': [],
    '95th_latency_ns': [],
    '99th_latency_ns': []
}

for match in re.finditer(pattern, log_content):
    data['time_sec'].append(int(match.group(1)))
    data['messages_sent'].append(int(match.group(2)))
    data['messages_received'].append(int(match.group(3)))
    data['min_latency_ns'].append(int(match.group(4)))
    data['median_latency_ns'].append(int(match.group(5)))
    data['75th_latency_ns'].append(int(match.group(6)))
    data['95th_latency_ns'].append(int(match.group(7)))
    data['99th_latency_ns'].append(int(match.group(8)))

# Converting data into a DataFrame
log_df = pd.DataFrame(data)

# Calculating total messages sent and received
total_messages_sent = log_df['messages_sent'].sum()
total_messages_received = log_df['messages_received'].sum()

# Setting the aesthetic style of the plots
sns.set_style("whitegrid")

# Plotting messages sent and received over time
plt.figure(figsize=(14, 6))
plt.plot(log_df['time_sec'], log_df['messages_sent'], label='Messages Sent', color='blue')
plt.plot(log_df['time_sec'], log_df['messages_received'], label='Messages Received', color='green')
plt.title('Messages Sent and Received Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Number of Messages')
plt.legend()
plt.show()

# Plotting consumer latency metrics
plt.figure(figsize=(14, 6))
plt.plot(log_df['time_sec'], log_df['min_latency_ns'], label='Min Latency', color='red')
plt.plot(log_df['time_sec'], log_df['median_latency_ns'], label='Median Latency', color='orange')
plt.plot(log_df['time_sec'], log_df['75th_latency_ns'], label='75th Percentile Latency', color='purple')
plt.plot(log_df['time_sec'], log_df['95th_latency_ns'], label='95th Percentile Latency', color='brown')
plt.plot(log_df['time_sec'], log_df['99th_latency_ns'], label='99th Percentile Latency', color='pink')
plt.title('Consumer Latency Metrics Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Latency (nanoseconds)')
plt.legend()
plt.show()

# Histograms for Messages Sent and Received
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
plt.hist(log_df['messages_sent'], bins=30, color='blue', alpha=0.7)
plt.title('Histogram of Messages Sent')
plt.xlabel('Messages Sent')
plt.ylabel('Frequency')
plt.subplot(1, 2, 2)
plt.hist(log_df['messages_received'], bins=30, color='green', alpha=0.7)
plt.title('Histogram of Messages Received')
plt.xlabel('Messages Received')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

# Box Plot for Latency Metrics
plt.figure(figsize=(14, 6))
log_df[['min_latency_ns', 'median_latency_ns', '75th_latency_ns', '95th_latency_ns', '99th_latency_ns']].plot(kind='box')
plt.title('Box Plot of Consumer Latency Metrics')
plt.ylabel('Latency (nanoseconds)')
plt.show()
