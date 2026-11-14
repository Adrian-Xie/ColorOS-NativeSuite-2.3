#!/system/bin/sh
[ "${BOOTMODE:-}" = true ] || abort 'Install from the running root manager.'
SUITE_DIR=$MODPATH
ui_print 'ColorOS native suite: OEM APKs + device-local configuration + native-view repair Hook.'
ui_print 'The Hook needs Zygisk/LSPosed. Bundled pinned framework installers run only if missing.'
ui_print 'The rejected volume resize and control-panel Hook are removed. Control-center secondary panels remain unimplemented.'
while read -r HASH REL; do
  SUM=$(sha256sum "$SUITE_DIR/$REL")
  [ "${SUM%% *}" = "$HASH" ] || abort "Suite payload integrity failed: $REL"
done < "$SUITE_DIR/payloads.sha256"
(
 MODPATH="$SUITE_DIR/parts/features"
 . "$MODPATH/customize.sh"
) || abort 'Device-local feature preparation failed.'
(
 MODPATH="$SUITE_DIR/parts/components"
 . "$MODPATH/customize.sh"
) || abort 'OEM component selection failed.'
(
 MODPATH="$SUITE_DIR/parts/themes"
 . "$MODPATH/customize.sh"
) || abort 'OEM template preparation failed.'
# Keep root-manager-owned files/scripts and mount implementation separate from framework installers.
set_perm_recursive "$SUITE_DIR" 0 0 0755 0644
for F in customize.sh post-fs-data.sh service.sh action.sh uninstall.sh setup-hook.sh; do set_perm "$SUITE_DIR/$F" 0 0 0755; done
for P in features components themes; do
 for F in common.sh post-fs-data.sh service.sh action.sh; do set_perm "$SUITE_DIR/parts/$P/$F" 0 0 0755; done
done
# Native PackageManager performs the signature/version checks. No permission/privacy auto-acceptance.
# PackageManager cannot read /data/adb. Give it a separately labeled temporary copy.
APK_STAGE=/data/local/tmp/coloros-native-suite-install-$$.apk
cp "$SUITE_DIR/payload/native-repairs.apk" "$APK_STAGE" || abort 'Cannot stage repair APK.'
chmod 0644 "$APK_STAGE"
chcon u:object_r:shell_data_file:s0 "$APK_STAGE" || { rm -f "$APK_STAGE"; abort 'Cannot label repair APK.'; }
# cmd package forwards stdout to system_server: keep its descriptor a pipe rather
# than a root-private /data/adb log file, which SELinux denies to system_server.
INSTALL_RESULT=$(pm install -r --user 0 "$APK_STAGE" 2>&1)
INSTALL_CODE=$?
printf '%s\n' "$INSTALL_RESULT" > "$SUITE_DIR/hook-install.txt"
rm -f "$APK_STAGE"
[ "$INSTALL_CODE" = 0 ] || { cat "$SUITE_DIR/hook-install.txt"; abort 'Repair APK install failed.'; }
grep -q Success "$SUITE_DIR/hook-install.txt" || abort 'Repair APK installation was not confirmed.'
if [ -n "${KSU:-}" ]; then
 KSUD=/data/adb/ksu/bin/ksud
 [ -x "$KSUD" ] || abort 'KernelSU module installer is unavailable.'
 for ITEM in 'zygisksu:Zygisk-Next-1.5.3-880-22a1bf5-release.zip' 'zygisk_lsposed:LSPosed-v2.0.0-7316-Irena-release.zip'; do
  ID=${ITEM%%:*}; ZIP=${ITEM#*:}
  for BASE in /data/adb/modules /data/adb/modules_update; do
   [ ! -e "$BASE/$ID/disable" ] || abort "Existing $ID is disabled. Enable it in your root manager and reboot before installing the suite."
   [ ! -e "$BASE/$ID/remove" ] || abort "Existing $ID is pending removal. Finish removal or cancel it before installing the suite."
  done
  if [ -f "/data/adb/modules/$ID/module.prop" ] || [ -f "/data/adb/modules_update/$ID/module.prop" ]; then
   ui_print "Keep existing framework: $ID"
  else
   ui_print "Installing included official framework: $ID"
   "$KSUD" module install "$SUITE_DIR/dependencies/$ZIP" > "$SUITE_DIR/$ID-install.txt" 2>&1 || { cat "$SUITE_DIR/$ID-install.txt"; abort "Official $ID installer refused."; }
   : > "$SUITE_DIR/framework_first_install"
  fi
 done
else
 [ -f /data/adb/modules/zygisk_lsposed/module.prop ] || abort 'This non-KernelSU installation needs an existing compatible Zygisk/LSPosed framework.'
fi
if [ -f /data/adb/lspd/config/modules_config.db ]; then
 SUITE_DIR="$SUITE_DIR" sh "$SUITE_DIR/setup-hook.sh" > "$SUITE_DIR/hook-setup.log" 2>&1 || { cat "$SUITE_DIR/hook-setup.log"; abort 'Hook setup could not be confirmed.'; }
else
 ui_print 'First framework installation: after the first boot, Action will show whether a second reboot is needed.'
fi
# Migrate only the previous companion from this task; never touch unrelated modules.
for OLD in /data/adb/modules/plt120_components /data/adb/modules_update/plt120_components; do
 if [ -f "$OLD/module.prop" ] && grep -q '^id=plt120_components$' "$OLD/module.prop"; then
  : > "$OLD/disable"; ui_print 'Previous companion disabled automatically; its payload is included here.'
 fi
done
ui_print 'Installation complete. Reboot manually to apply.'
ui_print 'AI privacy/login, weather city and real-order cloud eligibility still require the owner.'
