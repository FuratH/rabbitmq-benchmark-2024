package benchmark;

import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Base64;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import benchmark.worker.ConnectionConfiguration;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class FailureInjector {

    private HttpClient client;
    private List<String> serverUrls;
    private final Random random = new Random();
    private ConnectionConfiguration connectionConfig;

    private static String master = "";

    private static final Logger log = LoggerFactory.getLogger(FailureInjector.class);

    public FailureInjector(ConnectionConfiguration connectionConfig) {
        this.client = HttpClient.newHttpClient();
        this.connectionConfig = connectionConfig;
    }

    public FailureInjector(List<String> serverUrls, ConnectionConfiguration connectionConfig) {
        this(connectionConfig);
        this.serverUrls = new LinkedList<>(serverUrls);
    }

    private String getAuthorizationHeader(String username, String password) {
        String auth = username + ":" + password;
        return "Basic " + Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
    }

    public String fetchMasternode(String queueUrl, String username, String password) {
        try {
            String authHeader = getAuthorizationHeader(username, password);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(queueUrl))
                    .header("Authorization", authHeader)
                    .GET()
                    .build();

            CompletableFuture<String> future = client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                    .thenApply(HttpResponse::body)
                    .thenApply(responseBody -> {
                        if (responseBody.isEmpty()) {

                            return master;
                        } else {
                            JSONObject jsonResponse = new JSONObject(responseBody);
                            String node = jsonResponse.optString("node", "");

                            if (node.startsWith("rabbit@")) {

                                String masternodevalue = node.substring("rabbit@".length());
                                master = masternodevalue;
                                return masternodevalue;
                            }
                            return master;

                        }
                    });

            return future.get(2000, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            return master;
        } catch (InterruptedException | ExecutionException e) {
            return master;
        }
    }

    public void startMonitoringAll() {
        log.info("Starting monitoring for all servers");
        for (String url : serverUrls) {
            try {
                performActionOnServer(url, "/start-monitoring");
            } catch (Exception e) {
                log.error("Failed to start monitoring for " + url);
            }
        }
    }

    public void stopMonitoringAll(String directory) {
        log.info("Stopping monitoring for all servers");
        for (String url : serverUrls) {
            try {
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(url + "/stop-monitoring"))
                        .GET()
                        .build();

                HttpResponse<InputStream> response = client.send(request, HttpResponse.BodyHandlers.ofInputStream());

                String fileName = url.replace("http://", "").replace("https://", "").replaceAll("[^a-zA-Z0-9]", "_")
                        + "_monitoring.log";

                Path filePath = Path.of(directory + "/" + fileName);
                Files.copy(response.body(), filePath, StandardCopyOption.REPLACE_EXISTING);
                log.info("Monitoring log saved for " + url + " at " + filePath);

            } catch (Exception e) {
                log.error("Failed to stop monitoring for " + url);
            }
        }
    }

    public boolean checkHealth(String url) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url + "/health"))
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.body().contains("RabbitMQ status: active");
        } catch (Exception e) {
            log.info("Health check failed for " + url);
            return false;
        }
    }

    private String performActionOnServer(String url, String action) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url + action))
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        log.info("Response from " + url + ": " + response.body());

        return url;
    }

    private void stopRandomRabbitMQ() throws Exception {
        int index = random.nextInt(serverUrls.size());
        String url = serverUrls.toArray(new String[0])[index];
        log.info("Stopping:");
        if (checkHealth(url)) {
            log.info("Stopping: " + url);
            performActionOnServer(url, "/kill-rabbitmq");
        } else {
            log.info("Skipping stop on " + url + " due to failed health check.");
        }
    }

    private String getMasternode() {
        String master = "";

        while (master.equals("")) {
            master = this.fetchMasternode(this.connectionConfig.apiUrl + "/api/queues/%2F/ha.queue", "rabbitmq",
                    "password");

            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        return master;
    }

    private void stopMasternode() throws Exception {
        List<String> allNodes = this.serverUrls;

        String master = getMasternode();

        String[] masternodesArray = allNodes.stream()
                .filter(node -> node.contains(master))
                .toArray(String[]::new);

        int index = random.nextInt(masternodesArray.length);
        String url = masternodesArray[index];
        if (checkHealth(url)) {
            log.info("Stopping: " + url);
            performActionOnServer(url, "/kill-rabbitmq");
        } else {
            log.info("Skipping stop on " + url + " due to failed health check.");
        }
    }

    private void stopSlavenode() throws Exception {
        List<String> allNodes = this.serverUrls;

        String master = getMasternode();

        String[] slavesArray = allNodes.stream()
                .filter(node -> !node.contains(master))
                .toArray(String[]::new);

        int index = random.nextInt(slavesArray.length);
        String url = slavesArray[index];

        if (checkHealth(url)) {
            log.info("Stopping: " + url);
            performActionOnServer(url, "/kill-rabbitmq");
        } else {
            log.info("Skipping stop on " + url + " due to failed health check.");
        }
    }

    private void startSpecificRabbitMQ(String url) throws Exception {
        log.info("Starting");
        if (url != null && !checkHealth(url)) {
            log.info("Starting: " + url);
            performActionOnServer(url, "/start-rabbitmq");
        }
    }

    public void stopAllRabbitMQ() throws Exception {
        log.info("Stop all");
        for (String url : serverUrls) {
            if (checkHealth(url)) {
                performActionOnServer(url, "/kill-rabbitmq");
            } else {
                log.info("Skipping " + "/kill-rabbitmq" + " on " + url + " due to failed health check.");
            }
        }
    }

    public void startAllRabbitMQ() throws Exception {
        log.info("Start all");
        for (int i = serverUrls.size() - 1; i >= 0; i--) {
            String url = serverUrls.get(i);
            if (!checkHealth(url)) {
                String startedUrl = performActionOnServer(url, "/start-rabbitmq");
                startSpecificRabbitMQ(startedUrl);
            } else {
                log.info("Skipping " + "/start-rabbitmq" + " on " + url + " because nodes already active.");
            }

        }
    }

    public void runAction(String action) {
        switch (action) {
            case "master":
                try {
                    stopMasternode();
                } catch (Exception e) {
                }
                break;
            case "slave":
                try {
                    stopSlavenode();
                } catch (Exception e) {
                }
                break;
            case "all":
                try {
                    stopAllRabbitMQ();
                } catch (Exception e) {
                }
                break;
            case "single":
                try {
                    stopRandomRabbitMQ();
                } catch (Exception e) {
                }
                break;
            default:
                break;
        }
    }

}
