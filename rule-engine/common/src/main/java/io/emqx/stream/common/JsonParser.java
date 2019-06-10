package io.emqx.stream.common;

import java.lang.reflect.Type;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;

public class JsonParser {

  public static Map<String, Object> parseMqttMessage(String input) {
    Type type = new TypeToken<Map<String, Object>>() {}.getType();
    try {
      return new Gson().fromJson(input, type);
    } catch(JsonSyntaxException exp) {
      return null;
    }
  }

  public static Map<String, Object> parseRule(String input) {
    Type type = new TypeToken<Map<String, Object>>() {}.getType();
    try {
      return new Gson().fromJson(input, type);
    } catch(JsonSyntaxException exp) {
      return null;
    }
  }

  public static String toJson(Object resultMap) {
    return new Gson().toJson(resultMap);
  }

  @SuppressWarnings("unused")
  public static <T> T fromJson(String json, Class<T> classOfT) {
    return new Gson().fromJson(json, classOfT);
  }
}
