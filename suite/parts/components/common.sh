#!/system/bin/sh
CHECK_ERROR=
validate_payloads() {
  while read -r PKG VER HASH REL EXTRA; do
    [ -n "$PKG" ] || continue
    [ -z "$EXTRA" ] && [ "$REL" = "system/product/app/$PKG/$PKG.apk" ] || return 1
    SUM=$(sha256sum "$MODDIR/$REL") || return 1
    [ "${SUM%% *}" = "$HASH" ] || return 1
  done < "$MODDIR/apks.tsv"
  while read -r PKG HASH REL EXTRA; do
    SUM=$(sha256sum "$MODDIR/$REL") || return 1
    [ "${SUM%% *}" = "$HASH" ] || return 1
  done < "$MODDIR/native-libs.tsv"
}
verify_mounts() {
  while read -r PKG VER HASH REL EXTRA; do
    TARGET="/product/app/$PKG/$PKG.apk"
    SUM=$(sha256sum "$TARGET") || return 1
    [ "${SUM%% *}" = "$HASH" ] || return 1
  done < "$MODDIR/selected.tsv"
}
