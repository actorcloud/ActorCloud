package io.emqx.pulsar.functions;

import io.emqx.pulsar.functions.windowing.SessionConfig;
import io.emqx.pulsar.functions.windowing.SessionTimeTriggerPolicy;
import io.emqx.pulsar.functions.windowing.WindowAllowEmptyManager;
import io.emqx.stream.common.Constants;
import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import net.jodah.typetools.TypeResolver;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.functions.utils.WindowConfig;
import org.apache.pulsar.functions.utils.validation.ValidatorImpls;
import org.apache.pulsar.functions.windowing.*;
import org.apache.pulsar.functions.windowing.evictors.CountEvictionPolicy;
import org.apache.pulsar.functions.windowing.evictors.TimeEvictionPolicy;
import org.apache.pulsar.functions.windowing.evictors.WatermarkCountEvictionPolicy;
import org.apache.pulsar.functions.windowing.evictors.WatermarkTimeEvictionPolicy;
import org.apache.pulsar.functions.windowing.triggers.CountTriggerPolicy;
import org.apache.pulsar.functions.windowing.triggers.TimeTriggerPolicy;
import org.apache.pulsar.functions.windowing.triggers.WatermarkCountTriggerPolicy;
import org.apache.pulsar.functions.windowing.triggers.WatermarkTimeTriggerPolicy;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.stream.Collectors;

/**
 * This functions is almost a copy of WindowFunctionExecutor except that it allows context and empty window.
 * And the support for session window
 *
 * Support a user config key Session
 */
@SuppressWarnings({"unchecked", "Convert2MethodRef", "WeakerAccess", "OptionalGetWithoutIsPresent"})
@Slf4j
public class ContextWindowFunctionExecutor<I, O> implements Function<I, O> {

  private boolean initialized;
  protected WindowConfig windowConfig;
  protected SessionConfig sessionConfig;
  protected WindowAllowEmptyManager<I> windowManager;
  private TimestampExtractor<I> timestampExtractor;
  private transient WaterMarkEventGenerator<I> waterMarkEventGenerator;

  private Context context;
  private StringWindowRuleFunction windowFunction;

  protected void initialize(Context context) {
    this.context = context;
    this.windowFunction = new StringWindowRuleFunction();
    this.windowConfig = this.getWindowConfigs(context);
    log.info("Window Config: {}", this.windowConfig);
    this.windowManager = this.getWindowManager(this.windowConfig, context);
    this.initialized = true;
    this.start();
  }

  private WindowConfig getWindowConfigs(Context context) {

    if (!context.getUserConfigValue(WindowConfig.WINDOW_CONFIG_KEY).isPresent()) {
      throw new IllegalArgumentException("Window Configs cannot be found");
    }
    WindowConfig windowConfig = new Gson().fromJson(
            (new Gson().toJson(context.getUserConfigValue(WindowConfig.WINDOW_CONFIG_KEY).get())),
            WindowConfig.class);
    WindowUtils.inferDefaultConfigs(windowConfig);

    if (context.getUserConfigValue(Constants.SESSION_CONFIG_KEY).isPresent()) {
      log.info("Create session config");
      sessionConfig = new Gson().fromJson(
              (new Gson().toJson(context.getUserConfigValue(Constants.SESSION_CONFIG_KEY).get())),
              SessionConfig.class);
      log.info("Session Config: {}", this.sessionConfig);
      //In order to pass the validation
      windowConfig.setWindowLengthDurationMs(sessionConfig.getWindowLengthDurationMs());
    }
    ValidatorImpls.WindowConfigValidator.validateWindowConfig(windowConfig);
    return windowConfig;
  }

  protected WindowAllowEmptyManager<I> getWindowManager(WindowConfig windowConfig, Context context) {

    WindowLifecycleListener<Event<I>> lifecycleListener = newWindowLifecycleListener(context);
    WindowAllowEmptyManager<I> manager = new WindowAllowEmptyManager<>(lifecycleListener, new ConcurrentLinkedQueue<>());

    if (this.windowConfig.getTimestampExtractorClassName() != null) {
      this.timestampExtractor = getTimeStampExtractor(windowConfig);

      waterMarkEventGenerator = new WaterMarkEventGenerator<>(manager, this.windowConfig
              .getWatermarkEmitIntervalMs(),
              this.windowConfig.getMaxLagMs(), new HashSet<>(context.getInputTopics()), context);
    } else {
      if (this.windowConfig.getLateDataTopic() != null) {
        throw new IllegalArgumentException(
                "Late data topic can be defined only when specifying a timestamp extractor class");
      }
    }

    EvictionPolicy<I, ?> evictionPolicy = getEvictionPolicy(windowConfig);
    TriggerPolicy<I, ?> triggerPolicy = getTriggerPolicy(windowConfig, manager,
            evictionPolicy, context);
    manager.setEvictionPolicy(evictionPolicy);
    manager.setTriggerPolicy(triggerPolicy);

    return manager;
  }

  private TimestampExtractor<I> getTimeStampExtractor(WindowConfig windowConfig) {

    Class<?> theCls;
    try {
      theCls = Class.forName(windowConfig.getTimestampExtractorClassName(),
              true, Thread.currentThread().getContextClassLoader());
    } catch (ClassNotFoundException cnfe) {
      throw new RuntimeException(
              String.format("Timestamp extractor class %s must be in class path",
                      windowConfig.getTimestampExtractorClassName()), cnfe);
    }

    Object result;
    try {
      Constructor<?> constructor = theCls.getDeclaredConstructor();
      constructor.setAccessible(true);
      result = constructor.newInstance();
    } catch (InstantiationException ie) {
      throw new RuntimeException("User class must be concrete", ie);
    } catch (NoSuchMethodException e) {
      throw new RuntimeException("User class doesn't have such method", e);
    } catch (IllegalAccessException e) {
      throw new RuntimeException("User class must have a no-arg constructor", e);
    } catch (InvocationTargetException e) {
      throw new RuntimeException("User class constructor throws exception", e);
    }
    Class<?>[] timestampExtractorTypeArgs = TypeResolver.resolveRawArguments(
            TimestampExtractor.class, result.getClass());
    Class<?>[] typeArgs = TypeResolver.resolveRawArguments(Function.class, this.getClass());
    if (!typeArgs[0].equals(timestampExtractorTypeArgs[0])) {
      throw new RuntimeException(
              "Inconsistent types found between function input type and timestamp extractor type: "
                      + " function type = " + typeArgs[0] + ", timestamp extractor type = "
                      + timestampExtractorTypeArgs[0]);
    }
    return (TimestampExtractor<I>) result;
  }

  private TriggerPolicy<I, ?> getTriggerPolicy(WindowConfig windowConfig, WindowManager<I> manager,
                                               EvictionPolicy<I, ?> evictionPolicy, Context context) {
    if (sessionConfig != null){
      if (this.isEventTime()) {
        log.error("Does not support watermark for session window");
        return null;
      }
      return new SessionTimeTriggerPolicy<>(sessionConfig.getWindowLengthDurationMs(), sessionConfig.getTimeoutlDurationMs(), manager,
              evictionPolicy, context);
    }else if (windowConfig.getSlidingIntervalCount() != null) {
      if (this.isEventTime()) {
        return new WatermarkCountTriggerPolicy<>(
                windowConfig.getSlidingIntervalCount(), manager, evictionPolicy, manager);
      } else {
        return new CountTriggerPolicy<>(windowConfig.getSlidingIntervalCount(), manager, evictionPolicy);
      }
    } else {
      if (this.isEventTime()) {
        return new WatermarkTimeTriggerPolicy<>(windowConfig.getSlidingIntervalDurationMs(), manager,
                evictionPolicy, manager);
      }
      return new TimeTriggerPolicy<>(windowConfig.getSlidingIntervalDurationMs(), manager,
              evictionPolicy, context);
    }
  }

  private EvictionPolicy<I, ?> getEvictionPolicy(WindowConfig windowConfig) {
    if (sessionConfig != null){
      if (this.isEventTime()) {
        return new WatermarkTimeEvictionPolicy<>(
                0L, windowConfig.getMaxLagMs());
      } else {
        return new TimeEvictionPolicy<>(0L);
      }
    }else if (windowConfig.getWindowLengthCount() != null) {
      if (this.isEventTime()) {
        return new WatermarkCountEvictionPolicy<>(windowConfig.getWindowLengthCount());
      } else {
        return new CountEvictionPolicy<>(windowConfig.getWindowLengthCount());
      }
    } else {
      if (this.isEventTime()) {
        return new WatermarkTimeEvictionPolicy<>(
                windowConfig.getWindowLengthDurationMs(), windowConfig.getMaxLagMs());
      } else {
        return new TimeEvictionPolicy<>(windowConfig.getWindowLengthDurationMs());
      }
    }
  }

  private WindowLifecycleListener<Event<I>> newWindowLifecycleListener(Context context) {
    return new WindowLifecycleListener<Event<I>>() {
      @Override
      public void onExpiry(List<Event<I>> events) {
        for (Event<I> event : events) {
          event.getRecord().ack();
        }
      }

      @Override
      public void onActivation(List<Event<I>> tuples, List<Event<I>> newTuples, List<Event<I>>
              expiredTuples, Long referenceTime) {
        processWindow(
                context,
                tuples.stream().map(event -> event.get()).collect(Collectors.toList()),
                newTuples.stream().map(event -> event.get()).collect(Collectors.toList()),
                expiredTuples.stream().map(event -> event.get()).collect(Collectors.toList()),
                referenceTime);
      }
    };
  }

  private void processWindow(Context context, List<I> tuples, List<I> newTuples, List<I>
          expiredTuples, Long referenceTime) {

    O output;
    try {
      output = this.process(
              new WindowImpl<>(tuples, newTuples, expiredTuples, getWindowStartTs(referenceTime), referenceTime));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
    if (output != null) {
      context.publish(context.getOutputTopic(), output, context.getOutputSchemaType());
    }
  }

  private Long getWindowStartTs(Long endTs) {
    Long res = null;
    if (endTs != null && this.windowConfig.getWindowLengthDurationMs() != null) {
      res = endTs - this.windowConfig.getWindowLengthDurationMs();
    }
    return res;
  }

  private void start() {
    if (this.waterMarkEventGenerator != null) {
      log.debug("Starting waterMarkEventGenerator");
      this.waterMarkEventGenerator.start();
    }

    log.debug("Starting trigger policy");
    this.windowManager.getTriggerPolicy().start();
  }

  public void shutdown() {
    if (this.waterMarkEventGenerator != null) {
      this.waterMarkEventGenerator.shutdown();
    }
    if (this.windowManager != null) {
      this.windowManager.shutdown();
    }
  }

  private boolean isEventTime() {
    return this.timestampExtractor != null;
  }

  @Override
  public O process(I input, Context context) {
    if (!this.initialized) {
      initialize(context);
    }

    Record<?> record = context.getCurrentRecord();

    if (isEventTime()) {
      long ts = this.timestampExtractor.extractTimestamp(input);
      if (this.waterMarkEventGenerator.track(record.getTopicName().get(), ts)) {
        this.windowManager.add(input, ts, record);
      } else {
        if (this.windowConfig.getLateDataTopic() != null) {
          context.publish(this.windowConfig.getLateDataTopic(), input);
        } else {
          log.info(String.format(
                  "Received a late tuple %s with ts %d. This will not be " + "processed"
                          + ".", input, ts));
        }
        record.ack();
      }
    } else {
      this.windowManager.add(input, System.currentTimeMillis(), record);
    }
    return null;
  }

  public O process(Window<I> inputWindow) throws Exception {
    return (O) windowFunction.process((Collection<String>) inputWindow.get(), context);
  }
}
