package benchmark.worker;

import com.rabbitmq.client.*;

import java.io.IOException;
import java.util.Collections;
import java.util.Date;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentNavigableMap;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicBoolean;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.rabbitmq.client.AMQP.BasicProperties;

import benchmark.MetricsAggregator;

public class Producer extends Worker {
    private static final Logger log = LoggerFactory.getLogger(Producer.class);

    private final MetricsAggregator metricsAggregator;
    private ConfirmListener listener;
    private final SortedSet<Long> ackSet = Collections.synchronizedSortedSet(new TreeSet<>());
    private final ConcurrentNavigableMap<Long, Message> unconfirmed = new ConcurrentSkipListMap<>();
    private final ConcurrentHashMap<Long, CompletableFuture<Void>> futures = new ConcurrentHashMap<>();

    public Producer(ConnectionConfiguration config, MetricsAggregator metricsAggregator, AtomicBoolean running) {
        super(config, running);

        this.connection = config.getOrCreateConnection();
        this.metricsAggregator = metricsAggregator;

        this.listener = createConfirmListener();
    }

    @Override
    protected void attemptChannelInitialization() {
        if (!this.running.get()) {
            return;
        }

        if (this.channel != null && this.channel.isOpen()) {
            return;
        }

        if (this.connection == null || !this.connection.isOpen()) {
            this.connection = this.config.getOrCreateConnection();
        }

        try {
            this.channel = connection.createChannel();
            this.channel.confirmSelect();
            channel.queueDeclare(config.queueName, true, false, false, null);
            this.channel.addConfirmListener(createConfirmListener());
        } catch (Exception e) {
            log.error("Connection error", e);
        }
    }

    private ConfirmListener createConfirmListener() {
        return new ConfirmListener() {
            @Override
            public void handleAck(long deliveryTag, boolean multiple) {
                handleConfirmation(deliveryTag, multiple, true);
            }

            @Override
            public void handleNack(long deliveryTag, boolean multiple) {
                handleConfirmation(deliveryTag, multiple, false);
            }
        };
    }

    private void handleConfirmation(long deliveryTag, boolean multiple, boolean ack) {
        synchronized (ackSet) {
            try {
                if (multiple) {
                    ackSet.headSet(deliveryTag + 1).forEach(tag -> completeFuture(tag, ack));
                    ackSet.removeIf(tag -> tag <= deliveryTag);
                } else {
                    completeFuture(deliveryTag, ack);
                    ackSet.remove(deliveryTag);
                }
            } catch (Exception e) {
                log.error("Error in handleConfirmation: ", e);
            }
        }
    }

    private void completeFuture(long deliveryTag, boolean ack) {
        try {
            CompletableFuture<Void> future = futures.remove(deliveryTag);
            Message message = unconfirmed.remove(deliveryTag);
            if (future != null) {
                if (ack) {
                    future.complete(null);
                    if (message != null) {
                        long timeElapsed = System.currentTimeMillis() - message.timeSent;
                        this.metricsAggregator.recordMessageSent(timeElapsed, message.payload.length);
                    }
                } else {
                    future.completeExceptionally(new RuntimeException("Message NACKed"));
                }
            }
        } catch (Exception e) {
        }
    }

    public CompletableFuture<Void> sendAsync(byte[] payload) {
        BasicProperties props = new BasicProperties.Builder().timestamp(new Date()).build();
        CompletableFuture<Void> future = new CompletableFuture<>();

        try {
            retryOperationWithBackoff(() -> attemptSend(payload, future, props));
        } catch (RuntimeException e) {
            log.error("runtime", e);
            future.completeExceptionally(e);
        }
        return future;
    }

    private void attemptSend(byte[] payload, CompletableFuture<Void> future, BasicProperties props) {
        if (!this.running.get()) {
            return;
        }

        if (!channel.isOpen()) {
            initializeChannel();
            attemptSend(payload, future, props);
            return;
        }

        try {
            channel.basicPublish("", config.queueName, props, payload);

            long msgId = channel.getNextPublishSeqNo();
            ackSet.add(msgId);
            unconfirmed.put(msgId, new Message(System.currentTimeMillis(), payload));
            futures.put(msgId, future);

        } catch (IOException e) {
            log.error("publish error", e);
        }
    }
}
