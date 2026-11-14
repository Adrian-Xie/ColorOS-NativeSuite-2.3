#!/system/bin/sh
[ "${BOOTMODE:-}" = true ] || abort 'Install from the running root manager.'
MODDIR="$MODPATH"
. "$MODDIR/common.sh"
validate_payloads || abort 'Original APK/library payload failed integrity verification.'
grep -q overlay /proc/filesystems || abort 'OverlayFS kernel support is required for standalone mounting.'
case "$(getprop ro.product.cpu.abilist)" in *arm64-v8a*) ;; *) abort 'Bundled native code requires arm64-v8a.' ;; esac
[ "$(getconf PAGESIZE 2>/dev/null)" = 4096 ] || abort 'Original native libraries need matching 16K-compatible replacements on a 16K kernel.'
pm path android >/dev/null 2>&1 || abort 'PackageManager is unavailable.'
: > "$MODDIR/selected.tsv"; : > "$MODDIR/selection.txt"
for D in /data/adb/modules/ColorOSCommonFeatureSupplements-AppExtension /data/adb/modules_update/ColorOSCommonFeatureSupplements-AppExtension; do
  [ ! -d "$D" ] || abort 'Remove the broad original application extension and reboot first.'
done
while read -r PKG VER HASH REL EXTRA; do
  if [ "$PKG" = com.coloros.accessibilityassistant ] && [ "$(getprop ro.build.version.sdk)" -lt 35 ]; then
    printf 'SKIP minSdk35: %s\n' "$PKG" >> "$MODDIR/selection.txt"; continue
  fi
  EXISTING=$(pm path "$PKG" 2>/dev/null)
  if [ -n "$EXISTING" ]; then
    # Permit updating this same module, but preserve any other installed version.
    P=${EXISTING#package:}; SUM=$(sha256sum "$P" 2>/dev/null)
    case "$P" in /product/app/"$PKG"/"$PKG".apk|/system/product/app/"$PKG"/"$PKG".apk)
      if [ "${SUM%% *}" = "$HASH" ]; then :; else
        printf 'SKIP existing: %s\n' "$PKG" >> "$MODDIR/selection.txt"; continue
      fi ;;
    *) printf 'SKIP existing: %s\n' "$PKG" >> "$MODDIR/selection.txt"; continue ;;
    esac
  fi
  printf '%s\t%s\t%s\t%s\n' "$PKG" "$VER" "$HASH" "$REL" >> "$MODDIR/selected.tsv"
  printf 'ADD missing: %s\n' "$PKG" >> "$MODDIR/selection.txt"
done < "$MODDIR/apks.tsv"
set_perm_recursive "$MODPATH" 0 0 0755 0644
for F in common.sh post-fs-data.sh service.sh action.sh; do set_perm "$MODPATH/$F" 0 0 0755; done
ui_print 'No model/firmware/ColorOS-version lock. No external metamodule dependency.'
cat "$MODDIR/selection.txt"
ui_print 'Standalone tmpfs/OverlayFS mounting adds RAM use for selected payload files.'
ui_print 'Reboot manually. Component registration and actual AI/order workflows are separate checks.'
