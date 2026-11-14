#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
fail() { printf 'DISABLED: %s\n' "$1" >> "$MODDIR/status.txt"; : > "$MODDIR/disable"; exit 1; }
: > "$MODDIR/status.txt"
[ ! -f "$MODDIR/pending_boot" ] || fail 'Previous modified boot was not confirmed complete.'
[ -s "$MODDIR/selected.tsv" ] || { echo 'No missing components selected.' > "$MODDIR/status.txt"; exit 0; }
validate_payloads || fail 'Payload integrity failed.'
: > "$MODDIR/pending_boot"
STAGE=/mnt/vendor/coloros_components_local
[ ! -e "$STAGE" ] || fail 'Mount staging directory already exists.'
mkdir -p "$STAGE" || fail 'Cannot create staging directory.'
mount -t tmpfs -o mode=0755 tmpfs "$STAGE" || fail 'Cannot mount staging tmpfs.'
cleanup() { umount -l "$STAGE" 2>/dev/null; }
mkdir -p "$STAGE/app" || { cleanup; fail 'Cannot create app staging.'; }
chcon u:object_r:system_file:s0 "$STAGE" "$STAGE/app" || { cleanup; fail 'Cannot label staging.'; }
while read -r PKG VER HASH REL EXTRA; do
  SOURCE="$MODDIR/system/product/app/$PKG"
  [ -d "$SOURCE" ] || SOURCE="$MODDIR/product/app/$PKG"
  cp -R "$SOURCE" "$STAGE/app/$PKG" || { cleanup; fail "Cannot stage $PKG"; }
done < "$MODDIR/selected.tsv"
chown -R 0:0 "$STAGE/app" && chmod -R u=rwX,go=rX "$STAGE/app" && chcon -R u:object_r:system_file:s0 "$STAGE/app" || {
  cleanup; fail 'Cannot set staged APK permissions or context.';
}
TARGET=$(readlink -f /product/app)
[ -d "$TARGET" ] || { cleanup; fail 'Product app scan directory is unavailable.'; }
# Same read-only lowerdir composition as the upstream Mountify standalone path.
# Only this module's selected apps are staged, and no existing app is replaced.
mount -t overlay -o "lowerdir=$STAGE/app:$TARGET" KSU "$TARGET" || { cleanup; fail 'Independent application overlay mount failed.'; }
if ! verify_mounts; then
  umount "$TARGET" || umount -l "$TARGET"
  cleanup; fail 'Mounted APK hashes do not match.'
fi
du -sk "$STAGE/app" >> "$MODDIR/status.txt"
cleanup
printf '%s\n' 'MOUNTED: selected original APKs; waiting for boot and PackageManager.' >> "$MODDIR/status.txt"
