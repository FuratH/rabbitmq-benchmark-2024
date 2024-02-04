
package benchmark.worker;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MessageProducer {

    private static final Logger log = LoggerFactory.getLogger(MessageProducer.class);

    public void sendMessage(Producer producer, byte[] payload) {

        final long sendTime = System.currentTimeMillis();
        producer
                .sendAsync(payload)
                .thenRun(() -> success(payload.length, 0, sendTime))
                .exceptionally(this::failure);
    }

    private void success(long payloadLength, long intendedSendTime, long sendTime) {
        // log.info("success");
    }

    private Void failure(Throwable t) {
        log.warn("Write error on message", t);
        return null;
    }

}
