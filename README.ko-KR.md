<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI 에이전트 개발 워크플로 라우터</b><br>
  <sub>빠른 작업 · 버그 수정 · 새 기능 · 브랜치 · 계획 · 리팩토링 · 리뷰 · 브레인스토밍 · 블루프린트 · 리서치 · 그래프 · 동기화</sub>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README_zh.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a>
</p>

<p align="center">
  <a href="https://github.com/HunterXing/engineer-shovel/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="https://github.com/HunterXing/engineer-shovel/forks"><img alt="GitHub forks" src="https://img.shields.io/github/forks/HunterXing/engineer-shovel?style=flat-square"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square"></a>
  <img alt="Commands" src="https://img.shields.io/badge/commands-12-5865F2?style=flat-square">
  <img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-supported-2ea44f?style=flat-square"></a>
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-6f42c1?style=flat-square">
</p>

---

##这是什么?

Engineer Shovel은 OpenCode 및 Claude Code를 위한 경량 스킬 + 슬래시 명령어 팩입니다. 개발 작업을 결과를 검증할 수 있는 가장 저렴한 워크플로로 라우팅한 다음,リスク가 필요할 경우 더深い 에이전트 워크플로로エスカレーション합니다.

런타임 `SKILL.md`는 의도적으로 작게 유지됩니다. 장기 문서는 `docs/`에 있으므로 일상적인 세션에서 전체 매뉴얼을 로드하는 비용을 지불하지 않아도 됩니다.

## 능력 경계

기본 Engineer Shovel 설치는 경량 라우터와 12개의 `/tool-*` 명령을 제공합니다. 전체 워크플로에서 광고되는 더 깊은 기능은 recommended/full 모드에서 설치되거나 구성되는 선택적 외부 도구에서 제공됩니다: ECC, GSD, superpowers, code-review-graph, Caveman, RTK.

Minimal 설치는 의도적으로 작게 유지됩니다. 워크플로에서 GSD, ECC, Caveman, RTK 또는 code-review-graph와 같은 외부 명령이 언급されている 경우, 해당 기능에는 corresponding 선택적 도구가 설치되어 있고 건강한 상태여야 합니다.

## 빠른 시작

```bash
# 다운로드, 검사, 실행(기본: 모든 구성요소의 전체 모드)
curl -fsSL -o install.sh https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh
less install.sh
bash install.sh

# 비대화형: OpenCode용 전체 설치(기본값)
bash install.sh --target opencode

# 비대화형: OpenCode 및 Claude Code 모두에 설치
bash install.sh --target all

# 이미 소스를 신뢰하는 경우 바로가기:
# curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# 기타 모드
./install.sh --target opencode --recommended  # Skill + 명령 + Caveman
./install.sh --target opencode --minimal      # Skill + 명령만
./install.sh --target opencode --full --with-graph-build  # 초기 code-review-graph 인덱스도 빌드
```

인스톨러는 선택적 종속성을 스테이징하기 전에 고정된 외부 리포지토리 SHA를 확인합니다. 다운로드 우선 설치는 스크립트를 검사할 수 있고 서버 측 파이프 감지 차이를 피할 수 있으므로 Bash에 직접 파이프하는 것보다 안전합니다.

## 호환성 참고

이 최적화 주기는 공개 인터페이스를 안정적으로 유지합니다:

- `skill(name="engineer-shovel")`은 변경되지 않습니다.
- 모든 12개의 `/tool-*` 명령은 동일한 이름으로 유지됩니다.
- `--minimal`, `--recommended`, `--full`, `--dry-run`은 변경되지 않습니다.
- `--target opencode|claude|all|auto`를 통해 새 시스템은 OpenCode, Claude Code 또는 둘 다를 명시적으로 선택할 수 있습니다.

추가된 새로운 가드레일:

- 다운로드 우선 설치가 이제 권장되는 문서화된 경로입니다.
- 인스톨러는 SHA 핀 검증을 유지하며 이제 외부 인스톨러 실행에 대한 더 명확한 실패 동작을 표시합니다.
- 검증 스크립트에 경량 pytest 회귀 테스트가 추가되었습니다.

그런 다음 다음 중 하나를 사용합니다:

```text
skill(name="engineer-shovel")
```

또는 명령을 직접 호출합니다:

```text
/tool-quick --fast "fix typo in README"
/tool-review --fast
/tool-research --deep "compare options for X"
/tool-graph update
```

## 비용 모드

| 모드 | 사용时机 |典型적인 경로 |
|---|---|---|
| `--fast` | 저위험, 알려진 대상 | `/caveman lite`, 직접 편집, `/gsd-fast`, Caveman 리뷰 |
| `--standard` | 일반 개발 | `/caveman full`, 대상 검색, 구현, 테스트/빌드 |
| `--deep` | 모호함, 고위험, 멀티시스템 | `/caveman full` 또는 `ultra`, GSD, 깊은 리서치, Oracle/review-work |

RTK는 설치될 때 보완적으로 작동합니다: git, 테스트, 빌드, 로그 등의 시끄러운 Bash/도구 출력이 모델 컨텍스트에 들어가기 전에 압축합니다.

## 명령어

| 명령어 | 용도 |
|---|---|
| `/tool-quick` | 명백한 작은 편집 |
| `/tool-fix` | 버그, 실패한 테스트, 회귀 |
| `/tool-feat` | 새 기능 |
| `/tool-branch` | 브랜치 워크플로: 생성, 리뷰, 병합, 중단 |
| `/tool-plan` | 요구사항 및 구현 계획 |
| `/tool-refactor` | 동작 보존 정리 |
| `/tool-review` | 로컬 diff, PR 또는 깊은 리뷰 |
| `/tool-brainstorm` | 구축 전 아이디어 명확화 |
| `/tool-blueprint` | 멀티스텝 또는 멀티세션 프로젝트 |
| `/tool-research` | 증거 수집 및 합성 |
| `/tool-graph` | code-review-graph 상태, 전체 빌드, 증분 업데이트, 재빌드, 감시 |
| `/tool-update` | 동기화 및 설치 업데이트 |

## 구조

```
engineer-shovel/
├── commands/          # 12개의 실행 슬래시 명령어
├── docs/              # 런타임 컨텍스트에서 분리된 장기 참조
├── scripts/           # 동기화 및 검증 유틸리티
├── SKILL.md           # 경량 라우터
├── install.sh         # minimal/recommended/full 인스톨러
├── README.md
├── README_zh.md
└── LICENSE
```

## 문서

- 전체 워크플로: [`docs/workflows.md`](docs/workflows.md)
- Token 비용 모델: [`docs/token-cost.md`](docs/token-cost.md)
- 설치 모드: [`docs/install.md`](docs/install.md)
- 언어 참조: [`docs/language-reference.md`](docs/language-reference.md)
- 리포지토리 평가: [`docs/assessment.md`](docs/assessment.md)

## 라이선스

MIT — [LICENSE](LICENSE) 참조.

## 상위 도구 버전

Engineer Shovel은 `--full` 모드에서 이러한 상위 도구를 통합하고 구성합니다.

| 도구 | 리포지토리 | 현재 참조 버전 | 역할 |
|---|---|---:|---|
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI 에이전트 하네스 성능 시스템: 스킬, 규칙, 훅, MCP, 보안, 리서치 우선 워크플로 |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | Spec 기반 계획, 단계 실행, 검증 및 컨텍스트 엔지니어링 |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | 필수 스킬 워크플로: 브레인스토밍, TDD, 계획, 리뷰, 브랜치 완료 |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | 로컬 코드 지식 그래프, MCP 리뷰 컨텍스트, 폭발 반경 분석 |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | 출력 토큰 압축, 간결한 리뷰/커밋, MCP 압축 |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | 셸 및 도구 출력 압축 프록시 및 명령어 재작성 훅 |
