package io.emqx.pulsar.functions.windowing;

import org.apache.pulsar.functions.windowing.TriggerPolicy;
import org.apache.pulsar.functions.windowing.WindowLifecycleListener;
import org.apache.pulsar.functions.windowing.WindowManager;

import java.util.ArrayList;
import java.util.Collection;

@SuppressWarnings("unchecked")
public class WindowAllowEmptyManager<T> extends WindowManager {
  public WindowAllowEmptyManager(WindowLifecycleListener lifecycleListener, Collection queue) {
    super(lifecycleListener, queue);
  }

  @Override
  public boolean onTrigger() {
    boolean nonEmptyEvents = super.onTrigger();
    if(!nonEmptyEvents){
      windowLifecycleListener.onActivation(new ArrayList<>(), new ArrayList<>(), new ArrayList<>(),
              evictionPolicy.getContext().getReferenceTime());
    }
    return true;
  }

  public TriggerPolicy<T, ?> getTriggerPolicy(){
    return triggerPolicy;
  }

}
