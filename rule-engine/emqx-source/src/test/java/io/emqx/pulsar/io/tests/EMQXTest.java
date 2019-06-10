package io.emqx.pulsar.io.tests;

import io.emqx.pulsar.io.EMQXSource;
import org.apache.pulsar.functions.api.Record;
import org.testng.Assert;

public class EMQXTest {

  @SuppressWarnings("unused")
  public void testOpen() throws Exception {
    EMQXSource source = new EMQXSource();
    source.open(null, null);
    //TODO automatic this
    // Run emq client to publish message
    Record<String> message = source.read();
    while(message == null) {
      Thread.sleep(5000);
      message = source.read();
    }
    Assert.assertEquals("new", message.getValue());
    // Disconnect the client from the server
    source.close();
    log("Disconnected");
  }

  @SuppressWarnings("SameParameterValue")
  private void log(String message) {
    System.out.println(message);
  }
}
