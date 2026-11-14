"""Package additive OEM inspiration templates for the existing native editor."""
from pathlib import Path
import hashlib, shutil
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'work/oem_theme_payload'
DEST=ROOT/'work/public_v2/themes';DEST.mkdir(exist_ok=True)
shutil.copytree(SOURCE,DEST/'payload',dirs_exist_ok=True)
shutil.copy2(ROOT/'work/suite_research/theme-helper/classes.dex',DEST/'theme-helper.dex')
def write(name,text): (DEST/name).write_text(text,encoding='utf8',newline='\n')
write('common.sh',r'''#!/system/bin/sh
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
''')
write('customize.sh',r'''#!/system/bin/sh
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
''')
write('post-fs-data.sh',r'''#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
if [ -f "$MODDIR/pending_boot" ]; then echo 'SKIPPED: previous modified boot was not confirmed.' > "$MODDIR/status.txt"; : > "$MODDIR/disable"; exit 0; fi
if ! prepare_themes > "$MODDIR/status.txt" 2>&1; then echo 'SKIPPED: original native resources kept.' >> "$MODDIR/status.txt"; exit 0; fi
: > "$MODDIR/pending_boot"
if mount -o bind "$MODDIR/generated" "$THEME_TARGET" 2>> "$MODDIR/status.txt"; then
 echo 'MOUNTED: additive OEM template catalogue and assets; waiting for boot verification.' >> "$MODDIR/status.txt"
else
 rm -f "$MODDIR/pending_boot"
 echo 'SKIPPED: theme resource mount failed; original native resources kept.' >> "$MODDIR/status.txt"
fi
''')
write('service.sh',r'''#!/system/bin/sh
MODDIR=${0%/*}
[ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ] || exit 0
. "$MODDIR/common.sh"
N=0
while [ "$(getprop sys.boot_completed)" != 1 ] && [ "$N" -lt 180 ]; do sleep 2; N=$((N+1)); done
if [ "$(getprop sys.boot_completed)" = 1 ] && [ -f "$MODDIR/pending_boot" ]; then
 if cmp -s "$MODDIR/generated/inspiration_theme_templates.json" "$THEME_TARGET/inspiration_theme_templates.json"; then
  rm -f "$MODDIR/pending_boot"; echo 'Boot complete; OEM template catalogue mount verified. Editor workflow is a separate acceptance check.' >> "$MODDIR/status.txt"
 else echo 'WARNING: theme catalogue mount not visible.' >> "$MODDIR/status.txt"; fi
fi
''')
write('action.sh',r'''#!/system/bin/sh
MODDIR=${0%/*}
cat "$MODDIR/status.txt"
''')
files=[f for f in DEST.rglob('*') if f.is_file() and (f.is_relative_to(DEST/'payload') or f.name=='theme-helper.dex')]
write('payloads.sha256',''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(DEST).as_posix()+'\n' for f in sorted(files)))
print('Packaged native theme resources:',len(files),'files')
