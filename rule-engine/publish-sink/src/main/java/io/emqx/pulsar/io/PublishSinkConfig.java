package io.emqx.pulsar.io;

import lombok.Getter;
import org.apache.pulsar.shade.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.Map;


@Getter
public class PublishSinkConfig {

    private String url;
    private String username;
    private String password;

    public static PublishSinkConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), PublishSinkConfig.class);
    }
}
