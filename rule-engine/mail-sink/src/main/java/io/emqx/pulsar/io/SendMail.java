package io.emqx.pulsar.io;

import lombok.extern.slf4j.Slf4j;
import org.apache.pulsar.functions.api.Record;

import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.event.ConnectionAdapter;
import javax.mail.event.ConnectionEvent;
import javax.mail.event.TransportAdapter;
import javax.mail.event.TransportEvent;
import javax.mail.internet.MimeMessage;

@Slf4j
public class SendMail implements Runnable {

    private Record<String> record;
    private Session session;
    private String from;
    private MailActionConfig config;


    SendMail(Record<String> record, Session session, String from, MailActionConfig config) {
        this.record = record;
        this.session = session;
        this.from = from;
        this.config = config;
    }

    @Override
    public void run() {
        try {
            MimeMessage message = new MimeMessage(session);
            message.setFrom(from);
            message.setSubject(config.getTitle());
            message.setContent(config.getContent(), "text/html;charset=UTF-8");
            for (String email : config.getEmails()) {
                message.addRecipients(Message.RecipientType.TO, email);
            }
            Transport transport = session.getTransport();
            TransportAdapter adapter = new TransportAdapter() {
                @Override
                public void messageDelivered(TransportEvent e) {
                    log.debug("messageDelivered");
                    record.ack();
                }

                @Override
                public void messageNotDelivered(TransportEvent e) {
                    log.debug("messageNotDelivered");
                    record.fail();
                }

                @Override
                public void messagePartiallyDelivered(TransportEvent e) {
                    log.debug("messagePartiallyDelivered");
                    record.ack();
                }
            };
            transport.addConnectionListener(new ConnectionAdapter() {
                @Override
                public void opened(ConnectionEvent e) {
                    log.debug("Opened");
                }

                @Override
                public void disconnected(ConnectionEvent e) {
                    log.debug("Disconnected");
                }

                @Override
                public void closed(ConnectionEvent e) {
                    log.debug("Closed");
                }
            });
            transport.addTransportListener(adapter);
            transport.connect();
            transport.sendMessage(message, message.getAllRecipients());
            transport.close();
        } catch (MessagingException e) {
            log.error(e.getMessage());
            record.fail();
        }


    }
}
