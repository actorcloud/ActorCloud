package io.emqx.pulsar.io;

import com.google.gson.*;

import java.lang.reflect.Type;
import java.util.*;

public class MapJsonDeserializer implements JsonDeserializer<Map<String, Object>> {
    @Override
    public Map<String, Object> deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        Map<String, Object> treeMap = new HashMap<>();
        JsonObject jsonObject = jsonElement.getAsJsonObject();
        Set<Map.Entry<String, JsonElement>> entrySet = jsonObject.entrySet();
        Gson gson = new Gson();
        for (Map.Entry<String, JsonElement> entry : entrySet) {
            String key = entry.getKey();
            JsonElement element = entry.getValue();
            switch (key) {
                case "gateway":
                    if (element.isJsonObject()) {
                        Map<String, DataModel> dataModelMap = new HashMap<>();
                        element.getAsJsonObject().entrySet().forEach(stringJsonElementEntry ->
                                dataModelMap.put(stringJsonElementEntry.getKey(), gson.fromJson(stringJsonElementEntry.getValue(), DataModel.class)));
                        treeMap.put(key, dataModelMap);
                    } else {
                        treeMap.put(key, null);
                    }
                    break;
                case "devices":
                    List<SubDevice> list = new ArrayList<>();
                    if (element.isJsonArray()) {
                        JsonArray jsonArray = element.getAsJsonArray();
                        jsonArray.forEach(jsonElement1 -> list.add(gson.fromJson(jsonElement1, SubDevice.class)));
                        treeMap.put(key, list);
                    } else {
                        treeMap.put(key, null);
                    }
                    break;
                default:
                    if (element.isJsonObject()) {
                        treeMap.put(key, gson.fromJson(element, DataModel.class));
                    } else {
                        treeMap.put(key, element);
                    }
                    break;
            }
        }
        return treeMap;
    }
}
