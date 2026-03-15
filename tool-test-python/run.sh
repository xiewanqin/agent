#!/bin/bash
# Python 运行脚本 - 自动使用 python3
cd "$(dirname "$0")"
python3 src/my-test.py "$@"
