package benchmark.worker;

public class Message {
    public long timeSent;
    public byte[] payload;

    public Message(long timeSent, byte[] payload) {
        this.payload = payload;
        this.timeSent = timeSent;
    }
}
