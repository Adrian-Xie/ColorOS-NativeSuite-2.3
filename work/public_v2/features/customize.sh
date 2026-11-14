#!/system/bin/sh
[ "${BOOTMODE:-}" = true ] || abort 'Install from the running root manager.'
MODDIR="$MODPATH"
. "$MODDIR/common.sh"
for D in /data/adb/modules/ColorOSCommonFeatureSupplements /data/adb/modules_update/ColorOSCommonFeatureSupplements; do
  [ ! -d "$D" ] || abort 'Remove the broad original feature module and reboot first.'
done
generate_files || abort "${PATCH_ERROR:-Failed to generate local configuration}"
set_perm_recursive "$MODPATH" 0 0 0755 0644
for F in common.sh post-fs-data.sh service.sh action.sh; do set_perm "$MODPATH/$F" 0 0 0755; done
ui_print 'No model, firmware, ColorOS-version or baseline-hash restriction.'
ui_print 'Configuration is generated from THIS phone; no donor XML is bundled.'
ui_print 'Only the requested feature edits are applied; no global blur/animation changes.'
ui_print 'Reboot required. Per-feature UI/component/cloud verification remains necessary.'
