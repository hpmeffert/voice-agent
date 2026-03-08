# Transcript Templates (V7.4.0)

Default export templates:
- `exports/transcript_default.md.tpl`
- `exports/transcript_default.json.schema.json`

Legacy compatibility path:
- `transcript_default.md.tpl`

Supported placeholders:
- `{{date}}`
- `{{weekday}}`
- `{{start_time}}`
- `{{end_time}}`
- `{{user_id}}`
- `{{session_id}}`
- `{{backend}}`
- `{{model}}`
- `{{lang}}`
- `{{messages}}`

Message block format is rendered by API and injected into `{{messages}}`.

## Customization
- Preferred location for CRM export templates:
  - `v7/templates/exports/`
- API default:
  - `/app/templates/exports/transcript_default.md.tpl`
