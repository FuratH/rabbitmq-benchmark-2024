import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Reading the CSV file
file_path = 'data18/results.csv'
df = pd.read_csv(file_path)

# Setting the aesthetic style of the plots
sns.set_style("whitegrid")

# Plotting Publish Latency Metrics Over Time
plt.figure(figsize=(14, 6))
plt.plot(df['TimeElapsed (s)'], df['PublishLatencyValueAtPercentile50 (ms)'], label='50th Percentile Publish Latency', color='blue')
plt.plot(df['TimeElapsed (s)'], df['PublishLatencyValueAtPercentile75 (ms)'], label='75th Percentile Publish Latency', color='green')
plt.plot(df['TimeElapsed (s)'], df['PublishLatencyValueAtPercentile95 (ms)'], label='95th Percentile Publish Latency', color='red')
plt.plot(df['TimeElapsed (s)'], df['PublishLatencyValueAtPercentile99 (ms)'], label='99th Percentile Publish Latency', color='purple')
plt.title('Publish Latency Metrics Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Latency (milliseconds)')
plt.legend()
plt.show()

# Plotting End-to-End Latency Metrics Over Time
plt.figure(figsize=(14, 6))
plt.plot(df['TimeElapsed (s)'], df['EndToEndLatencyValueAtPercentile50 (ms)'], label='50th Percentile End-to-End Latency', color='orange')
plt.plot(df['TimeElapsed (s)'], df['EndToEndLatencyValueAtPercentile75 (ms)'], label='75th Percentile End-to-End Latency', color='brown')
plt.plot(df['TimeElapsed (s)'], df['EndToEndLatencyValueAtPercentile95 (ms)'], label='95th Percentile End-to-End Latency', color='pink')
plt.plot(df['TimeElapsed (s)'], df['EndToEndLatencyValueAtPercentile99 (ms)'], label='99th Percentile End-to-End Latency', color='cyan')
plt.title('End-to-End Latency Metrics Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Latency (milliseconds)')
plt.legend()
plt.show()

# Box Plot for Publish and End-to-End Latency Metrics
plt.figure(figsize=(14, 6))
df[['PublishLatencyValueAtPercentile50 (ms)', 'PublishLatencyValueAtPercentile75 (ms)', 
    'PublishLatencyValueAtPercentile95 (ms)', 'PublishLatencyValueAtPercentile99 (ms)',
    'EndToEndLatencyValueAtPercentile50 (ms)', 'EndToEndLatencyValueAtPercentile75 (ms)',
    'EndToEndLatencyValueAtPercentile95 (ms)', 'EndToEndLatencyValueAtPercentile99 (ms)']].plot(kind='box')
plt.title('Box Plot of Publish and End-to-End Latency Metrics')
plt.ylabel('Latency (milliseconds)')
plt.show()

# Density Plot for Publish Latency Metrics
plt.figure(figsize=(14, 6))
sns.kdeplot(df['PublishLatencyValueAtPercentile50 (ms)'], label='50th Percentile', shade=True)
sns.kdeplot(df['PublishLatencyValueAtPercentile75 (ms)'], label='75th Percentile', shade=True)
sns.kdeplot(df['PublishLatencyValueAtPercentile95 (ms)'], label='95th Percentile', shade=True)
sns.kdeplot(df['PublishLatencyValueAtPercentile99 (ms)'], label='99th Percentile', shade=True)
plt.title('Density Plot of Publish Latency Metrics')
plt.xlabel('Latency (milliseconds)')
plt.ylabel('Density')
plt.legend()
plt.show()

# Density Plot for End-to-End Latency Metrics
plt.figure(figsize=(14, 6))
sns.kdeplot(df['EndToEndLatencyValueAtPercentile50 (ms)'], label='50th Percentile', shade=True)
sns.kdeplot(df['EndToEndLatencyValueAtPercentile75 (ms)'], label='75th Percentile', shade=True)
sns.kdeplot(df['EndToEndLatencyValueAtPercentile95 (ms)'], label='95th Percentile', shade=True)
sns.kdeplot(df['EndToEndLatencyValueAtPercentile99 (ms)'], label='99th Percentile', shade=True)
plt.title('Density Plot of End-to-End Latency Metrics')
plt.xlabel('Latency (milliseconds)')
plt.ylabel('Density')
plt.legend()
plt.show()

# ECDF Plot for Publish Latency Metrics
plt.figure(figsize=(14, 6))
sns.ecdfplot(df['PublishLatencyValueAtPercentile50 (ms)'], label='50th Percentile')
sns.ecdfplot(df['PublishLatencyValueAtPercentile75 (ms)'], label='75th Percentile')
sns.ecdfplot(df['PublishLatencyValueAtPercentile95 (ms)'], label='95th Percentile')
sns.ecdfplot(df['PublishLatencyValueAtPercentile99 (ms)'], label='99th Percentile')
plt.title('ECDF Plot of Publish Latency Metrics')
plt.xlabel('Latency (milliseconds)')
plt.ylabel('ECDF')
plt.legend()
plt.show()

# ECDF Plot for End-to-End Latency Metrics
plt.figure(figsize=(14, 6))
sns.ecdfplot(df['EndToEndLatencyValueAtPercentile50 (ms)'], label='50th Percentile')
sns.ecdfplot(df['EndToEndLatencyValueAtPercentile75 (ms)'], label='75th Percentile')
sns.ecdfplot(df['EndToEndLatencyValueAtPercentile95 (ms)'], label='95th Percentile')
sns.ecdfplot(df['EndToEndLatencyValueAtPercentile99 (ms)'], label='99th Percentile')
plt.title('ECDF Plot of End-to-End Latency Metrics')
plt.xlabel('Latency (milliseconds)')
plt.ylabel('ECDF')
plt.legend()
plt.show()
