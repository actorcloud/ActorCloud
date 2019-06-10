package io.emqx.stream.agent;

import org.apache.pulsar.client.admin.PulsarAdmin;
import org.apache.pulsar.client.api.PulsarClientException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import static org.springframework.boot.SpringApplication.run;

@SuppressWarnings("unused")
@SpringBootApplication
public class AgentApplication {
  public static void main(String[] args) {
    run(AgentApplication.class, args);
  }


  @Value("${pulsar.adminUrl}")
  private String pulsarUrl;


  @Bean
  public PulsarAdmin pulsarAdmin() throws PulsarClientException {
    return PulsarAdmin.builder().serviceHttpUrl(pulsarUrl).build();
  }
}