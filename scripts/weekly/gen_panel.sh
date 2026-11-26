#!/usr/bin/env bash
# 用法：scripts/weekly/gen_panel.sh <输出文件> "<场景描述>"。调用 Gemini（agy）按 config/comic_style.txt 的统一画风出一张图；按会话编号取图，可并行。
out="$1"; scene="$2"; B=/c/Users/WINDOWS/.gemini/antigravity-cli/brain
for try in 1 2 3; do
  json=$(timeout 500 agy -p "$(cat "$(dirname "$0")/../../config/comic_style.txt")

用你的图像生成工具生成一张插画。场景：$scene
生成后自己检查：若出现文字、数字、乱码或畸形手部就重画。" --mode accept-edits --output-format json 2>/dev/null)
  cid=$(printf '%s' "$json" | grep -oE '"conversation_id":"[^"]+"' | head -1 | cut -d'"' -f4)
  [ -n "$cid" ] || continue
  f=$(find "$B/$cid" \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
  if [ -n "$f" ]; then cp "$f" "$out"; echo "ok $out ($cid)"; exit 0; fi
done
echo "fail $out"; exit 1
