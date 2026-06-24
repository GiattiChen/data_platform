#!/bin/bash
# 通过 Cloudflare Tunnel 暴露本地 Streamlit（公网临时访问）
# 安装: brew install cloudflared
# 用法: 先在一个终端 streamlit run app.py，再在另一个终端 bash start_tunnel.sh

set -e
cd "$(dirname "$0")"

PORT=8730

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "未安装 cloudflared，请先执行: brew install cloudflared"
  exit 1
fi

echo "正在将 http://localhost:${PORT} 映射到公网临时域名..."
echo "请保持此终端运行，关闭后公网链接失效。"
cloudflared tunnel --url "http://localhost:${PORT}"
