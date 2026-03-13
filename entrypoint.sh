#!/bin/sh
set -eu

LOOP_ENABLED="${LOOP_ENABLED:-false}"
ALIGN_TO_HOUR="${ALIGN_TO_HOUR:-true}"
RUN_IMMEDIATELY="${RUN_IMMEDIATELY:-false}"

normalize_bool() {
  value="$(printf "%s" "$1" | tr '[:upper:]' '[:lower:]')"
  case "$value" in
    1|true|yes|on) echo "true" ;;
    *) echo "false" ;;
  esac
}

LOOP_ENABLED="$(normalize_bool "$LOOP_ENABLED")"
ALIGN_TO_HOUR="$(normalize_bool "$ALIGN_TO_HOUR")"
RUN_IMMEDIATELY="$(normalize_bool "$RUN_IMMEDIATELY")"

run_once() {
  echo "[entrypoint] Menjalankan VPS Pulse..."
  python -m app.main
}

sleep_until_next_hour() {
  now="$(date +%s)"
  next_hour=$(( (now / 3600 + 1) * 3600 ))
  sleep_seconds=$(( next_hour - now ))
  echo "[entrypoint] Sleep ${sleep_seconds}s sampai jam berikutnya ($(date -u -d "@$next_hour" '+%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || echo "$next_hour"))."
  sleep "$sleep_seconds"
}

if [ "$LOOP_ENABLED" = "true" ]; then
  echo "[entrypoint] Loop mode aktif."

  if [ "$RUN_IMMEDIATELY" = "true" ]; then
    run_once || echo "[entrypoint] app.main exit non-zero."
  fi

  while true; do
    if [ "$ALIGN_TO_HOUR" = "true" ]; then
      sleep_until_next_hour
    else
      echo "[entrypoint] ALIGN_TO_HOUR=false, fallback sleep 3600s."
      sleep 3600
    fi

    run_once || echo "[entrypoint] app.main exit non-zero."
  done
else
  echo "[entrypoint] Loop mode nonaktif. Menjalankan sekali lalu exit."
  run_once
fi
