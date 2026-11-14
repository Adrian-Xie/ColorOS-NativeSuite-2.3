#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
[ -s "$MODDIR/selected.tsv" ] || exit 0
. "$MODDIR/common.sh"
N=0
while [ "$(getprop sys.boot_completed)" != 1 ]; do
  [ "$N" -lt 300 ] || exit 1; sleep 5; N=$((N+5))
done
verify_mounts || { echo 'CONFLICT: component mount changed.' >> "$MODDIR/status.txt"; exit 1; }
FAIL=0
while read -r PKG VER HASH REL EXTRA; do
  P=$(pm path "$PKG" 2>/dev/null)
  case "$P" in
    package:/product/app/"$PKG"/"$PKG".apk|package:/system/product/app/"$PKG"/"$PKG".apk)
      printf 'REGISTERED: %s\n' "$PKG" >> "$MODDIR/status.txt" ;;
    *) printf 'UNAVAILABLE OR EXISTING UPDATE: %s\n' "$PKG" >> "$MODDIR/status.txt"; FAIL=1 ;;
  esac
done < "$MODDIR/selected.tsv"
[ "$FAIL" = 0 ] || exit 1
rm -f "$MODDIR/pending_boot"
printf '%s\n' 'Boot complete and selected packages registered; UI/cloud availability depends on OEM support.' >> "$MODDIR/status.txt"
