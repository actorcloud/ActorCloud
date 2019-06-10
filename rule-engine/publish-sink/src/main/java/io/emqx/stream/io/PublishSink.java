package io.emqx.stream.io;

import io.emqx.stream.common.JsonParser;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.io.core.Sink;
import org.apache.pulsar.io.core.SinkContext;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Slf4j
public class PublishSink implements Sink<String> {
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    private OkHttpClient client;
    private String url;


    @Override
    public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {
        PublishSinkConfig publishSinkConfig = PublishSinkConfig.load(config);

        url = publishSinkConfig.getUrl();
        String username = publishSinkConfig.getUsername();
        String password = publishSinkConfig.getPassword();
        if (url == null) {
            throw new IllegalArgumentException("Required publish url not set.");
        }

        client = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .writeTimeout(10, TimeUnit.SECONDS)
                .addInterceptor(new LoggingInterceptor())
                .authenticator((route, response) -> {
                    String credential = Credentials.basic(username, password);
                    return response.request().newBuilder().header("Authorization", credential).build();
                })
                .build();
        log.info("Init client success");


    }

    @Override
    public void write(Record<String> record) throws Exception {
        String message = record.getValue();
        log.debug("Receive message {}", message);
        Map<String, Object> actionMessage = JsonParser.parseMqttMessage(message);
        if (actionMessage != null) {
            //noinspection unchecked
            Map<String, Object> action = (Map<String, Object>) actionMessage.get("action");
            String payload = ((String) action.get("json"));
            post(url, payload, new HttpCallback(record));
        }

    }

    @Override
    public void close() {
        client.dispatcher().executorService().shutdown();
        client.connectionPool().evictAll();
        log.info("Client resources released");
    }

    private void post(String url, String json, Callback callback) {
        RequestBody body = RequestBody.create(JSON, json);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();
        client.newCall(request).enqueue(callback);
    }

    class HttpCallback implements Callback {

        private final Record record;

        HttpCallback(Record record) {
            this.record = record;
        }

        @Override
        public void onFailure(Call call, IOException e) {
            record.fail();
        }

        @Override
        public void onResponse(Call call, Response response) {
            if (response.isSuccessful()) {
                record.ack();
            } else {
                record.fail();
            }
        }
    }


    private static class LoggingInterceptor implements Interceptor {
        @Override
        public Response intercept(Chain chain) throws IOException {
            long t1 = System.nanoTime();
            Request request = chain.request();
            log.debug("Sending request {}", request.url());
            Response response = chain.proceed(request);

            long t2 = System.nanoTime();
            log.debug("Received response for {} in {}ms", request.url(), (t2 - t1) / 1e6d);
            return response;
        }
    }
}
