package io.emqx.pulsar.functions.windowing;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import lombok.extern.slf4j.Slf4j;
import org.apache.logging.log4j.ThreadContext;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.windowing.*;

import java.util.concurrent.*;

@Slf4j
public class SessionTimeTriggerPolicy<T> implements TriggerPolicy<T, Void> {
  private final long duration;
  private final long timeout;
  private final TriggerHandler handler;
  private final EvictionPolicy<T, ?> evictionPolicy;
  private ScheduledFuture<?> executorFuture;
  private ScheduledFuture<?> timeoutFuture;
  private final ScheduledExecutorService executor;
  private final Context context;

  public SessionTimeTriggerPolicy(long duration, long timeout, TriggerHandler handler, EvictionPolicy<T, ?>
          evictionPolicy, Context context) {
    this.duration = duration;
    this.timeout = timeout;
    this.handler = handler;
    this.evictionPolicy = evictionPolicy;
    ThreadFactory threadFactory = new ThreadFactoryBuilder()
            .setNameFormat("time-trigger-policy-%d")
            .setDaemon(true)
            .build();
    this.executor = Executors.newSingleThreadScheduledExecutor(threadFactory);
    this.context = context;
  }

  @Override
  public void track(Event<T> event) {
    checkFailuresAndStart();
  }

  @Override
  public void reset() {
  }

  @Override
  public void start() {
    //The session starts on the first event
  }

  @Override
  public void shutdown() {
    executor.shutdown();
    try {
      if (!executor.awaitTermination(2, TimeUnit.SECONDS)) {
        executor.shutdownNow();
      }
    } catch (InterruptedException ie) {
      executor.shutdownNow();
      Thread.currentThread().interrupt();
    }
  }

  @Override
  public String toString() {
    return "TimeTriggerPolicy{" + "duration=" + duration + '}';
  }

  private Runnable newTriggerTask(boolean isTimeout) {
    return () -> {
      log.info("Trigger with timeout? " + isTimeout);
      // initialize the thread context
      ThreadContext.put("function", WindowUtils.getFullyQualifiedName(
              context.getTenant(), context.getNamespace(), context.getFunctionName()));
      // do not process current timestamp since tuples might arrive while the trigger is executing
      long now = System.currentTimeMillis() - 1;
      try {
        /*
         * set the current timestamp as the reference time for the eviction policy
         * to evict the events
         */
        evictionPolicy.setContext(new DefaultEvictionContext(now, null, null, 0L));
        handler.onTrigger();
        if(isTimeout){
          executorFuture.cancel(true);
        }
      } catch (Throwable th) {
        log.error("handler.onTrigger failed ", th);
        /*
         * propagate it so that task gets canceled and the exception
         * can be retrieved from executorFuture.get()
         */
        throw th;
      }
    };
  }

  private void checkFailuresAndStart() {
    if (executorFuture != null && executorFuture.isDone()) {
      try {
        if(executorFuture.isCancelled()){
          executorFuture = null;
        }else{
          executorFuture.get();
        }
      } catch (InterruptedException | ExecutionException e) {
        log.error("Got exception in timer trigger policy ", e);
        executorFuture = null;
      }
    }

    if(executorFuture == null){
      executorFuture = executor.scheduleAtFixedRate(newTriggerTask(false), duration, duration, TimeUnit.MILLISECONDS);
    }
    if(timeoutFuture != null){
      try{
        timeoutFuture.cancel(true);
      } catch (Exception e) {
        log.error("Got exception while cancelling timeout trigger", e);
      }
    }
    timeoutFuture = executor.schedule(newTriggerTask(true), timeout, TimeUnit.MILLISECONDS);
  }

  @Override
  public Void getState() {
    return null;
  }

  @Override
  public void restoreState(Void state) {

  }
}
