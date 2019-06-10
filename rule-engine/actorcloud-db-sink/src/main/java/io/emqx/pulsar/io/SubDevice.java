package io.emqx.pulsar.io;

import com.google.gson.annotations.SerializedName;
import lombok.Data;

import java.util.HashMap;

@Data
public class SubDevice extends BaseData {

    /**
     * {
     * "device_id": "device_id_1",
     * "data": {
     * "status": {
     * "time": 1547661822,
     * "value": true
     * },
     * "mode": {
     * "time": 1547661822,
     * "value": "cold"
     * }    }
     * }
     */

    @SerializedName("device_id")
    private String deviceID;

    private HashMap<String, DataModel> data;

    @Override
    public boolean isInvalid() {
        return deviceID == null || isDataMapInvalid(data);
    }

}
