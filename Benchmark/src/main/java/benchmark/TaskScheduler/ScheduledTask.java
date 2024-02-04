package benchmark.TaskScheduler;

public class ScheduledTask {
    private int delay; // Delay in minutes
    private String action;

    public int getDelay() {
        return delay;
    }

    public void setDelay(int delay) {
        this.delay = delay;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }
}
