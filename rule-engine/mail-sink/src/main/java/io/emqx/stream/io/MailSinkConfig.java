package io.emqx.stream.io;

import lombok.Getter;
import org.apache.pulsar.shade.com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import org.apache.pulsar.shade.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.Map;

@Getter
@JsonIgnoreProperties(ignoreUnknown = true)
class MailSinkConfig {

    private String host;
    private int port = 25;
    private String user;
    private String password;
    private String from;
    //  SSL or STARTTLS
    private String encryptionType;
    private boolean debug;


    static MailSinkConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), MailSinkConfig.class);
    }


}
