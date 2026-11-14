#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
N=0
while [ "$(getprop sys.boot_completed)" != 1 ]; do
  [ "$N" -lt 300 ] || exit 1; sleep 5; N=$((N+5))
done
while read -r REL ORIGINAL PATCHED; do
  SUM=$(sha256sum "/$REL")
  [ "${SUM%% *}" = "$PATCHED" ] || { printf 'CONFLICT: %s\n' "$REL" >> "$MODDIR/status.txt"; exit 1; }
done < "$MODDIR/files.tsv"
rm -f "$MODDIR/pending_boot"
printf '%s\n' 'Boot complete; feature mounts verified.' >> "$MODDIR/status.txt"
