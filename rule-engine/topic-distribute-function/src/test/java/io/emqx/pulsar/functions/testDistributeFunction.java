package io.emqx.pulsar.functions;

import io.emqx.stream.common.internal.MockContext;
import org.testng.Assert;
import org.testng.annotations.Test;

public class testDistributeFunction {
  @Test
  public void testDistribute(){
    MockContext context = new MockContext();
    TopicDistributeFunction function = new TopicDistributeFunction();
    function.process("up/tenant1/product1/device2/topic1%;{\"temperature\":27,\"ts\":1541152486032}", context);
    Assert.assertEquals(context.getResultTopic(), "up%%tenant1%%product1%%device2%%topic1");
    Assert.assertEquals(context.getResult(), "{\"temperature\":27,\"ts\":1541152486032}");
  }
}
