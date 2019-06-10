package io.emqx.pulsar.io;

import io.emqx.stream.common.JsonParser;
import com.google.gson.annotations.SerializedName;
import lombok.Data;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Stream;

@Data
public class ActorcloudPayload extends BaseData {

    /**
     * {
     * "data_type": "event",
     * "stream_id": 'stream1',
     * "data": {
     * "act_th": {"time": 1547661822, "value": 100},
     * "ina_th": {"time": 1547661822, "value": 100},
     * "act_time": {"time": 1547661822, "value": 100}
     * }
     * }
     */


    @SerializedName("data_type")
    private String dataType;

    @SerializedName("stream_id")
    private String streamID;

    private Result result;

    private Map<String, Object> data;


    @Override
    public boolean isInvalid() {
        if (getDataType() == 1) {
            return hasInvalidData();
        } else if (getDataType() == 2) {
            return isResultInvalid();
        } else {
            return true;
        }
    }

    int getDataType() {
        Map<String, Integer> dataTypeMap = new HashMap<String, Integer>() {{
            put("event", 1);
            put("response", 2);
        }};
        return dataTypeMap.getOrDefault(dataType, -1);
    }


    String getDataJson() {
        if (data == null) {
            return null;
        }
        if (isGateway()) {
            return data.containsKey("gateway") ? JsonParser.toJson(data.get("gateway")) : null;
        } else {
            return JsonParser.toJson(data);
        }
    }

    String getResultJson() {
        return result == null ? null : JsonParser.toJson(result);
    }


    boolean isGateway() {
        if (data != null) {
            return data.containsKey("gateway") || data.containsKey("devices");
        } else {
            return false;
        }

    }

    ArrayList<SubDevice> getSubDevices() {
        //noinspection unchecked
        return (ArrayList<SubDevice>) data.get("devices");
    }


    private boolean hasInvalidData() {
        if (data == null || streamID == null) {
            return true;
        }

        if (isGateway()) {
            return Stream.of(isGatewayInvalid(), isSubDevicesInvalid()).anyMatch(aBoolean -> aBoolean);
        } else {
            return data.values().stream().anyMatch(o -> {
                if (o instanceof DataModel) {
                    return ((DataModel) o).isInvalid();
                } else {
                    return true;
                }
            });
        }
    }

    private boolean isResultInvalid() {
        return result == null || result.isInvalid();
    }

    private boolean isGatewayInvalid() {
        //noinspection unchecked
        return data.containsKey("gateway") && isDataMapInvalid(((Map<String, DataModel>) data.get("gateway")));
    }


    private boolean isSubDevicesInvalid() {
        return getSubDevices() != null && getSubDevices().stream().anyMatch(SubDevice::isInvalid);
    }
}
