#!/usr/bin/env bash
# content-hook: log-event
# 记录事件到 .content-state.json
# Usage: hook_log_event.sh <event_type> <detail>
echo "{\"event\": \"$1\", \"detail\": \"$2\", \"at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
