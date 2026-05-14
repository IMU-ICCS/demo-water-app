package com.example.suricata;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Slf4j
@Data
@Configuration
@ConfigurationProperties(prefix = "suricata")
public class ApplicationProperties implements InitializingBean {
    private String eveFilePath;
    private String amqConnectionString;
    private String amqUsername;
    private String amqPassword;
    private String amqAlertsTopic = "alerts";

    @Override
    public void afterPropertiesSet() {
        log.info("Properties: {}", this);
    }
}
