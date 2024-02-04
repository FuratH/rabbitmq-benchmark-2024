package benchmark.TaskScheduler;

import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import benchmark.FailureInjector;

public class ActionScheduler {

    private static final Logger log = LoggerFactory.getLogger(ActionScheduler.class);

    public List<ScheduledTask> scheduledTasks;
    private FailureInjector failureInjector;

    public ActionScheduler(List<ScheduledTask> scheduledTasks, FailureInjector failureInjector) {
        this.scheduledTasks = scheduledTasks;
        this.failureInjector = failureInjector;
    }

    public void startSchedule() {
        if (this.scheduledTasks == null || this.scheduledTasks.size() == 0 || this.failureInjector == null) {
            log.info("no tasks");
            return;
        }

        ScheduledExecutorService executor = Executors.newScheduledThreadPool(10);
        for (ScheduledTask task : scheduledTasks) {
            Runnable taskRunnable = getRunnableForAction(task.getAction());
            executor.schedule(taskRunnable, task.getDelay(), TimeUnit.MINUTES);
        }
    }

    private Runnable getRunnableForAction(String action) {
        return () -> {
            System.out.println("Executing " + action);
            failureInjector.runAction(action);
        };
    }
}
