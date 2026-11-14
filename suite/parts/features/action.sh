#!/system/bin/sh
MODDIR=${0%/*}
cat "$MODDIR/status.txt"
cat "$MODDIR/files.tsv"
