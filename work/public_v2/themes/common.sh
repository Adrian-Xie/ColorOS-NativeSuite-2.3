#!/system/bin/sh
THEME_TARGET=/my_product/decouping_wallpaper/inspiration_theme_resource/inspiration_theme_templates
prepare_themes() {
 [ -f "$THEME_TARGET/inspiration_theme_templates.json" ] || { echo 'SKIPPED: native template directory not found.'; return 2; }
 while read -r HASH REL; do
  SUM=$(sha256sum "$MODDIR/$REL")
  [ "${SUM%% *}" = "$HASH" ] || { echo "SKIPPED: resource integrity failed: $REL"; return 2; }
 done < "$MODDIR/payloads.sha256"
 [ -s "$MODDIR/wallpapers-apk.txt" ] || return 2
 IFS= read -r APK < "$MODDIR/wallpapers-apk.txt"
 case "$APK" in /product/*/Wallpapers/*.apk|/system/*/Wallpapers/*.apk|/my_product/*/Wallpapers/*.apk|/system_ext/*/Wallpapers/*.apk|/data/app/*.apk) ;; *) echo 'SKIPPED: unexpected native APK path.'; return 2 ;; esac
 [ -f "$APK" ] || { echo 'SKIPPED: native APK moved after update; reinstall the suite to recheck.'; return 2; }
 CLASSPATH="$MODDIR/theme-helper.dex" app_process /system/bin ThemeSetup "$THEME_TARGET" "$MODDIR/payload" "$MODDIR/generated" "$APK" || return 2
 chown -R 0:0 "$MODDIR/generated" && chmod -R u=rwX,go=rX "$MODDIR/generated" && chcon -R u:object_r:system_file:s0 "$MODDIR/generated" || return 2
}
