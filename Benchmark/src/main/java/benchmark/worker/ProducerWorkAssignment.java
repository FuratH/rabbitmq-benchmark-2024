package benchmark.worker;

import java.util.ArrayList;
import java.util.List;

public class ProducerWorkAssignment {

    public List<byte[]> payloadData;

    public ProducerWorkAssignment() {
        this.payloadData = new ArrayList<>();
    }

    public ProducerWorkAssignment(List<byte[]> payloadData) {
        this.payloadData = payloadData;
    }
}