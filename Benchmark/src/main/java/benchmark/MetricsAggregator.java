package benchmark;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.concurrent.atomic.AtomicLong;
import org.HdrHistogram.Histogram;
import java.util.concurrent.TimeUnit;

public class MetricsAggregator {
    public final MeterRegistry meterRegistry;

    public final Timer messageLatencyTimer;
    public final Timer messageEndToEndLatencyTimer; // consumer latency
    public final Histogram endToEndLatency; // consumer latency
    public final Histogram producerLatency;

    public final AtomicLong messagesSent = new AtomicLong(0); // mesages succes sent
    public AtomicLong messageReceived = new AtomicLong(0); // message received
    public AtomicLong bytesSent = new AtomicLong(0); // message received

    public final AtomicLong timer = new AtomicLong(0);

    public MetricsAggregator() {

        this.meterRegistry = new SimpleMeterRegistry();
        this.messageLatencyTimer = Timer.builder("message.latency")
                .description("Time taken for messages to be acknowledged")
                .publishPercentiles(0.5, 0.75, 0.95, 0.99)
                .register(meterRegistry);

        this.messageEndToEndLatencyTimer = Timer.builder("end-to-end.latency")
                .description("Time taken for end-to-end message processing")
                .publishPercentiles(0.5, 0.75, 0.95, 0.99)
                .register(meterRegistry);

        this.endToEndLatency = new Histogram(TimeUnit.MINUTES.toMillis(1), 3);
        this.endToEndLatency.setAutoResize(true);

        this.producerLatency = new Histogram(TimeUnit.MINUTES.toMillis(1), 3);
        this.producerLatency.setAutoResize(true);
    }

    // producer latency
    public void recordMessageSent(long latency, int size) {
        messagesSent.incrementAndGet();
        producerLatency.recordValue(latency);
        bytesSent.addAndGet(size);
    }

    // used to record received and latency end to end
    public void recordMessageReceived(long latency) {
        messageReceived.incrementAndGet();
        endToEndLatency.recordValue(latency);
    }

    public long getThroughput() {
        return (bytesSent.getAndSet(0) / 1024);
    }

    public long getTime() {
        return timer.addAndGet(1);
    }

    public long getMessageSendCount() {
        return messagesSent.getAndSet(0); // success sent
    }

    public long getMessageReceivedCount() {
        return messageReceived.getAndSet(0);
    }

    public void reset() {
        this.producerLatency.reset();
        this.endToEndLatency.reset();
    }

}
