#!/system/bin/sh
SUITE_DIR=${0%/*}
for P in features components themes; do echo "[$P]"; cat "$SUITE_DIR/parts/$P/status.txt"; done
echo '[Hook]'; cat "$SUITE_DIR/hook-setup.txt"; cat "$SUITE_DIR/status.txt"
echo '[OEM fluid capability]'
content call --uri content://com.oplus.pantanal.ums.IntentProvider --method isFluidCloudSupport 2>&1
echo '[OEM AI components]'
for PKG in com.heytap.speechassist com.oplus.pantanal.ums com.oplus.metis com.coloros.sceneservice com.coloros.colordirectservice com.coloros.directui; do
 printf '%s: ' "$PKG"; pm path "$PKG" 2>/dev/null
done
