#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
fail() { printf 'DISABLED: %s\n' "$1" > "$MODDIR/status.txt"; : > "$MODDIR/disable"; exit 1; }
[ ! -f "$MODDIR/pending_boot" ] || fail 'Previous modified boot was not confirmed complete.'
generate_files || fail "${PATCH_ERROR:-Cannot generate current-device XML}"
: > "$MODDIR/pending_boot"
: > "$MODDIR/mount-errors.txt"
MOUNTED=
rollback() { for T in $MOUNTED; do umount "$T" 2>>"$MODDIR/mount-errors.txt" || umount -l "$T" 2>>"$MODDIR/mount-errors.txt"; done; }
while read -r REL ORIGINAL PATCHED; do
  FILE="$MODDIR/generated/$REL"
  chown 0:0 "$FILE" && chmod 0644 "$FILE" && chcon u:object_r:system_file:s0 "$FILE" || { rollback; fail 'Cannot label generated XML'; }
  mount -o bind "$FILE" "/$REL" 2>>"$MODDIR/mount-errors.txt" || { rollback; fail "Mount failed: $REL"; }
  MOUNTED="/$REL $MOUNTED"
  SUM=$(sha256sum "/$REL")
  [ "${SUM%% *}" = "$PATCHED" ] || { rollback; fail "Mounted hash mismatch: $REL"; }
done < "$MODDIR/files.tsv"
printf '%s\n' 'ACTIVE: adaptive feature XML mounted; individual UI results require verification.' > "$MODDIR/status.txt"
