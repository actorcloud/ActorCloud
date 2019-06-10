package io.emqx.pulsar.io;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import org.apache.pulsar.shade.com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.io.IOException;
import java.util.Map;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class DatabaseActionConfig {

    private Map<String, String> columns;

    public static DatabaseActionConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), DatabaseActionConfig.class);
    }
}
