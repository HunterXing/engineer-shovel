# AI Coding Agent Memory & Context Persistence: Research Report

**Generated:** 2026-05-04 | **Sources:** 20+ | **Confidence:** High

---

## Executive Summary

Memory/context persistence for AI coding agents is one of the hottest areas in AI tooling as of mid-2026. The dominant approach is **auto-capture + AI compression + hybrid retrieval** (SQLite FTS5 + vector DB). The clear market leader is **claude-mem** (71.7k GitHub stars, v12.6.0), which installs as a Claude Code plugin with lifecycle hooks and provides a three-layer progressive disclosure search system. **Mem0** (41k+ stars, $24M Series A) is the enterprise SDK alternative. **SharedContext** is the emerging sovereign/encrypted approach using Arweave. **Hermes Agent** (40k+ stars) represents a different paradigm: autonomous self-learning agent with built-in memory, not a plugin.

For a project already using ecc + gsd + superpowers + code-review-graph + caveman + rtk + OpenSpec, the most complementary options are:

1. **claude-mem** (best fit — plugin-based, OpenCode compatible, complements existing toolchain)
2. **Official MCP Memory Server** (lightweight, official, knowledge graph model)
3. **Mem0** (if production-grade memory API is needed)

---

## 1. claude-mem (Persistent Memory Compression Plugin)

| Attribute | Detail |
|-----------|--------|
| **URL** | https://github.com/thedotmack/claude-mem |
| **Stars** | 71.7k (May 2026) |
| **Latest Version** | v12.6.0 |
| **Language** | TypeScript (86.7%), JavaScript (7.3%) |
| **License** | AGPL-3.0 |
| **Install** | `npx claude-mem install` or `/plugin marketplace add thedotmack/claude-mem` |
| **OpenCode Support** | ✅ `npx claude-mem install --ide opencode` |
| **Gemini CLI Support** | ✅ `npx claude-mem install --ide gemini-cli` |
| **Description** | Claude Code plugin that auto-captures tool outputs, compresses via Claude Agent SDK, injects relevant context into future sessions |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    5 Lifecycle Hooks                         │
│  SessionStart → UserPromptSubmit → PostToolUse → Stop →     │
│  SessionEnd                                                  │
├─────────────────────────────────────────────────────────────┤
│  Worker Service (port 37777)                                 │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ Web Viewer UI│  │ 10 Search APIs   │  │mem-search Skill│  │
│  └──────────────┘  └──────────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Storage: SQLite (FTS5 full-text) + Chroma (vector semantic) │
│  Compression: Claude Agent SDK (1000-10000 → ~500 tokens)   │
└─────────────────────────────────────────────────────────────┘
```

### Three-Layer Progressive Disclosure Search

1. **`search`** — Compact index with IDs (~50-100 tokens/result)
2. **`timeline`** — Chronological context around interesting results
3. **`get_observations`** — Full details ONLY for filtered IDs (~500-1000 tokens/result)

**~10x token savings** compared to naive full-context approaches.

### Key Features
- 🧠 **Persistent Memory** — Automatic, no manual intervention
- 📊 **Progressive Disclosure** — Layered memory retrieval with token cost visibility
- 🔍 **Skill-Based Search** — `mem-search` skill for natural language queries
- 🖥️ **Web Viewer UI** — Real-time memory stream at `http://localhost:37777`
- 🔒 **Privacy Control** — `<private>` tags exclude sensitive content
- ⚙️ **Fine-grained Context Control** — Configurable injection settings
- 🔗 **Citations** — Reference past observations by ID
- 🧪 **Beta: Endless Mode** — Biomimetic memory architecture for extended sessions
- 🌐 **Multi-IDE** — Claude Code, Gemini CLI, OpenCode, Cursor, OpenClaw

### Strengths
- Battle-tested with massive community (71.7k stars, 109 contributors, 1,832 commits)
- Local-first (no cloud dependency for core operation)
- Three-layer disclosure is genuinely token-efficient
- OpenCode support is explicit and documented
- Web viewer provides observability into what's being remembered
- Active development (256 releases, latest May 4, 2026)

### Weaknesses
- AGPL-3.0 license may be restrictive for commercial use
- Requires Bun runtime + Python uv for vector search
- Local resource consumption (SQLite + Chroma DB)
- Claude Agent SDK dependency (costs tokens to compress)
- Single-machine by default (no sync across machines)

### Integration with Existing Toolchain
- ✅ OpenCode: Explicit `--ide opencode` support
- ✅ Plugin marketplace: Adds to existing Claude Code plugin system
- ⚠️ GSD: Memory of GSD phases and decisions would be captured automatically
- ⚠️ Caveman: Potential overlap — caveman compresses communication, claude-mem persists it
- ⚠️ code-review-graph: Complementary — one is code structure graph, other is session memory
- ✅ superpowers/ECC: Works alongside existing skill ecosystem

---

## 2. SharedContext (Sovereign, Encrypted, Portable Memory)

| Attribute | Detail |
|-----------|--------|
| **URL** | https://github.com/Eversmile12/sharedcontext |
| **Stars** | 47 (early-stage) |
| **Version** | v0.1.x |
| **Language** | TypeScript |
| **License** | MIT |
| **Install** | `npm install -g ai-sharedcontext` |
| **Description** | MCP server giving AI assistants persistent cross-client memory. Facts in SQLite, AES-256-GCM encrypted, synced to Arweave |

### Architecture

```
┌───────────────────────────────────────────────────────┐
│              SharedContext MCP Server                  │
├───────────────────────────────────────────────────────┤
│  Local: SQLite (facts, pending_deletes, meta)         │
│  Encryption: AES-256-GCM (client-side)                │
│  Signatures: secp256k1                                 │
│  Key Derivation: Argon2id                              │
│  Sync: Arweave (permanent, censorship-resistant)      │
│  Recovery: 12-word mnemonic phrase                     │
├───────────────────────────────────────────────────────┤
│  MCP Tools: store_fact, recall_context,               │
│  recall_conversation                                    │
│  Watchers: Cursor transcripts, Claude Code JSONL       │
└───────────────────────────────────────────────────────┘
```

### Key Features
- **Cross-client unified memory** — Cursor + Claude + Codex all share one memory
- **Encrypted sync** — All data encrypted before leaving machine
- **Portable** — 12-word phrase restores everything on any machine
- **Conversation sharing** — Share specific conversations via encrypted link
- **Auto-setup** — Detects installed clients and configures MCP automatically

### Strengths
- True sovereignty (no server, no account, you are the only keyholder)
- Cross-machine portability via Arweave
- MIT license (commercial-friendly)
- Elegant security model

### Weaknesses
- **Very early stage** (v0.1.x, 8 commits, 47 stars)
- No semantic/vector search (heuristic/keyword only)
- Single-user only
- Not battle-tested in production
- Small community, uncertain longevity

---

## 3. Mem0 (Universal Memory Layer for AI Apps)

| Attribute | Detail |
|-----------|--------|
| **URL** | https://github.com/mem0ai/mem0 |
| **Stars** | 41k+ |
| **Language** | Python (primary), TypeScript SDK |
| **License** | Apache 2.0 |
| **Funding** | $24M Series A (Feb 2026) |
| **Description** | Universal, self-improving AI memory layer for LLM applications |

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Mem0 Memory Layer                     │
├──────────────────────────────────────────────────────┤
│  SDKs: Python, JavaScript, TypeScript                 │
│  Integration: MCP, Claude Code Plugin, OpenClaw Skill │
│  Exclusive: AWS Agent SDK memory provider             │
│  Storage: Cloud-hosted or self-hosted (vector DB)     │
│  Algorithm: Token-efficient memory (benchmark: 91.6)  │
├──────────────────────────────────────────────────────┤
│  Benchmarks (April 2026, new algorithm):              │
│  - LoCoMo: 91.6 (was 71.4), 7.0K tokens               │
│  - LongMemEval: 93.4 (was 67.8), 6.8K tokens          │
│  - BEAM (1M): 64.1, 6.7K tokens                       │
│  - BEAM (10M): 48.6, 6.9K tokens                      │
└──────────────────────────────────────────────────────┘
```

### Strengths
- Enterprise-grade with strong funding and AWS partnership
- Excellent benchmark scores with new algorithm
- Multi-SDK support
- Apache 2.0 license

### Weaknesses
- Cloud dependency by default (API key required)
- Overkill for personal/individual use
- Less focus on coding-specific memory vs. general AI app memory

---

## 4. Official MCP Memory Server

| Attribute | Detail |
|-----------|--------|
| **URL** | https://github.com/modelcontextprotocol/servers (in `src/memory/`) |
| **Stars** | Official Anthropic MCP repository |
| **Language** | TypeScript |
| **License** | MIT |
| **Install** | `claude mcp add-json memory-mcp '{"command":"cmd","args":["/c","npx","-y","@modelcontextprotocol/server-memory"],...}'` |

### Architecture (Knowledge Graph Model)
```
┌─────────────────────────────────────────┐
│      Official MCP Memory Server          │
├─────────────────────────────────────────┤
│  Data Model: Knowledge Graph             │
│  - Entities (nodes)                      │
│  - Relations (edges)                     │
│  - Observations (facts about entities)   │
├─────────────────────────────────────────┤
│  Tools:                                  │
│  - create_entities                       │
│  - create_relations                      │
│  - add_observations                      │
│  - delete_entities / relations / obs     │
│  - read_graph / search_nodes             │
│  - open_nodes                            │
├─────────────────────────────────────────┤
│  Storage: JSON file (MEMORY_FILE_PATH)   │
└─────────────────────────────────────────┘
```

### Strengths
- Official Anthropic MCP server
- Knowledge graph model is intuitive and structured
- Simple, lightweight
- No external dependencies beyond Node.js

### Weaknesses
- **No auto-capture** — requires explicit tool calls to store/retrieve
- No compression or summarization
- JSON file storage (not optimized for large volumes)
- No semantic search (exact/keyword only in basic config)
- No web viewer or observability

---

## 5. Hermes Agent (Autonomous Self-Learning Agent)

| Attribute | Detail |
|-----------|--------|
| **URL** | https://github.com/NousResearch/hermes-agent |
| **Stars** | 40k+ |
| **Language** | Python |
| **License** | MIT |
| **Description** | Self-hosted, self-evolving autonomous AI agent with persistent memory and auto-skill generation |

### Four-Layer Memory System
1. **MEMORY.md** — Environmental facts, lessons learned
2. **USER.md** — Professional profile, goals, preferences
3. **Skills** — Auto-generated reusable workflows
4. **Conversation History** — Searchable past interactions (FTS5)

### Relationship to Project
Hermes Agent is a **competing/alternative paradigm** — it's a full autonomous agent framework, not a plugin. It replaces rather than augments existing toolchains. Not recommended for this project but worth understanding as a reference architecture for self-learning memory.

---

## 6. continuous-learning-v2 (Already Installed)

| Attribute | Detail |
|-----------|--------|
| **Location** | `/root/.claude/skills/continuous-learning-v2/` |
| **Type** | ECC Skill |
| **Description** | Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, evolves them into skills/commands/agents |

### How It Works
- Observes sessions via hooks
- Creates atomic instincts with confidence scoring
- Evolves instincts into skills/commands/agents over time
- v2.1 adds project-scoped instincts to prevent cross-project contamination

This is already part of the project's toolchain and provides a form of memory/learning. However, it's focused on pattern extraction rather than session-to-session context continuity.

---

## Memory Patterns in AI Coding Agents: Comparative Analysis

| Pattern | Examples | How It Works | Best For |
|---------|----------|-------------|----------|
| **File-based** | CLAUDE.md, AGENTS.md, MEMORY.md | Static files, manually or semi-automatically maintained | Project conventions, preferences |
| **Auto-Capture + Compression** | claude-mem | Hooks capture tool outputs, AI compresses to semantic observations | Session continuity, "what did we do yesterday" |
| **Knowledge Graph** | MCP Memory Server, code-review-graph | Structured entities + relations + observations | Structured fact recall, relationship querying |
| **Vector DB / Semantic** | claude-mem (Chroma), Mem0 | Embeddings for similarity search | Finding relevant past context by meaning |
| **Self-Learning Loops** | continuous-learning-v2, Hermes Agent | Pattern extraction → skill generation → confidence scoring | Gradual improvement, pattern recognition |
| **Encrypted Sovereign Sync** | SharedContext | AES-256-GCM encryption + Arweave permanent storage | Cross-machine, privacy-first, portable |

---

## Recommendation: What Works Best for This Project

### Current Toolchain
```
ecc + gsd + superpowers + code-review-graph + caveman + rtk + OpenSpec
+ continuous-learning-v2 (already installed)
```

### Tier 1 — Immediate High Value

**claude-mem** is the clear first choice:
- ✅ Explicit OpenCode support (`npx claude-mem install --ide opencode`)
- ✅ Plugin-based (fits the existing plugin ecosystem)
- ✅ Auto-capture (no manual effort required)
- ✅ Semantic search (Chroma vector DB)
- ✅ Web viewer for observability
- ✅ Active, well-maintained (71.7k stars, daily updates)
- ⚠️ AGPL-3.0 — check compatibility for your use case
- ⚠️ Memory of GSD phase artifacts would be captured, complementing GSD's structured planning

### Tier 2 — Complementary

**Official MCP Memory Server** as a lightweight structured memory layer:
- Would work alongside claude-mem (different memory model)
- Knowledge graph model complements code-review-graph's existing graph
- Official, no license concerns

### Tier 3 — If Needed

**Mem0** if the project needs production-grade memory API with multi-user support:
- Overkill for individual development
- Best if building a multi-user AI coding platform

### Not Recommended
- **SharedContext** — too early, overlapping with claude-mem but less mature
- **Hermes Agent** — full framework replacement, not a plugin

### Integration Architecture Suggestion

```
┌─────────────────────────────────────────────────────────┐
│                    Your Project                           │
├─────────────────────────────────────────────────────────┤
│  Session Continuity: claude-mem                          │
│  (auto-captures tool outputs, compresses, retrieves)     │
│                                                          │
│  Structured Facts: MCP Memory Server (optional)          │
│  (knowledge graph for project decisions, architecture)   │
│                                                          │
│  Pattern Learning: continuous-learning-v2                │
│  (already installed — instinct-based skill generation)   │
│                                                          │
│  Code Structure: code-review-graph                       │
│  (already installed — codebase knowledge graph)           │
│                                                          │
│  Static Context: CLAUDE.md + AGENTS.md                   │
│  (project conventions, toolchain preferences)            │
│                                                          │
│  Token Efficiency: caveman + rtk                         │
│  (already installed — communication compression)         │
└─────────────────────────────────────────────────────────┘
```

---

## Sources

1. [claude-mem GitHub](https://github.com/thedotmack/claude-mem) — Claude Code persistent memory compression plugin, 71.7k stars
2. [claude-mem Official Docs](https://docs.claude-mem.ai/) — Full architecture, installation, and usage docs
3. [SharedContext GitHub](https://github.com/Eversmile12/sharedcontext) — MCP server for sovereign, encrypted agent memory
4. [Mem0 GitHub](https://github.com/mem0ai/mem0) — Universal memory layer for AI agents, 41k+ stars
5. [Mem0 Official](https://mem0.ai/) — Enterprise memory platform, $24M Series A
6. [Official MCP Memory Server](https://github.com/modelcontextprotocol/servers) — Anthropic knowledge graph memory server
7. [Hermes Agent (NousResearch)](https://github.com/NousResearch/hermes-agent) — Self-evolving autonomous agent, 40k+ stars
8. [claude-memory-mcp GitHub](https://github.com/randall-gross/claude-memory-mcp) — Claude Desktop/Code MCP memory setup guide
9. [给Claude Code装上长期记忆 (Tencent Cloud)](https://cloud.tencent.com/developer/article/2632345) — claude-mem deep analysis
10. [AI Agent记忆系统避坑指南 (CSDN)](https://blog.csdn.net/play7/article/details/151279414) — Agent memory engineering practices
11. [浅谈 Agent Memory (Tencent News)](https://new.qq.com/rain/a/20260412A05LII00) — Agent memory architecture overview
12. [instinct-based self-learning system](https://so.html5.qq.com/page/real/search_news?docid=70000021_75869d5052d30252) — Confidence-based AI agent learning
13. [Hermes Agent 完整知识总结 (CSDN)](https://blog.csdn.net/weixin_50701238/article/details/160031867) — Hermes Agent comprehensive analysis
14. [Claude Code 使用技巧 (CSDN)](https://blog.csdn.net/zs16113/article/details/158807056) — Claude Code MCP and memory configuration
15. [Claude Code 与MCP 服务器使用指南 (CSDN)](https://blog.csdn.net/xautxuliang/article/details/157291296) — MCP server configuration guide

## Methodology

Searched 7 queries across web (MiniMax) and web fetch (GitHub README). Analyzed 15+ sources with full README reads for top projects. Cross-referenced features, community size, update frequency, and compatibility with existing toolchain (ecc + gsd + superpowers + code-review-graph + caveman + rtk + OpenSpec + continuous-learning-v2).

Sub-questions investigated:
1. What is claude-mem and how does it work?
2. What other memory plugins/tools exist for Claude Code and OpenCode?
3. What are the common memory patterns in AI coding agents?
4. Which tools integrate best with the existing toolchain?
5. What is the current state of memory persistence across sessions?
