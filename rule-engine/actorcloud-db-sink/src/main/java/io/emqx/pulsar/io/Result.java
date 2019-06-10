package io.emqx.pulsar.io;

import com.google.gson.annotations.SerializedName;
import lombok.Data;


@Data
public class Result extends BaseData {

    /**
     * {"task_id":"177a4f99809b5639a425172797bc68ff",code:200}
     */

    @SerializedName("task_id")
    private String taskID;

    private int code = -1;

    @Override
    boolean isInvalid() {
        return taskID == null || code == -1;
    }

}
