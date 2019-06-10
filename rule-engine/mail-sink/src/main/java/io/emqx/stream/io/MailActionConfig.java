package io.emqx.stream.io;


import lombok.Getter;
import lombok.Setter;
import org.apache.pulsar.shade.com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import org.apache.pulsar.shade.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@Getter
@Setter
@JsonIgnoreProperties(ignoreUnknown = true)
class MailActionConfig {

    private String title;
    private String content;
    private List<String> emails;

    static MailActionConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), MailActionConfig.class);
    }

}
