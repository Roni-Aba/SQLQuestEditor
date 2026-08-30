#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 ]]; then
  printf 'Verwendung: %s <kategorie> "<kurze Aktion>" [--duration-ms <ms>] [--tokens-estimated <anzahl>]\n' "$0" >&2
  exit 1
fi

category="$1"
action="$2"
shift 2
duration="nicht verfügbar"
token_usage="nicht verfügbar"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(dirname "$script_dir")"
log_file="$project_root/log.md"

case "$category" in
  analyse|tool|entscheidung|implementierung|validierung|sichtpruefung) ;;
  *)
    printf 'Ungültige Kategorie: %s\n' "$category" >&2
    exit 1
    ;;
esac

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration-ms)
      if [[ $# -lt 2 || ! "$2" =~ ^[0-9]+$ ]]; then
        printf 'Der Wert für --duration-ms muss eine ganze Millisekundenanzahl sein.\n' >&2
        exit 1
      fi
      duration="$2 ms"
      shift 2
      ;;
    --tokens-estimated)
      if [[ $# -lt 2 || ! "$2" =~ ^[0-9]+$ ]]; then
        printf 'Der Wert für --tokens-estimated muss eine ganze Tokenanzahl sein.\n' >&2
        exit 1
      fi
      token_usage="ca. $2 (sichtbare Nutzlast)"
      shift 2
      ;;
    *)
      printf 'Unbekannte Option: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

escape_table_cell() {
  printf '%s' "$1" | tr '\n' ' ' | sed 's/|/\\|/g'
}

if [[ ! -f "$log_file" ]]; then
  {
    printf '# Arbeitslog\n\n'
    printf '| Nr. | Kategorie | Aktion | Timestamp | Dauer | Tokenverbrauch (sichtbar, geschätzt) |\n'
    printf '| ---: | --- | --- | --- | ---: | --- |\n'
  } > "$log_file"
fi

next_number="$(
  awk -F'|' '
    $2 ~ /^[[:space:]]*[0-9]+[[:space:]]*$/ {
      number = $2
      gsub(/[[:space:]]/, "", number)
      number += 0
      if (number > maximum) {
        maximum = number
      }
    }
    END {
      print maximum + 1
    }
  ' "$log_file"
)"

timestamp="$(date '+%Y-%m-%dT%H:%M:%S%z')"
formatted_category="$(escape_table_cell "$category")"
formatted_action="$(escape_table_cell "$action")"
formatted_duration="$(escape_table_cell "$duration")"
formatted_token_usage="$(escape_table_cell "$token_usage")"
log_row="$(printf '| %s | %s | %s | `%s` | %s | %s |' \
  "$next_number" \
  "$formatted_category" \
  "$formatted_action" \
  "$timestamp" \
  "$formatted_duration" \
  "$formatted_token_usage")"
temporary_log="$(mktemp "$log_file.XXXXXX")"

awk -v row="$log_row" '
  /^## Ergebnis$/ && !inserted {
    print row
    print ""
    inserted = 1
  }
  {
    print
  }
  END {
    if (!inserted) {
      print row
    }
  }
' "$log_file" > "$temporary_log"

mv "$temporary_log" "$log_file"
