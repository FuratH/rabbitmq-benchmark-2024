package benchmark;

import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.yaml.snakeyaml.Yaml;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import benchmark.TaskScheduler.ScheduledTask;
import benchmark.Workload.Workload;
import benchmark.worker.ConnectionConfiguration;

public class ConfigurationManager {

    private static final Logger log = LoggerFactory.getLogger(ConfigurationManager.class);
    private final Config config;

    public ConfigurationManager(Path configFilePath) {
        try (InputStream inputStream = Files.newInputStream(configFilePath)) {
            Yaml yaml = new Yaml();
            this.config = yaml.loadAs(inputStream, Config.class);
        } catch (Exception e) {
            log.error("Error loading configuration: {}", e.getMessage());
            throw new RuntimeException("Failed to load configuration", e);
        }
    }

    public List<String> getServerUrls() {
        return config.getServerUrls();
    }

    public Workload getWorkloadConfiguration() {
        return config.getWorkload();
    }

    public ConnectionConfiguration getConnectionConfiguration() {
        return config.getConnectionConfig();
    }

    public List<ScheduledTask> getTasks() {
        return config.getTasks();
    }


    public static class Config {
        private List<String> serverUrls;
        private Workload workload;
        private ConnectionConfiguration connectionConfig;
        private List<ScheduledTask> tasks;


        public void setServerUrls(List<String> serverUrls) {
            this.serverUrls = serverUrls;
        }

        public void setWorkload(Workload workload) {
            this.workload = workload;
        }

        public void setConnectionConfig(ConnectionConfiguration connectionConfig) {
            this.connectionConfig = connectionConfig;
        }

        public void setTasks(List<ScheduledTask> tasks) {
            this.tasks = tasks;
        }


        public List<String> getServerUrls() {
            return serverUrls;
        }

        public Workload getWorkload() {
            return workload;
        }

        public ConnectionConfiguration getConnectionConfig() {
            return connectionConfig;
        }

        public List<ScheduledTask> getTasks() {
        return tasks;
    }
    }
}
