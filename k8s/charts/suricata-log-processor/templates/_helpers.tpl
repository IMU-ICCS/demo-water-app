{{- define "suricata-log-processor.name" -}}
suricata-log-processor
{{- end }}

{{- define "suricata-log-processor.fullname" -}}
{{ .Release.Name }}-{{ include "suricata-log-processor.name" . }}
{{- end }}

{{- define "suricata-log-processor.labels" -}}
app.kubernetes.io/name: {{ include "suricata-log-processor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
