#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
if [ -f "$MODDIR/pending_boot" ]; then echo 'SKIPPED: previous modified boot was not confirmed.' > "$MODDIR/status.txt"; : > "$MODDIR/disable"; exit 0; fi
if ! prepare_themes > "$MODDIR/status.txt" 2>&1; then echo 'SKIPPED: original native resources kept.' >> "$MODDIR/status.txt"; exit 0; fi
: > "$MODDIR/pending_boot"
if mount -o bind "$MODDIR/generated" "$THEME_TARGET" 2>> "$MODDIR/status.txt"; then
 echo 'MOUNTED: additive OEM template catalogue and assets; waiting for boot verification.' >> "$MODDIR/status.txt"
else
 rm -f "$MODDIR/pending_boot"
 echo 'SKIPPED: theme resource mount failed; original native resources kept.' >> "$MODDIR/status.txt"
fi
