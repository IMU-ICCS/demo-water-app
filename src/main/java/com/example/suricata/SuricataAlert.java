package com.example.suricata;

public record SuricataAlert(
        String timestamp,
        String srcIp,
        Integer srcPort,
        String destIp,
        Integer destPort,
        String proto,
        String signature,
        Long signatureId,
        Integer severity
) {}
