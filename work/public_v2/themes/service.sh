#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
N=0
while [ "$(getprop sys.boot_completed)" != 1 ] && [ "$N" -lt 180 ]; do sleep 2; N=$((N+1)); done
if [ "$(getprop sys.boot_completed)" = 1 ] && [ -f "$MODDIR/pending_boot" ]; then
 if cmp -s "$MODDIR/generated/inspiration_theme_templates.json" "$THEME_TARGET/inspiration_theme_templates.json"; then
  rm -f "$MODDIR/pending_boot"; echo 'Boot complete; OEM template catalogue mount verified. Editor workflow is a separate acceptance check.' >> "$MODDIR/status.txt"
 else echo 'WARNING: theme catalogue mount not visible.' >> "$MODDIR/status.txt"; fi
fi
