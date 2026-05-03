# Documentation Sync Policy

## Supported Languages

| File | Language | Status |
|------|----------|--------|
| `README.md` | English | Complete (master) |
| `README_zh.md` | Chinese (Simplified) | Complete |
| `README.ja-JP.md` | Japanese | Complete |
| `README.ko-KR.md` | Korean | Complete |

## Sync Rule

**日语、韩语文档必须与英语文档保持同步更新。**

When `README.md` is modified:
1. Update `README.ja-JP.md` and `README.ko-KR.md` in the same commit/PR
2. Translations must not be "preparing" or outdated placeholders
3. The `## Status` section above must reflect actual state

## PR Checklist

Before merging any PR that modifies `README.md`:
- [ ] Verify `README.ja-JP.md` is updated and complete
- [ ] Verify `README.ko-KR.md` is updated and complete
- [ ] Update this file if new documents are added

## Translation Priority

If translation lags behind, the English version (`README.md`) is the authoritative source.