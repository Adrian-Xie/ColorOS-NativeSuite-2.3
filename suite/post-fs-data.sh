#!/system/bin/sh
SUITE_DIR=${0%/*}
[ ! -e "$SUITE_DIR/disable" ] && [ ! -e "$SUITE_DIR/remove" ] || exit 0
: > "$SUITE_DIR/status.txt"
STATE=1
for P in features components themes; do
 sh "$SUITE_DIR/parts/$P/post-fs-data.sh" || { echo "FAILED: $P; see part status" >> "$SUITE_DIR/status.txt"; STATE=0; }
done
setprop sys.coloros_native_suite "$STATE"
