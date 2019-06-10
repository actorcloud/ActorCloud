package io.emqx.stream.io;

import io.emqx.stream.common.JsonParser;
import lombok.extern.slf4j.Slf4j;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.io.core.Sink;
import org.apache.pulsar.io.core.SinkContext;

import javax.mail.Authenticator;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Slf4j
public class MailSink implements Sink<String> {

    private static final int corePoolSize = 1;

    private static final int maximumPoolSize = 4;

    private static final long keepAliveTime = 0;


    private ExecutorService executorService;
    private Session session;
    private MailSinkConfig mailSinkConfig;


    @Override
    public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {

        BlockingQueue<Runnable> workQueue = new LinkedBlockingDeque<>();
        executorService = new ThreadPoolExecutor(corePoolSize, maximumPoolSize, keepAliveTime,
                TimeUnit.SECONDS, workQueue, new ThreadPoolExecutor.CallerRunsPolicy());

        mailSinkConfig = MailSinkConfig.load(config);
        Properties props = new Properties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.host", mailSinkConfig.getHost());
        props.put("mail.smtp.port", String.valueOf(mailSinkConfig.getPort()));
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
        props.put("mail.smtp.socketFactory.port", String.valueOf(mailSinkConfig.getPort()));
        props.put("mail.debug", String.valueOf(mailSinkConfig.isDebug()));
        String encryptionType = mailSinkConfig.getEncryptionType();
        if (encryptionType != null) {
            if (encryptionType.toLowerCase().equals("ssl") || encryptionType.toLowerCase().equals("starttls")) {
                props.put("mail.smtp." + encryptionType.toLowerCase() + ".enable", "true");
            }
        }

        session = Session.getDefaultInstance(props, new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication(mailSinkConfig.getUser(), mailSinkConfig.getPassword());
            }
        });


    }

    @Override
    public void write(Record<String> record) throws Exception {
        String message = record.getValue();
        log.info("MailSink received message: {} ", message);
        Map<String, Object> actionMessage = JsonParser.parseMqttMessage(message);
        assert actionMessage != null;
        //noinspection unchecked
        Map<String, Object> action = (Map<String, Object>) actionMessage.get("action");
        MailActionConfig actionConfig = MailActionConfig.load(action);
        //noinspection unchecked
        List<Map<String, Object>> values = (List<Map<String, Object>>) actionMessage.get("values");
        if (!values.isEmpty()) {
            Map<String, Object> result = values.get(0);

            Map<String, String> map = result.entrySet()
                    .stream()
                    .collect(Collectors.toMap(Map.Entry::getKey, entry -> (String.valueOf(entry.getValue()))));
            String content = renderString(actionConfig.getContent(), map);
            actionConfig.setContent(content);
        }
        executorService.execute(new SendMail(record, session, mailSinkConfig.getFrom(), actionConfig));

    }

    @Override
    public void close() {
        executorService.shutdown();

    }

    private static String renderString(String content, Map<String, String> map) {
        Set<Map.Entry<String, String>> sets = map.entrySet();
        for (Map.Entry<String, String> entry : sets) {
            String regex = "\\$\\{" + entry.getKey() + "}";
            Pattern pattern = Pattern.compile(regex);
            Matcher matcher = pattern.matcher(content);
            content = matcher.replaceAll(entry.getValue());
        }
        return content;
    }
}
