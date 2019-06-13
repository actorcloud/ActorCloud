package io.emqx.pulsar.io;


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
public class WebhookSink implements Sink<String> {

    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    private OkHttpClient client;


    @SuppressWarnings("RedundantThrows")
    @Override
    public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {
        client = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .writeTimeout(10, TimeUnit.SECONDS)
                .addInterceptor(new LoggingInterceptor())
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
            WebhookActionConfig webhookActionConfig = WebhookActionConfig.load(action);
            String url = webhookActionConfig.getUrl();
            post(url, message, new WebhookCallback(record));
        }

    }

    @SuppressWarnings("RedundantThrows")
    @Override
    public void close() throws Exception {
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

    class WebhookCallback implements Callback {

        private final Record record;

        WebhookCallback(Record record) {
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


    @SuppressWarnings("unused")
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
