package io.emqx.stream;

import lombok.Data;
import org.apache.pulsar.shade.com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import org.apache.pulsar.shade.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.Map;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class WebhookActionConfig {

    private String url;

    private String token;

    public static WebhookActionConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), WebhookActionConfig.class);
    }
}
