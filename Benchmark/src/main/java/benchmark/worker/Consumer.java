package benchmark.worker;

import com.rabbitmq.client.*;

import benchmark.MetricsAggregator;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Consumer extends Worker {
    private static final Logger log = LoggerFactory.getLogger(Consumer.class);

    private final MetricsAggregator metricsAggregator;

    public Consumer(ConnectionConfiguration config, MetricsAggregator metricsAggregator, AtomicBoolean running) {
        super(config, running);
        this.connection = config.getOrCreateConnection();
        this.metricsAggregator = metricsAggregator;
    }

    @Override
    protected void attemptChannelInitialization() throws Exception {
        if (!this.running.get()) {
            return;
        }

        if (this.channel != null && this.channel.isOpen()) {
            return;
        }

        if (this.connection == null || !this.connection.isOpen()) {
            this.connection = this.config.getOrCreateConnection();
        }

        this.channel = connection.createChannel();
        channel.queueDeclare(config.queueName, true, false, false, null);
    }

    public void startConsuming() throws InterruptedException {
        retryOperationWithBackoff(this::attemptStartConsuming);
    }

    private void attemptStartConsuming() throws IOException {
        checkAndRecoverConnection();
        DeliverCallback deliverCallback = (consumerTag, delivery) -> {

            long now = System.currentTimeMillis();
            long publishTimestamp = delivery.getProperties().getTimestamp().getTime();
            long endToEndLatency = TimeUnit.MILLISECONDS.toMillis(now - publishTimestamp);

            this.metricsAggregator.recordMessageReceived(endToEndLatency);

        };
        CancelCallback cancelCallback = consumerTag -> log.warn("Consumer was cancelled");

        channel.basicConsume(config.queueName, true, deliverCallback, cancelCallback);
    }
}
