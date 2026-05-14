package com.example.suricata;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.nio.file.Path;

@Slf4j
@Service
@RequiredArgsConstructor
public class AlertService {
    private final ApplicationProperties applicationProperties;

    public Flux<SuricataAlert> streamAlerts() {
        Path evePath = Path.of(applicationProperties.getEveFilePath());
        return SuricataAlertStream.fromFile(evePath)
                .doOnNext(alert -> log.info("ALERT: {}", alert));
    }
}
