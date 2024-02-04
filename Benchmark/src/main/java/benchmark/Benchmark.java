package benchmark;

import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zeroturnaround.zip.ZipUtil;

import benchmark.TaskScheduler.ActionScheduler;
import benchmark.Workload.Workload;
import benchmark.Workload.WorkloadGenerator;
import benchmark.worker.ConnectionConfiguration;
import benchmark.worker.WorkerHandler;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.Executors;

public class Benchmark {

    private static final Logger log = LoggerFactory.getLogger(Benchmark.class);

    private static ScheduledExecutorService runtimeScheduler = Executors.newScheduledThreadPool(1);

    public static void main(String[] args) {

        if (args.length < 1) {
            System.out.println("Please provide the path to the YAML config file.");
            return;
        }

        String yamlFilePath = args[0];

        log.info("Starting benchmark");

        // Create directory to store config.yaml and results
        String directory = "run_" + System.currentTimeMillis();
        try {
            Files.createDirectories(Paths.get(directory));
            Path from = Paths.get(yamlFilePath);
            Path to = Paths.get(directory + "/config.yaml");
            Files.copy(from, to); // Copy config.yaml

        } catch (IOException e) {
            e.printStackTrace();
        }

        MetricsAggregator metricsAggregator = new MetricsAggregator();

        // config.yaml is loaded as a configManager object
        ConfigurationManager configManager = new ConfigurationManager(Paths.get(yamlFilePath));
        ConnectionConfiguration connectionConfig = configManager.getConnectionConfiguration();

        FailureInjector failureInjector = new FailureInjector(configManager.getServerUrls(), connectionConfig);
        ActionScheduler actionScheduler = new ActionScheduler(configManager.getTasks(), failureInjector);

        Workload workload = configManager.getWorkloadConfiguration();
        WorkloadGenerator workloadGenerator = new WorkloadGenerator(workload);

        WorkerHandler workerHandler = new WorkerHandler(connectionConfig, metricsAggregator);
        BenchmarkDriver workerDriver = new BenchmarkDriver(workload, workerHandler, workloadGenerator,
                metricsAggregator, connectionConfig);

        // Start benchmark
        workerDriver.startBenchmark(); // Start workload
        failureInjector.startMonitoringAll(); // Start monitoring on each node
        actionScheduler.startSchedule(); // Start failure injector

        // End benchmark after runtimeduration ended
        runtimeScheduler.schedule(() -> {
            log.info("Run completed, stopping workload.");
            workerHandler.stopAll();
            workerDriver.stop();

            // Stop monitoring and fetch node logs and store them in the result directory
            failureInjector.stopMonitoringAll(directory);

            // Create csv file for results
            Results.writeToCSV(directory + "/results.csv");
            String filename = directory + ".zip";
            ZipUtil.pack(new File(directory), new File(filename));

            // Upload results.zip to google bucket
            try {
                FileUpload.uploadFile(filename, filename, connectionConfig.projectId, connectionConfig.bucketName);
            } catch (IOException e) {
                e.printStackTrace();
            }

            System.exit(0);
        }, workload.runtimeDurtationMinutes, TimeUnit.MINUTES);
    }
}
