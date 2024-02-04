package benchmark.worker;

import com.rabbitmq.client.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.net.SocketException;
import java.util.concurrent.atomic.AtomicBoolean;

public abstract class Worker {
    protected static final Logger log = LoggerFactory.getLogger(Worker.class);

    protected Channel channel;
    protected Connection connection;
    protected ConnectionConfiguration config;
    protected AtomicBoolean running;

    protected Worker(ConnectionConfiguration config, AtomicBoolean running) {
        this.running = running;
        this.config = config;
        initializeChannel();
    }

    protected void initializeChannel() {
        if (this.running.get()) {
            retryOperationWithBackoff(this::attemptChannelInitialization);
        }
    }

    protected abstract void attemptChannelInitialization() throws Exception;

    protected void retryOperationWithBackoff(RunnableWithException operation) {
        while (this.running.get()) {
            try {
                operation.run();
                return;
            } catch (SocketException e) {
                log.error("Socket error", e);
                checkAndRecoverConnection();
            } catch (Exception e) {
                log.error("Retry error", e);
            }
        }
    }

    protected void checkAndRecoverConnection() {
        if (this.running.get() && (this.connection == null || !this.connection.isOpen())) {
            log.info("Connection is closed or null, attempting to reconnect.");
            try {
                this.connection = this.config.getOrCreateConnection();
                initializeChannel();
            } catch (Exception e) {
                log.error("Recovering error", e);
            }
        }
    }

    public void close() {
        try {
            if (channel != null && channel.isOpen()) {
                channel.close();
            }
            this.connection.close();
            this.connection.abort();
        } catch (AlreadyClosedException e) {
            log.warn("Channel already closed", e);
        } catch (Exception e) {
            log.error("Error closing channel", e);
        }
    }

    public void stopWorker() {
        this.running.set(false);
        this.close();
        log.info("closing");
    }

    @FunctionalInterface
    protected interface RunnableWithException {
        void run() throws Exception;
    }
}
