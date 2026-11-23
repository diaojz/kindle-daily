#!/bin/sh
# Name: 今日简报
# Author: kindle-daily
# Icon: /mnt/us/koreader/resources/koreader.png
# 点一下：联网下载当天的每日简报（已下过就不重复下），然后直接在 KOReader 里打开。
BASE=https://diaojz.github.io/kindle-daily
DIR=/mnt/us/documents/简报
CA=/mnt/us/koreader/data/ca-bundle.crt
mkdir -p "$DIR"
say() { eips 2 38 "$1                              " >/dev/null 2>&1; }
get() { curl -fsSL -m 120 "$@" || curl -fsSL -m 120 --cacert "$CA" "$@"; }

lipc-set-prop com.lab126.cmd wirelessEnable 1 >/dev/null 2>&1
say "kindle-daily: connecting..."
i=0
while [ $i -lt 30 ]; do
  D=$(get "$BASE/version.txt" 2>/dev/null | tr -d '\r\n ')
  [ -n "$D" ] && break
  sleep 2; i=$((i+1))
done

if [ -n "$D" ] && [ ! -s "$DIR/$D.epub" ]; then
  say "kindle-daily: downloading $D ..."
  if get -o "$DIR/$D.epub.part" "$BASE/$D.epub"; then
    mv "$DIR/$D.epub.part" "$DIR/$D.epub"
  else
    rm -f "$DIR/$D.epub.part"
  fi
fi
# 只留最近 7 期
ls -1 "$DIR"/*.epub 2>/dev/null | sort -r | tail -n +8 | while read -r f; do rm -rf "$f" "${f%.epub}.sdr"; done

LATEST=$(ls -1 "$DIR"/*.epub 2>/dev/null | sort -r | head -1)
if [ -z "$LATEST" ]; then
  say "kindle-daily: no network, try again"
  exit 1
fi
/mnt/us/koreader/koreader.sh --kual "$LATEST" &
