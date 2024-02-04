package benchmark;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedList;
import java.util.List;

public class Results {
    public static List<Results> benchmarkingResults = new LinkedList<>();

    public long timeElapsed;
    public long messageSentCount;
    public long messageSentThroughput;
    public long messageReceivedCount;
    public long publishLatencyMinValue;
    public long publishLatencyValueAtPercentile50;
    public long publishLatencyValueAtPercentile75;
    public long publishLatencyValueAtPercentile95;
    public long publishLatencyValueAtPercentile99;
    public long endToEndLatencyMinValue;
    public long endToEndLatencyValueAtPercentile50;
    public long endToEndLatencyValueAtPercentile75;
    public long endToEndLatencyValueAtPercentile95;
    public long endToEndLatencyValueAtPercentile99;
    public String masternode;

    public Results(long timeElapsed,
            long messageSentCount,
            long messageSentThroughput,
            long messageReceivedCount,
            long publishLatencyMinValue,
            long publishLatencyValueAtPercentile50,
            long publishLatencyValueAtPercentile75,
            long publishLatencyValueAtPercentile95,
            long publishLatencyValueAtPercentile99,
            long endToEndLatencyMinValue,
            long endToEndLatencyValueAtPercentile50,
            long endToEndLatencyValueAtPercentile75,
            long endToEndLatencyValueAtPercentile95,
            long endToEndLatencyValueAtPercentile99,
            String masternode) {
        this.timeElapsed = timeElapsed;
        this.messageSentCount = messageSentCount;
        this.messageSentThroughput = messageSentThroughput;
        this.messageReceivedCount = messageReceivedCount;
        this.publishLatencyMinValue = publishLatencyMinValue;
        this.publishLatencyValueAtPercentile50 = publishLatencyValueAtPercentile50;
        this.publishLatencyValueAtPercentile75 = publishLatencyValueAtPercentile75;
        this.publishLatencyValueAtPercentile95 = publishLatencyValueAtPercentile95;
        this.publishLatencyValueAtPercentile99 = publishLatencyValueAtPercentile99;
        this.endToEndLatencyMinValue = endToEndLatencyMinValue;
        this.endToEndLatencyValueAtPercentile50 = endToEndLatencyValueAtPercentile50;
        this.endToEndLatencyValueAtPercentile75 = endToEndLatencyValueAtPercentile75;
        this.endToEndLatencyValueAtPercentile95 = endToEndLatencyValueAtPercentile95;
        this.endToEndLatencyValueAtPercentile99 = endToEndLatencyValueAtPercentile99;
        this.masternode = masternode;

        // Add results to list after creating Result object
        benchmarkingResults.add(this);
    }

    public static void writeToCSV(String fileName) {
        // Write results list to CSV file
        try (FileWriter fileWriter = new FileWriter(fileName);
                PrintWriter printWriter = new PrintWriter(fileWriter)) {

            printWriter.println("TimeElapsed (s),MessageSentCount,MessageSentThroughput (KB/s),MessageReceivedCount," +
                    "PublishLatencyMinValue (ms),PublishLatencyValueAtPercentile50 (ms),PublishLatencyValueAtPercentile75 (ms),"
                    +
                    "PublishLatencyValueAtPercentile95 (ms),PublishLatencyValueAtPercentile99 (ms)," +
                    "EndToEndLatencyMinValue (ms),EndToEndLatencyValueAtPercentile50 (ms),EndToEndLatencyValueAtPercentile75 (ms),"
                    +
                    "EndToEndLatencyValueAtPercentile95 (ms),EndToEndLatencyValueAtPercentile99 (ms),masternode");

            for (Results result : benchmarkingResults) {
                printWriter.printf("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s%n",
                        result.timeElapsed, result.messageSentCount, result.messageSentThroughput,
                        result.messageReceivedCount, result.publishLatencyMinValue,
                        result.publishLatencyValueAtPercentile50, result.publishLatencyValueAtPercentile75,
                        result.publishLatencyValueAtPercentile95, result.publishLatencyValueAtPercentile99,
                        result.endToEndLatencyMinValue, result.endToEndLatencyValueAtPercentile50,
                        result.endToEndLatencyValueAtPercentile75, result.endToEndLatencyValueAtPercentile95,
                        result.endToEndLatencyValueAtPercentile99, result.masternode);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
