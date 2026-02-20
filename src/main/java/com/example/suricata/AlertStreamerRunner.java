package com.example.suricata;

import gr.iccs.imu.ems.brokerclient.BrokerClient;
import gr.iccs.imu.ems.brokerclient.event.EventMap;
import jakarta.jms.JMSException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.nio.file.Path;

@Slf4j
@Component
@RequiredArgsConstructor
public class AlertStreamerRunner implements CommandLineRunner {

    private final ApplicationProperties properties;

    @Override
    public void run(String... args) throws JMSException, IOException {
        Path evePath = Path.of(properties.getEveFilePath());
        log.info("Tailing eve.json at: {}", evePath);

        boolean initialized = false;
        while (true) {
            try {
                // Start EMS BrokerClient and connect
                initialized = false;
                BrokerClient brokerclient = BrokerClient.newClient();
                brokerclient.openConnection(
                        properties.getAmqConnectionString(),
                        properties.getAmqUsername(),
                        properties.getAmqPassword(),
                        true);
                initialized = true;

                SuricataAlertStream.fromFile(evePath)
                        .doOnNext(alert -> {
                            //log.info("[ALERT]: {}", alert);
                            EventMap event = new EventMap(0, 0, 0);
                            event.put("ts", alert.timestamp());
                            event.put("srcIp", alert.srcIp());
                            event.put("srcPort", alert.srcPort());
                            event.put("destIp", alert.destIp());
                            event.put("destPort", alert.destPort());
                            event.put("proto", alert.proto());
                            event.put("signature", alert.signature());
                            event.put("signatureId", alert.signatureId());
                            event.put("severity", alert.severity());
                            try {
                                brokerclient.publishEvent(null, properties.getAmqAlertsTopic(), event);
                                //log.info("Published event: {}", event);
                            } catch (JMSException e) {
                                log.error("Failed to publish event: {}\n", event, e);
                            }
                        })
                        .doOnError(err -> log.error("[Error]: {}", err.getMessage()))
                        .subscribe();

                // Keep JVM alive in CLI mode
                Mono.never().block();

            } catch (Exception e) {
                log.error("Exception caught: {}", e.getMessage(), e);
                if (initialized) {
                    log.error("Restarting everything");
                } else {
                    int delay = 10;
                    log.error("EMS not ready. Waiting for {}s", delay);
                    try {
                        Thread.sleep(1000 * delay);
                    } catch (InterruptedException ignored) {}
                }
            }
        }
    }
}
