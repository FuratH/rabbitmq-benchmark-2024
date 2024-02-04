package benchmark;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.HdrHistogram.Histogram;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.rabbitmq.client.impl.WorkPool;

import benchmark.Workload.Workload;
import benchmark.Workload.WorkloadGenerator;
import benchmark.worker.ConnectionConfiguration;
import benchmark.worker.ProducerWorkAssignment;
import benchmark.worker.WorkerHandler;

public class BenchmarkDriver {
    private Workload workload;
    public MetricsAggregator metricsAggregator;
    private WorkerHandler worker;
    private WorkloadGenerator workloadGenerator;
    private ScheduledExecutorService metricsScheduler;
    private ConnectionConfiguration connectionConfig;

    private static final Logger log = LoggerFactory.getLogger(BenchmarkDriver.class);

    public BenchmarkDriver(Workload workload, WorkerHandler worker, WorkloadGenerator workloadGenerator,
            MetricsAggregator metricsAggregator, ConnectionConfiguration connectionConfig) {
        this.workload = workload;
        this.metricsAggregator = metricsAggregator;
        this.metricsScheduler = Executors.newScheduledThreadPool(1);
        this.workloadGenerator = workloadGenerator;
        this.worker = worker;
        this.connectionConfig = connectionConfig;

    }

    public void startBenchmark() {
        // Collect metrics every second and add them to results list in class Results
        metricsScheduler.scheduleAtFixedRate(() -> {
            // Store metrics
            long timeElapsed = metricsAggregator.getTime();
            long messageSentCount = metricsAggregator.getMessageSendCount();
            long messageReceivedCount = metricsAggregator.getMessageReceivedCount();

            long messageSentThroughput = metricsAggregator.getThroughput();

            Histogram publishLatency = metricsAggregator.producerLatency;
            Histogram endToEndLatency = metricsAggregator.endToEndLatency;

            FailureInjector failureInjector = new FailureInjector(connectionConfig);
            // Get current masternode
            String masternode = failureInjector
                    .fetchMasternode(
                            this.connectionConfig.apiUrl + "/api/queues/%2F/" + this.connectionConfig.queueName,
                            "rabbitmq",
                            "password");

            log.info(
                    "time: {} s; Message sent {}; Throughput {} KB/s; Messages received {}; Publish Latency min/median/75th/95th/99th - {}/{}/{}/{}/{} ms; End-to-End Latency min/median/75th/95th/99th - {}/{}/{}/{}/{} ms; masternode: {}",
                    timeElapsed,
                    messageSentCount,
                    messageSentThroughput,
                    messageReceivedCount,
                    publishLatency.getMinValue(),
                    publishLatency.getValueAtPercentile(50.0),
                    publishLatency.getValueAtPercentile(75.0),
                    publishLatency.getValueAtPercentile(95.0),
                    publishLatency.getValueAtPercentile(99.0),
                    endToEndLatency.getMinValue(),
                    endToEndLatency.getValueAtPercentile(50.0),
                    endToEndLatency.getValueAtPercentile(75.0),
                    endToEndLatency.getValueAtPercentile(95.0),
                    endToEndLatency.getValueAtPercentile(99.0),
                    masternode);

            new Results(timeElapsed,
                    messageSentCount,
                    messageSentThroughput,
                    messageReceivedCount,
                    publishLatency.getMinValue(),
                    publishLatency.getValueAtPercentile(50.0),
                    publishLatency.getValueAtPercentile(75.0),
                    publishLatency.getValueAtPercentile(95.0),
                    publishLatency.getValueAtPercentile(99.0),
                    endToEndLatency.getMinValue(),
                    endToEndLatency.getValueAtPercentile(50.0),
                    endToEndLatency.getValueAtPercentile(75.0),
                    endToEndLatency.getValueAtPercentile(95.0),
                    endToEndLatency.getValueAtPercentile(99.0),
                    masternode);

            metricsAggregator.reset();

        }, 0, 1, TimeUnit.SECONDS);

        // Start worker
        try {
            this.startWorker();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    public void startWorker() throws Exception {
        int runtime = this.workload.runtimeDurtationMinutes;

        log.info("Runtime duration: {} minutes", runtime);

        long producerCreationDuration = System.currentTimeMillis();
        worker.createProducers(workload.producers);
        log.info("Created {} producers in {} ms", workload.producers, producerCreationDuration);

        long ConsumerCreationDuration = System.currentTimeMillis();
        worker.createConsumers(workload.consumers);
        log.info("Created {} consumers in {} ms", workload.consumers, ConsumerCreationDuration);

        ProducerWorkAssignment producerWorkAssignment = new ProducerWorkAssignment();

        this.workloadGenerator.generateWorkload(producerWorkAssignment);

        log.info("Load starting");

        worker.startLoad(producerWorkAssignment);

    }

    public void stop() {
        metricsScheduler.shutdownNow();
        try {
            if (!metricsScheduler.awaitTermination(60, TimeUnit.SECONDS)) {
                metricsScheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            metricsScheduler.shutdownNow();
        }
    }

}
