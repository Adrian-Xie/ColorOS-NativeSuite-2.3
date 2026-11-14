#!/system/bin/sh
SUITE_DIR=${SUITE_DIR:-${0%/*}}
DB=/data/adb/lspd/config/modules_config.db
[ -f "$DB" ] || { echo 'LSPosed database not ready; setup will run after first boot.'; exit 3; }
APK=$(pm path cn.local.plt120.recentsfix 2>/dev/null)
APK=${APK#package:}
case "$APK" in /data/app/*.apk) ;; *) echo 'Repair APK is not installed in owner user.'; exit 2 ;; esac
CLASSPATH="$SUITE_DIR/payload/scope-helper.dex" app_process /system/bin ScopeSetup enable "$DB" "$APK" || exit 2
printf '%s\n' 'Own module enabled for com.android.launcher, user 0. Reboot required.' > "$SUITE_DIR/hook-setup.txt"
