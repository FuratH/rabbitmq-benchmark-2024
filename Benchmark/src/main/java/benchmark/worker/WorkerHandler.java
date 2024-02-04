package benchmark.worker;

import static java.util.stream.Collectors.toList;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.IntStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.util.concurrent.RateLimiter;
import com.rabbitmq.client.Connection;

import benchmark.MetricsAggregator;
import benchmark.worker.WorkerHandler;

public class WorkerHandler {

    private ConnectionConfiguration config;
    private final List<Producer> producers = new ArrayList<>();
    private final List<Consumer> consumers = new ArrayList<>();

    private final AtomicBoolean running = new AtomicBoolean(true);

    private final MetricsAggregator metricsAggregator;

    private volatile MessageProducer messageProducer = new MessageProducer();

    private final ExecutorService executor = Executors.newCachedThreadPool(Executors.defaultThreadFactory());

    private static final Logger log = LoggerFactory.getLogger(WorkerHandler.class);

    public WorkerHandler(ConnectionConfiguration config, MetricsAggregator metricsAggregator) {
        this.config = config;
        this.metricsAggregator = metricsAggregator;
    }

    public CompletableFuture<Producer> createProducer() {
        CompletableFuture<Producer> future = new CompletableFuture<>();

        ForkJoinPool.commonPool()
                .execute(
                        () -> {
                            try {
                                future.complete(new Producer(config, metricsAggregator, running));
                            } catch (Exception e) {
                                e.printStackTrace();
                                future.completeExceptionally(e);
                            }
                        });
        return future;
    }

    public CompletableFuture<Consumer> createConsumer() {
        CompletableFuture<Consumer> future = new CompletableFuture<>();

        ForkJoinPool.commonPool()
                .execute(
                        () -> {
                            try {
                                future.complete(new Consumer(config, metricsAggregator, running));
                            } catch (Exception e) {
                                future.completeExceptionally(e);
                            }
                        });
        return future;
    }

    public void createProducers(int amount) {
        List<CompletableFuture<Producer>> futures = IntStream.range(0, amount)
                .mapToObj(i -> createProducer())
                .collect(toList());

        CompletableFuture<Void> allOf = CompletableFuture.allOf(
                futures.toArray(new CompletableFuture[0]));

        allOf.thenRun(() -> {
            this.producers.addAll(
                    futures.stream()
                            .map(CompletableFuture::join)
                            .collect(toList())

            );
            log.info("All {} producers created successfully.", amount);
        }).exceptionally(throwable -> {
            log.error("Failed to create producers", throwable);
            return null;
        }).join();
    }

    public void createConsumers(int amount) {
        List<CompletableFuture<Consumer>> futures = IntStream.range(0, amount)
                .mapToObj(i -> createConsumer())
                .collect(toList());

        CompletableFuture<Void> allOf = CompletableFuture.allOf(
                futures.toArray(new CompletableFuture[0]));

        allOf.thenRun(() -> {
            this.consumers.addAll(
                    futures.stream()
                            .map(CompletableFuture::join)
                            .collect(toList()));
            log.info("All Consumers created successfully.");
        }).exceptionally(throwable -> {
            log.error("Failed to create Consumers", throwable);
            return null;
        }).join();
    }

    public void startLoad(ProducerWorkAssignment producerWorkAssignment) {
        producers.forEach(producer -> CompletableFuture.runAsync(() -> {
            try {
                runProducerLoad(producer, producerWorkAssignment);
            } catch (InterruptedException e) {
            } catch (Exception e) {
                log.error("Producer encountered an error", e);
            }
        }, executor));

        consumers.forEach(producer -> CompletableFuture.runAsync(() -> {
            try {
                producer.startConsuming();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } catch (Exception e) {
                log.error("Producer encountered an error", e);
            }
        }, executor));

    }

    private void runProducerLoad(Producer producer, ProducerWorkAssignment assignment) throws InterruptedException {
        while (running.get()) {
            for (byte[] payload : assignment.payloadData) {
                if (!running.get()) {
                    System.out.println("stopp");
                    break;
                }
                producer.sendAsync(payload);

                // messageProducer.sendMessage(producer, payload);
            }
        }
    }

    public void stopAll() {
        log.info("stoppAll");
        running.set(false);
        producers.forEach(
                worker -> CompletableFuture.runAsync(() -> {
                    try {
                        worker.stopWorker();
                    } catch (Exception e) {
                    }
                }, executor));

        consumers.forEach(
                worker -> CompletableFuture.runAsync(() -> {
                    try {
                        worker.stopWorker();
                    } catch (Exception e) {

                        e.printStackTrace();
                    }
                }, executor));
    }

}
