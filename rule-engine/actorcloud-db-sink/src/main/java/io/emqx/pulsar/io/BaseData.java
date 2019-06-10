package io.emqx.pulsar.io;

import java.util.Map;

abstract class BaseData {

    abstract boolean isInvalid();


    <T extends BaseData> boolean isDataMapInvalid(Map<String, T> map) {
        if (map == null) {
            return true;
        } else {
            return map.values().stream().anyMatch(BaseData::isInvalid);
        }
    }
}
