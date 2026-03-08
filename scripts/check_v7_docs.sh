#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "[DOC-CHECK][FAIL] $1" >&2
  exit 1
}

must_contain() {
  local file="$1"
  local pattern="$2"
  local msg="$3"
  if ! rg -q "$pattern" "$file"; then
    fail "$msg ($file, pattern: $pattern)"
  fi
}

# Required files
for f in \
  v7/web/index.html \
  v7/docs/ui/HELP_USER.md \
  v7/docs/ui/DEMO_GUIDE.md \
  v7/docs/admin/HELP_ADMIN.md \
  v7/docs/RELEASE.md \
  v7/docs/DOCUMENTATION_RULES.md; do
  [[ -f "$f" ]] || fail "Missing required file: $f"
done

# Help menu structure in UI
must_contain v7/web/index.html 'Admin Token speichern' 'Help menu: missing admin token menu item text'
must_contain v7/web/index.html 'data-help-doc="/docs/ui/HELP_USER.md"' 'Help menu: Help must point to user docs'
must_contain v7/web/index.html 'data-help-doc="/docs/ui/DEMO_GUIDE.md"' 'Help menu: Demo Guide missing'
must_contain v7/web/index.html 'data-help-endpoint="/api/admin/docs/help"' 'Help menu: Admin Docs endpoint missing'
must_contain v7/web/index.html 'data-help-doc="/docs/RELEASE.md"' 'Help menu: Release Notes link missing'

# Silence threshold defaults
must_contain v7/web/index.html 'id="silenceMs"[^\n]*value="1300"' 'Silence threshold default in UI must be 1300ms'
must_contain v7/web/index.html '\|\| 1300' 'Silence threshold fallback in UI must be 1300ms'
must_contain v7/docker/api/app.py 'LISTEN_SILENCE_MS_DEFAULT.*"1300"' 'API default silence threshold must be 1300ms'

# Content quality checks
must_contain v7/docs/ui/HELP_USER.md 'Benutzer Dokumentation' 'User help title missing/incorrect'
must_contain v7/docs/ui/HELP_USER.md 'Einstellungen fuer Gespraechsfluss' 'User help must explain settings and effects'
must_contain v7/docs/ui/DEMO_GUIDE.md 'Stellen Sie sich' 'Demo guide must include story-language hook'
must_contain v7/docs/admin/HELP_ADMIN.md 'Installation und Start' 'Admin docs must include installation/start'
must_contain v7/docs/admin/HELP_ADMIN.md 'Empfohlene Admin-Tests' 'Admin docs must include test guidance'

# Release notes coverage: must include timeline from v7.0.0 to latest release note file
must_contain v7/docs/RELEASE.md 'V7\.0\.0' 'Release overview must include v7.0.0'
latest_release="$(ls v7/docs/RELEASE_NOTES_v*.md 2>/dev/null | sed -E 's#.*(v[0-9]+\.[0-9]+\.[0-9]+)\.md#\1#' | sort -V | tail -1)"
[[ -n "$latest_release" ]] || fail 'No RELEASE_NOTES_v*.md files found in v7/docs'
must_contain v7/docs/RELEASE.md "$latest_release" "Release overview must include latest release $latest_release"

# Maintenance rule present
must_contain v7/docs/RELEASE.md 'Pflege-Regel' 'Release overview must contain maintenance rule'
must_contain v7/docs/DOCUMENTATION_RULES.md 'Pflicht bei JEDEM Release' 'Documentation rules must enforce per-release updates'

echo '[DOC-CHECK][OK] V7 documentation and help-menu checks passed.'
