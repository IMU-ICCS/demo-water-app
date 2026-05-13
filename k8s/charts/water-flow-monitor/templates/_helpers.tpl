{{- define "water-flow-monitor.name" -}}
water-flow-monitor
{{- end }}

{{- define "water-flow-monitor.fullname" -}}
{{ .Release.Name }}-{{ include "water-flow-monitor.name" . }}
{{- end }}

{{- define "water-flow-monitor.labels" -}}
app.kubernetes.io/name: {{ include "water-flow-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
