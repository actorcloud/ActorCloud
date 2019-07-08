package io.emqx.pulsar.functions;

import io.emqx.pulsar.functions.windowing.SessionConfig;
import io.emqx.stream.common.JsonParser;
import io.emqx.stream.common.internal.MockContext;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.functions.windowing.Event;
import org.apache.pulsar.functions.windowing.Window;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@SuppressWarnings("unchecked")
public class TestContextWindowFunctionExecutor {

  private static final long TIMESTAMP = 1516776194873L;
  @SuppressWarnings("TypeParameterHidesVisibleType")
  private class MockContextWindowFunctionExecutor<Integer, Void> extends ContextWindowFunctionExecutor{

    private List<Event<java.lang.Integer>> currentWindow = Collections.emptyList();
    @Override
    public Void process(Window inputWindow) {
      //noinspection unchecked
      currentWindow = inputWindow.get();
      return null;
    }

    protected List<Event<java.lang.Integer>> getCurrentWindow(){
      return currentWindow;
    }
  }

  @SuppressWarnings("TypeParameterHidesVisibleType")
  private class MockEvent<Integer> implements Event {
    private final Record<Integer> record;
    private final Integer event;
    private final long ts;
    @SuppressWarnings("SameParameterValue")
    MockEvent(Integer event, long ts, Record<Integer> record) {
      this.event = event;
      this.ts = ts;
      this.record = record;
    }

    @Override
    public Record<?> getRecord() {
      return record;
    }

    @Override
    public long getTimestamp() {
      return ts;
    }

    @Override
    public Object get() {
      return event;
    }

    @Override
    public boolean isWatermark() {
      return false;
    }
  }

  @Test
  public void testSessionConfig(){
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT ts FROM sample$$abc where temperature" +
            " > 25.0\",\"actions\":[{\"file\":\"newfile\"}]," +
            "\"__session\":{\"windowLengthDurationMs\":40000,\"timeoutlDurationMs\":4000}," +
            "\"__WINDOWCONFIGS__\":{\"actualWindowFunctionClassName\":\"DummyWindowFunction\"}}");
    MockContext context = new MockContext(userConfigMap);
    ContextWindowFunctionExecutor executor = new ContextWindowFunctionExecutor();
    executor.initialize(context);
    SessionConfig expected = new SessionConfig().setTimeoutlDurationMs(4000L).setWindowLengthDurationMs(40000L);
    Assert.assertEquals(executor.sessionConfig, expected);
  }

  @Test
  public void testSessionActivation() throws Exception {
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT ts FROM sample$$abc where temperature" +
            " > 25.0\",\"actions\":[{\"file\":\"newfile\"}]," +
            "\"__session\":{\"windowLengthDurationMs\":70,\"timeoutlDurationMs\":40}," +
            "\"__WINDOWCONFIGS__\":{\"actualWindowFunctionClassName\":\"DummyWindowFunction\"}}");
    MockContext context = new MockContext(userConfigMap);
    MockContextWindowFunctionExecutor executor = new MockContextWindowFunctionExecutor();
    executor.process(createEvent(1, context), context);
    Thread.sleep(800);
    //Should have timeout
    Assert.assertEquals(executor.getCurrentWindow().size(), 1);
    executor.process(createEvent(2, context), context); //0
    Thread.sleep(30);
    executor.process(createEvent(3, context), context); //30
    Thread.sleep(30);
    executor.process(createEvent(4, context), context); //60
    Thread.sleep(30);
    Assert.assertEquals(executor.getCurrentWindow().size(), 3);
    executor.process(createEvent(5, context), context); //90
    //This is the duration window
    Thread.sleep(100);
    //Another timeout window
    Assert.assertEquals(executor.getCurrentWindow().size(), 1);
  }

  private MockEvent createEvent(int i, MockContext context) {
    Record rec =  new Record<Integer>() {
      @Override
      public Optional<String> getKey() {
        return Optional.empty();
      }

      @Override
      public Integer getValue() {
        return null;
      }
    };
    context.setRecord(rec);
    return new MockEvent<>(i, TIMESTAMP, rec);
  }

}
