package io.emqx.pulsar.io.jdbc;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import lombok.*;
import lombok.experimental.Accessors;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.util.Map;


@Data
@Setter
@Getter
@EqualsAndHashCode
@ToString
@Accessors(chain = true)
public class JdbcSinkConfig implements Serializable {

    private static final long serialVersionUID = 1L;


    private String userName;

    private String password;

    private String jdbcUrl;

    private String tableName;

    private String[] columns;

    private int timeoutMs = 500;

    private int batchSize = 10;

    @SuppressWarnings("unused")
    public static JdbcSinkConfig load(String yamlFile) throws IOException {
        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
        return mapper.readValue(new File(yamlFile), JdbcSinkConfig.class);
    }

    public static JdbcSinkConfig load(Map<String, Object> map) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(new ObjectMapper().writeValueAsString(map), JdbcSinkConfig.class);
    }
}