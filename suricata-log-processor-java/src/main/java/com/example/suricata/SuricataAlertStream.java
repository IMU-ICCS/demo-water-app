package com.example.suricata;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.nio.file.Path;

@Slf4j
public class SuricataAlertStream {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static Flux<SuricataAlert> fromFile(Path evePath) {
        return ReactiveFileTailer.tail(evePath)
                //.filter(line -> line.contains("\"event_type\":\"alert\""))
                //.map(SuricataAlertStream::parseAlert);
        // ---OR---
                //.log("raw-lines") // logs raw eve.json lines
                .flatMap(line -> Mono.justOrEmpty(parseAlert(line)))
                //.log("parsed-alerts") // logs SuricataAlert objects
                ;
    }

    private static SuricataAlert parseAlert(String line) {
        try {
            JsonNode root = mapper.readTree(line);

            if (!"alert".equals(root.path("event_type").asText())) {
                return null;
            }

            JsonNode alertNode = root.path("alert");

            return new SuricataAlert(
                    root.path("timestamp").asText(),
                    root.path("src_ip").asText(),
                    root.path("src_port").isMissingNode() ? null : root.path("src_port").asInt(),
                    root.path("dest_ip").asText(),
                    root.path("dest_port").isMissingNode() ? null : root.path("dest_port").asInt(),
                    root.path("proto").asText(),
                    alertNode.path("signature").asText(),
                    alertNode.path("signature_id").asLong(),
                    alertNode.path("severity").asInt()
            );
        } catch (Exception ignored) {
            return null;
        }
    }
}
