# CONFIG.MD — stapel-mailtrap

Config registry for **stapel-mailtrap** (`static-scaffold-and-config.md` §2).
One row per configuration key the module reads, its **source** (`env` = the
process environment / the `STAPEL_MAILTRAP` settings dict), what it is for,
whether it is required, and its default.

Every key is read through `mailtrap_settings`
(`stapel_mailtrap.conf.AppSettings`, namespace `STAPEL_MAILTRAP`). Resolution
order per key: `settings.STAPEL_MAILTRAP` dict → a flat Django setting of the
same name → environment variable → the default below.

## stapel-mailtrap

| Key | Source | Purpose | Required | Default |
|-----|--------|---------|----------|---------|
| SCOPE_PROVIDER | env | dotted path to a ScopeProvider — the multi-tenant seam (REPLACE). Default is a single global scope. | no | stapel_mailtrap.scope.DefaultScopeProvider |
| MAX_EMAILS | env | retention: hard cap on stored messages; the sweep deletes the oldest beyond this. 0 disables. | no | 1000 |
| TTL_DAYS | env | retention: delete messages older than this many days. 0 disables. | no | 30 |
| STORE_BODY | env | store rendered HTML/text bodies on the row (False keeps only the envelope). | no | true |
