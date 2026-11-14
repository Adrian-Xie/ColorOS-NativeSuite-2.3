#!/system/bin/sh
SUITE_DIR=${0%/*}
setprop sys.coloros_native_suite 0
DB=/data/adb/lspd/config/modules_config.db
if [ -f "$DB" ]; then CLASSPATH="$SUITE_DIR/payload/scope-helper.dex" app_process /system/bin ScopeSetup disable "$DB" > "$SUITE_DIR/hook-uninstall.txt" 2>&1; fi
# Frameworks may be shared by other modules; leave them installed.
pm uninstall cn.local.plt120.recentsfix >/dev/null 2>&1
