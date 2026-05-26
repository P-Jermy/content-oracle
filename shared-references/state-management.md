# .content-state.json 管理协议

## 位置

每个内容项目的根目录下：`<project>/.content-state.json`

## schema

```json
{
  "schema_version": "0.1.0",
  "skill_version": "0.1.0",
  "initialized_at": "ISO8601 UTC",
  "rubric_version": "v0",
  "content_form": "long-essay|video|podcast|thread",
  "target_publish_cadence_days": 3,
  "benchmark_status": "not-setup|imported|calibrated",
  "benchmark_sample_count": 0,
  "calibration_samples": 0,
  "enabled_trend_sources": ["github-trending", "hacker-news"],
  "last_trends_run_at": null,
  "last_trends_added_count": 0,
  "last_published_at": null,
  "last_published_file": null,
  "shoots": [],
  "pending_retros": [],
  "consecutive_directional_errors": [],
  "in_progress_session": null
}
```

## 读写规则

- 由 scripts/state.py 统一管理
- Hermes 子 skill 通过 import state 模块读写
- 不手动编辑（除非 debug）
- schema 变更时由 migration 脚本处理
