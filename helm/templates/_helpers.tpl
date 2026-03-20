{{/*
Expand the name of the chart.
*/}}
{{- define "redmine-mcp.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "redmine-mcp.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "redmine-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "redmine-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "redmine-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Name of the secret containing Redmine credentials
*/}}
{{- define "redmine-mcp.secretName" -}}
{{- if .Values.redmine.existingSecret -}}
{{ .Values.redmine.existingSecret }}
{{- else -}}
{{ include "redmine-mcp.name" . }}-credentials
{{- end }}
{{- end }}
