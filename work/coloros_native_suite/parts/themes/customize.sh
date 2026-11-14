#!/system/bin/sh
MODDIR=$MODPATH
APK=$(pm path com.oplus.wallpapers 2>/dev/null)
APK=${APK#package:}
case "$APK" in *'
'*|'') ui_print 'OEM template resources skipped: native wallpaper/theme editor not resolved.'; : > "$MODDIR/disable"; exit 0 ;; esac
printf '%s\n' "$APK" > "$MODDIR/wallpapers-apk.txt"
. "$MODDIR/common.sh"
for PKG in com.oplus.keyguard.clock.base com.oplus.keyguard.clock.magazine com.oplus.keyguard.clock.gallery com.oplus.keyguard.clock.graffiti; do
 pm path "$PKG" >/dev/null 2>&1 || { ui_print "OEM theme resources skipped: missing native clock $PKG"; : > "$MODDIR/disable"; exit 0; }
done
if prepare_themes > "$MODDIR/prepare-log.txt" 2>&1; then
 ui_print 'Additional OEM inspiration template resources prepared for native editor.'
else
 ui_print 'OEM template resources incompatible; see parts/themes/prepare-log.txt. Other suite features remain available.'
 : > "$MODDIR/disable"
fi
