package benchmark.Workload;

import java.util.Random;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import benchmark.worker.ProducerWorkAssignment;

public class WorkloadGenerator {
    private final Workload workload;

    private static final Logger log = LoggerFactory.getLogger(WorkloadGenerator.class);

    public WorkloadGenerator(Workload workload) {
        this.workload = workload;
    }

    public void generateWorkload(ProducerWorkAssignment producerWorkAssignment) {
        int sizeInBytes = workload.messageSize * 1024;
        byte[] workload = new byte[sizeInBytes];

        Random random = new Random(this.workload.seed);
        random.nextBytes(workload);

        producerWorkAssignment.payloadData.add(workload);
    }
}
