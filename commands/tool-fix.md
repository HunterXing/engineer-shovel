> ⚠️ Reference doc — commands are not executable. Follow the steps manually.

# /tool-fix — Bug Fixing

**工兵铲 · Bug 修复工作流**

## Pipeline
```
Bug报告 → 定位 → 修复 → 验证 → 防止回归 → 提交
```

## Steps

### 1. 系统调试
```bash
/gsd-debug "$BUG_DESCRIPTION"
# 1. 复现 Bug
# 2. 隔离根因
# 3. 形成假设
# 4. 修复
# 5. 验证修复
```

### 2. 修复（最小改动）
```bash
# 根据调试结果直接修复，或通过 subagent:
task(session_id="$SESSION_ID", prompt="Fix: $ROOT_CAUSE")
```

### 3. 验证
```bash
/go-test          # Go
/rust-test        # Rust  
/cpp-test         # C++
/flutter-test     # Flutter
/kotlin-test      # Kotlin
bun test          # JS/TS
```

### 4. 防回归
```bash
/ai-regression-testing
```

### 5. 提交
```bash
git add . && git commit -m "fix: $ROOT_CAUSE"
```

## Scope Decision
| Scope | 方式 |
|-------|------|
| 单行/typo | cavecrew builder |
| 单函数 | 直接修复 → test |
| 跨文件 | /gsd-debug → task(deep) → test |
| 安全漏洞 | /security-review → fix → /security-scan |

---
> Load the skill first: `skill(name="engineer-shovel")`
