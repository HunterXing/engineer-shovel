<h1 align="center">🪖 Engineer Shovel</h1>

<p align="center">
  <b>Token-aware AI エージェント開発ワークフロールーター</b><br>
  <sub>クイックタスク · バグ修正 · 新機能 · ブランチ · プラン · リファクタリング · レビュー · ブレインストーミング · ブループリント · リサーチ · グラフ · 同期</sub>
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

## これは何ですか？

Engineer Shovel は、OpenCode と Claude Code 向けの軽量スキル + スラッシュコマンドパックです。開発作業を最も低コストで結果を検証できるワークフローにルーティングし、リスクが必要と判断した場合のみより深いエージェントワークフローにエスカレーションします。

ランタイムの `SKILL.md` は意図的に小さく保たれています。長文ドキュメントは `docs/` に置かれているため、日常的なセッションでは完全なマニュアルを読み込むコストを払う必要がありません。

## 能力の境界

Engineer Shovel のネイティブインストールは、軽量ルーターと12の `/tool-*` コマンドです。フルワークフローで宣伝されているより深い機能は、recommended/full モードでインストールまたは構成されたオプションの外部ツールから提供されます：ECC、GSD、superpowers、code-review-graph、Caveman、RTK。

Minimal インストールは意図的に小さく保たれています。ワークフローで GSD、ECC、Caveman、RTK、code-review-graph などの外部コマンドが言及されている場合、これらの機能には対応するオプションツールがインストールされ正常動作している必要があります。

## クイックスタート

```bash
# ダウンロード，检查，実行（デフォルト：全コンポーネントのフルモード）
curl -fsSL -o install.sh https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh
less install.sh
bash install.sh

# 非対話型：OpenCode 用フルインストール（デフォルト）
bash install.sh --target opencode

# 非対話型：OpenCode と Claude Code の両方にインストール
bash install.sh --target all

# ソースをすでに信頼している場合のショートカット：
# curl -fsSL https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.sh | bash

# その他のモード
./install.sh --target opencode --recommended  # Skill + コマンド + Caveman
./install.sh --target opencode --minimal      # Skill + コマンドのみ
./install.sh --target opencode --full --with-graph-build  # 初期 code-review-graph インデックスも構築
```

インストーラーは、オプションの依存関係をステージングする前に、固定された外部リポジトリの SHA を確認します。ダウンロードファーストインストールは、スクリプトを検査でき、サーバーサイドのパイプ検出の違いを回避できるため、直接 Bash にパイプするよりも安全です。

## 互換性について

この最適化サイクルは、公開インターフェースを安定に保ちます：

- `skill(name="engineer-shovel")` は変更されません。
- 12 の `/tool-*` コマンドはすべて同じ名前で維持されます。
- `--minimal`、`--recommended`、`--full`、`--dry-run` は変更されません。
- `--target opencode|claude|all|auto` により、新しいマシンは OpenCode、Claude Code、またはその両方を明示的に選択できます。

追加された新しいガードレール：

- ダウンロードファーストインストールが推奨されるドキュメントパスになりました。
- インストーラーは SHA ピン検証を維持し、外部インストーラー実行に関するより明確な失敗動作を表示するようになりました。
- バリデーションスクリプトに軽量な pytest 回帰テストが追加されました。

その後、いずれかを使用します：

```text
skill(name="engineer-shovel")
```

または、コマンドを直接呼び出します：

```text
/tool-quick --fast "fix typo in README"
/tool-review --fast
/tool-research --deep "compare options for X"
/tool-graph update
```

## コストモード

| モード | 使用タイミング | 典型的なパス |
|---|---|---|
| `--fast` | 低リスク、既知のターゲット | `/caveman lite`、直接編集、`/gsd-fast`、Caveman レビュー |
| `--standard` | 通常の開発 | `/caveman full`、ターゲット検索、実装、テスト/ビルド |
| `--deep` | 曖昧、高リスク、マルチシステム | `/caveman full` または `ultra`、GSD、深いリサーチ、Oracle/review-work |

RTK はインストールされている場合、git、テスト、ビルド、ログなどのノイズの多い Bash/tool 出力をモデルコンテキストに入る前に圧縮する дополнение です。

## コマンド

| コマンド | 用途 |
|---|---|
| `/tool-quick` | 明らかな小さな編集 |
| `/tool-fix` | バグ、失敗したテスト、回帰 |
| `/tool-feat` | 新機能 |
| `/tool-branch` | ブランチワークフロー：作成、レビュー、マージ、中止 |
| `/tool-plan` | 要件と実装の計画 |
| `/tool-refactor` | 動作を保つクリーンアップ |
| `/tool-review` | ローカル差分、PR、または深いレビュー |
| `/tool-brainstorm` | **[非推奨]** — アイデア明確化は `/tool-feat` や `/tool-plan` に内蔵 |
| `/tool-blueprint` | **[非推奨]** — マルチステップ計画は `/tool-plan --deep` に統合 |
| `/tool-research` | 証拠の収集と統合 |
| `/tool-graph` | code-review-graph ステータス、完全ビルド，增分更新、再構築、監視 |
| `/tool-update` | インストールと同期 |

## 構造

```
engineer-shovel/
├── commands/          # 12 の実行可能スラッシュコマンド
├── docs/              # ランタイムコンテキストから分離された長文リファレンス
├── scripts/           # 同期とバリデーションのユーティリティ
├── SKILL.md           # 軽量ルーター
├── install.sh         # minimal/recommended/full インストーラー
├── README.md
├── README_zh.md
└── LICENSE
```

## ドキュメント

- ツールチェーンアーキテクチャ：[`docs/architecture.md`](docs/architecture.md)
- Token コストモデル：[`docs/token-cost.md`](docs/token-cost.md)
- インストールモード：[`docs/install.md`](docs/install.md)
- 言語リファレンス：[`docs/language-reference.md`](docs/language-reference.md)

## ライセンス

MIT — [LICENSE](LICENSE) 参照。

## 上流ツールバージョン

Engineer Shovel は `--full` モードでこれらの上流ツールを統合および構成します。

| ツール | リポジトリ | 現在の参照バージョン | 役割 |
|---|---|---:|---|
| ECC | https://github.com/affaan-m/everything-claude-code | v1.10.0 | AI エージェントハーネス性能システム：スキル、ルール、フック、MCP、セキュリティ、research-first ワークフロー |
| GSD | https://github.com/gsd-build/get-shit-done | v1.39.0 | Spec駆動の計画、フェーズ実行、検証、コンテキストエンジニアリング |
| superpowers | https://github.com/obra/superpowers | v5.0.7 | 必須スキルワークフロー：ブレインストーミング、TDD、計画、レビュー、ブランチ終結 |
| code-review-graph | https://github.com/tirth8205/code-review-graph | v2.3.2 | ローカルコード知識グラフ、MCP レビューコンテキスト、ブラスト半径分析 |
| Caveman | https://github.com/JuliusBrussee/caveman | v1.7.0 | 出力トークン圧縮、簡潔なレビュー/コミット、MCP shrink |
| RTK | https://github.com/rtk-ai/rtk | v0.38.0 | シェルとツール出力圧縮プロキシおよびコマンド書き換えフック |
