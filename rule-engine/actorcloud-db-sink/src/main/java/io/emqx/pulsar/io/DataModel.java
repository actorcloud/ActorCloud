package io.emqx.pulsar.io;


import lombok.Data;

@Data
public class DataModel extends BaseData {
    /**
     * time : 12314141
     * value : 82
     */

    private long time = -1;
    private Object value;

    public boolean isInvalid() {
        return time == -1 || value == null;
    }


}
