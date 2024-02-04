package benchmark;

import java.io.IOException;
import java.nio.file.Paths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;

public class FileUpload {
  private static final Logger log = LoggerFactory.getLogger(FileUpload.class);

  // Upload file to google bucket
  public static void uploadFile(String path, String filename, String projectId, String bucketName) throws IOException {
    Storage storage = StorageOptions.newBuilder().setProjectId(projectId).build().getService();

    BlobId blobId = BlobId.of(bucketName, filename);
    BlobInfo blobInfo = BlobInfo.newBuilder(blobId).build();

    storage.createFrom(blobInfo, Paths.get(path));
    log.info("File {} uploaded to bucket {} as {}", path, bucketName, filename);
  }
}
