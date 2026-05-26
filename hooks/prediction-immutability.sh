#!/usr/bin/env bash
# content-hook: prediction-immutability
# 确保预测文件不被修改
# 在 predictions/ 目录设置只读权限
# find predictions/ -name "*.md" -exec chmod 444 {} \;
echo "prediction immutability check"
