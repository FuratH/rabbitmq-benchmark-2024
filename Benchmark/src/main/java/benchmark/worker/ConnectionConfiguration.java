package benchmark.worker;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.rabbitmq.client.Address;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;

public class ConnectionConfiguration {

    private static final Logger log = LoggerFactory.getLogger(ConnectionConfiguration.class);

    public List<String> amqpUris = new ArrayList<>();
    public boolean messagePersistence;
    public long producerCreationDelay;
    public int producerCreationBatchSize;
    public long consumerCreationDelay;
    public int consumerCreationBatchSize;
    public String primaryBrokerUri;
    public String apiUrl;
    public String queueName;
    public String projectId;
    public String bucketName;

    public Connection getOrCreateConnection() {
        try {
            ConnectionFactory connectionFactory = new ConnectionFactory();
            connectionFactory.setAutomaticRecoveryEnabled(true);
            connectionFactory.setTopologyRecoveryEnabled(true);

            if (primaryBrokerUri != null) {
                URI primaryUri = new URI(primaryBrokerUri);
                connectionFactory.setUri(primaryUri);
            }

            List<Address> addresses = amqpUris.stream()
                    .map(URI::create)
                    .map(uri -> new Address(uri.getHost(), uri.getPort()))
                    .collect(Collectors.toList());

            return connectionFactory.newConnection(addresses);
        } catch (Exception e) {
            throw new RuntimeException("Couldn't establish connection", e);
        }
    }

}
