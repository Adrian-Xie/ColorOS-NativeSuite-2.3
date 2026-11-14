#!/system/bin/sh
SUITE_DIR=${0%/*}
[ ! -e "$SUITE_DIR/disable" ] && [ ! -e "$SUITE_DIR/remove" ] || exit 0
for P in features components themes; do sh "$SUITE_DIR/parts/$P/service.sh"; done
if [ ! -s "$SUITE_DIR/hook-setup.txt" ]; then
 if SUITE_DIR="$SUITE_DIR" sh "$SUITE_DIR/setup-hook.sh" > "$SUITE_DIR/hook-setup.log" 2>&1; then
  echo 'First framework setup finished. Reboot once more to load the Hook with its configured scope.' >> "$SUITE_DIR/status.txt"
 else echo 'HOOK NOT READY: inspect hook-setup.log or enable ColorOS native repair in LSPosed.' >> "$SUITE_DIR/status.txt"; fi
fi
