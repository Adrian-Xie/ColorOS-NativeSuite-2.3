"""One flashable suite: device-local XML, OEM packages, native repair APK and pinned frameworks."""
from pathlib import Path
import shutil,zipfile,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'work/public_v2';DEST=ROOT/'work/coloros_native_suite';OUT=ROOT/'outputs/integrated'
DEST.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
def write(name,text):
 p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8',newline='\n')
for source,name in [('features','features'),('components','components'),('themes','themes')]:
 shutil.copytree(SRC/source,DEST/'parts'/name,dirs_exist_ok=True)
shutil.copy2(SRC/'patch_features.awk',DEST/'parts/features/patch_features.awk')
f=DEST/'parts/features/customize.sh';f.write_text(f.read_text(encoding='utf8').replace('Only the requested six feature edits are applied','Only the requested feature edits are applied'),encoding='utf8',newline='\n')
(DEST/'payload').mkdir(exist_ok=True)
shutil.copy2(ROOT/'outputs/public-test/ColorOS_RecentsRepair_0.4.apk',DEST/'payload/native-repairs.apk')
shutil.copy2(ROOT/'work/suite_research/scope-helper/classes.dex',DEST/'payload/scope-helper.dex')
deps=[('Zygisk-Next-1.5.3-880-22a1bf5-release.zip','zygisksu','186a0a26c9fcb895af1954b42de831433c23d72d1bd0758b986069154359db67'),('LSPosed-v2.0.0-7316-Irena-release.zip','zygisk_lsposed','1f843e0b5062666ce4d8e8eecbb8510497419175b3c3fd1898f885c7cae37cd1')]
(DEST/'dependencies').mkdir(exist_ok=True)
for name,module,digest in deps:
 p=ROOT/'work/v2_research/hook_versions'/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 shutil.copy2(p,DEST/'dependencies'/name)
write('module.prop','''id=plt120_selective_features
name=ColorOS 原生功能整合补全（测试版）
version=2.3-suite-test
versionCode=20300
author=Local customization; OEM APKs from user-supplied extension
description=原厂流体云配套、小布普通模式及建议卡片容器、堆叠与桌面卡片、主题资源和堆叠修复。一包安装，无固定机型/固件限制，无元模块依赖。云端AI及订单场景仍需原厂支持。
''')
write('skip_mount','');write('skip_mountify','')
write('setup-hook.sh',r'''#!/system/bin/sh
SUITE_DIR=${SUITE_DIR:-${0%/*}}
DB=/data/adb/lspd/config/modules_config.db
[ -f "$DB" ] || { echo 'LSPosed database not ready; setup will run after first boot.'; exit 3; }
APK=$(pm path cn.local.plt120.recentsfix 2>/dev/null)
APK=${APK#package:}
case "$APK" in /data/app/*.apk) ;; *) echo 'Repair APK is not installed in owner user.'; exit 2 ;; esac
CLASSPATH="$SUITE_DIR/payload/scope-helper.dex" app_process /system/bin ScopeSetup enable "$DB" "$APK" || exit 2
printf '%s\n' 'Own module enabled for com.android.launcher, user 0. Reboot required.' > "$SUITE_DIR/hook-setup.txt"
''')
write('customize.sh',r'''#!/system/bin/sh
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
''')
write('post-fs-data.sh',r'''#!/system/bin/sh
SUITE_DIR=${0%/*}
[ ! -e "$SUITE_DIR/disable" ] && [ ! -e "$SUITE_DIR/remove" ] || exit 0
: > "$SUITE_DIR/status.txt"
STATE=1
for P in features components themes; do
 sh "$SUITE_DIR/parts/$P/post-fs-data.sh" || { echo "FAILED: $P; see part status" >> "$SUITE_DIR/status.txt"; STATE=0; }
done
setprop sys.coloros_native_suite "$STATE"
''')
write('service.sh',r'''#!/system/bin/sh
SUITE_DIR=${0%/*}
[ ! -e "$SUITE_DIR/disable" ] && [ ! -e "$SUITE_DIR/remove" ] || exit 0
for P in features components themes; do sh "$SUITE_DIR/parts/$P/service.sh"; done
if [ ! -s "$SUITE_DIR/hook-setup.txt" ]; then
 if SUITE_DIR="$SUITE_DIR" sh "$SUITE_DIR/setup-hook.sh" > "$SUITE_DIR/hook-setup.log" 2>&1; then
  echo 'First framework setup finished. Reboot once more to load the Hook with its configured scope.' >> "$SUITE_DIR/status.txt"
 else echo 'HOOK NOT READY: inspect hook-setup.log or enable ColorOS native repair in LSPosed.' >> "$SUITE_DIR/status.txt"; fi
fi
''')
write('action.sh',r'''#!/system/bin/sh
SUITE_DIR=${0%/*}
for P in features components themes; do echo "[$P]"; cat "$SUITE_DIR/parts/$P/status.txt"; done
echo '[Hook]'; cat "$SUITE_DIR/hook-setup.txt"; cat "$SUITE_DIR/status.txt"
echo '[OEM fluid capability]'
content call --uri content://com.oplus.pantanal.ums.IntentProvider --method isFluidCloudSupport 2>&1
echo '[OEM AI components]'
for PKG in com.heytap.speechassist com.oplus.pantanal.ums com.oplus.metis com.coloros.sceneservice com.coloros.colordirectservice com.coloros.directui; do
 printf '%s: ' "$PKG"; pm path "$PKG" 2>/dev/null
done
''')
write('uninstall.sh',r'''#!/system/bin/sh
SUITE_DIR=${0%/*}
setprop sys.coloros_native_suite 0
DB=/data/adb/lspd/config/modules_config.db
if [ -f "$DB" ]; then CLASSPATH="$SUITE_DIR/payload/scope-helper.dex" app_process /system/bin ScopeSetup disable "$DB" > "$SUITE_DIR/hook-uninstall.txt" 2>&1; fi
# Frameworks may be shared by other modules; leave them installed.
pm uninstall cn.local.plt120.recentsfix >/dev/null 2>&1
''')
write('SOURCES.txt','''OEM packages: user-supplied ColorOS application extension v1.1, original signatures unchanged.
https://github.com/CiZhanYue/magisk-ColorOSCommonFeatureSupplements
Standalone mount mechanism: https://github.com/backslashxx/mountify/tree/standalone-script (Unlicense, included).
Zygisk Next 1.5.3 build880: https://github.com/Dr-TSNG/ZygiskNext/releases/tag/v1.5.3
LSPosed Irena 2.0.0 build7316: https://github.com/re-zero001/LSPosed-Irena/releases/tag/2.0.0
Framework installer ZIPs are bundled byte-for-byte and their checks remain active. Existing frameworks are preserved.
LSPosed source and configuration schema: https://github.com/re-zero001/LSPosed-Irena
''')
write('README.txt','''ColorOS native suite 2.3 test / 2026-11-10
One ZIP installs the feature layer, five missing OEM apps, one native repair Hook, and missing pinned framework dependencies.
No fixed model, firmware or ColorOS version restriction. APK ABI, page-size, XML structure and signature checks are retained.
Current actual test device: OPPO PLT120, ColorOS 15.0.2.1005. ColorOS 16 is unverified; interface mismatch skips the Hook.
Native lockscreen clock editor includes weather/lunar information, clock styles and fonts. This is not proof of an arbitrary agenda-widget picker.
Missing OEM inspiration-template groups are appended from a pinned public firmware resource tree. Existing device groups are retained. Native editor/schema/style-asset compatibility is checked before mounting; an incompatible theme part is skipped. No APK is replaced and no theme is automatically applied. Theme-resource provenance and hashes are included under parts/themes/payload/source-manifest.json. Unrelated live-wallpaper and global animation gates are preserved.
AI/video/order services require OEM support and user consent/account. Installed packages alone do not verify complete workflows.
The Xiaobu suggestions container override has args=boolean:true: UMS reads its boolean value, not only its presence. The OEM card resource already exists and is not a third-party replacement.
Both speechassist.cui.device.light.low and speechassist.cui.device.light declarations are removed. This changes the native lightweight-mode branch and isLightSystem request flag; it does not replace OEM cloud configuration or impersonate another model.
KernelSU-family first-time framework installation may require two reboots, but the ZIP is flashed once. Existing compatible framework users need one reboot.
The framework configuration helper changes only cn.local.plt120.recentsfix, owner-user 0, with Launcher scope, using a checked schema and an atomic SQLite transaction.
Disable and reboot reverses XML/APK mounting and disables the suite Hook through its boot-session activation property. Uninstall removes the suite Hook APK automatically.
The original companion from this task is disabled automatically. It is not deleted or re-enabled on uninstall. Existing frameworks are not removed automatically.
''')
for name in ('发布说明.md','验收记录.md'):
 shutil.copy2(ROOT/'docs'/name,DEST/name)
manifest=[]
for f in sorted(DEST.rglob('*')):
 if f.is_file() and f!=DEST/'payloads.sha256':manifest.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(DEST).as_posix())
write('payloads.sha256','\n'.join(manifest)+'\n')
artifact=OUT/'ColorOS_NativeSuite_2.3-test.zip'
with zipfile.ZipFile(artifact,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(DEST.rglob('*')):
  if f.is_file():
   info=zipfile.ZipInfo(f.relative_to(DEST).as_posix(),(2026,11,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=(0o100755 if f.suffix=='.sh' else 0o100644)<<16;z.writestr(info,f.read_bytes())
with zipfile.ZipFile(artifact) as z:assert z.testzip() is None
digest=hashlib.sha256(artifact.read_bytes()).hexdigest();artifact.with_suffix('.zip.sha256').write_text(digest+'  '+artifact.name+'\n',encoding='utf8')
report={'file':str(artifact),'bytes':artifact.stat().st_size,'sha256':digest,'files':len(manifest)+1,'frameworks':[{'file':n,'id':i,'sha256':h} for n,i,h in deps]}
(OUT/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
