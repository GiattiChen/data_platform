#!/bin/bash
# 启动 Data Platform
cd "$(dirname "$0")"
streamlit run app.py --server.port 8730
