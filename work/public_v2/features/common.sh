#!/system/bin/sh
PATCH_ERROR=
for BB in /data/adb/ksu/bin/busybox /data/adb/magisk/busybox /data/adb/ap/bin/busybox; do [ ! -x "$BB" ] || break; done
awk() { "$BB" awk "$@"; }
generate_files() {
  mkdir -p "$MODDIR/generated" || return 1
  : > "$MODDIR/files.tsv.new"
  COUNT_APP=0; COUNT_OPLUS=0; SEEN='|'
  for BASE in /my_product /product /system/product /my_stock /my_region /system_ext /system; do
    for NAME in com.oplus.app-features.xml com.oplus.oplus-feature.xml; do
      TARGET="$BASE/etc/extension/$NAME"
      [ -f "$TARGET" ] || continue
      REAL=$(readlink -f "$TARGET") || return 1
      case "$SEEN" in *"|$REAL|"*) continue ;; esac
      SEEN="$SEEN$REAL|"
      if [ "$NAME" = com.oplus.app-features.xml ]; then
        KIND=app; PRIMARY=0; [ "$COUNT_APP" -ne 0 ] || PRIMARY=1
        COUNT_APP=$((COUNT_APP+1))
      else
        KIND=oplus; PRIMARY=0; [ "$COUNT_OPLUS" -ne 0 ] || PRIMARY=1
        COUNT_OPLUS=$((COUNT_OPLUS+1))
      fi
      REL=${TARGET#/}; DEST="$MODDIR/generated/$REL"
      mkdir -p "${DEST%/*}" || return 1
      awk -v kind="$KIND" -v primary="$PRIMARY" -f "$MODDIR/patch_features.awk" "$TARGET" > "$DEST.new" || {
        PATCH_ERROR="Unsupported XML structure: $TARGET"; return 1;
      }
      [ -s "$DEST.new" ] || return 1
      mv -f "$DEST.new" "$DEST" || return 1
      A=$(sha256sum "$TARGET"); B=$(sha256sum "$DEST")
      printf '%s\t%s\t%s\n' "$REL" "${A%% *}" "${B%% *}" >> "$MODDIR/files.tsv.new"
    done
  done
  [ "$COUNT_APP" -gt 0 ] && [ "$COUNT_OPLUS" -gt 0 ] || {
    PATCH_ERROR='Required ColorOS feature XML files were not found'; return 1;
  }
  mv -f "$MODDIR/files.tsv.new" "$MODDIR/files.tsv"
}
