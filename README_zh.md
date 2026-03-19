# skill-publisher

<p align="center">
  <h1>Skill Publisher</h1>
  <p>一键发布 Claude Code Skill 到 GitHub，自动验证、补全文件、创建仓库、推送并验证可安装。</p>
</p>

[[English](README.md)] | [中文]

---

## 特性

- 一键发布，自动化程度高
- 自动验证 SKILL.md 格式
- 支持私有/公开仓库
- 支持自定义分支
- 可选分支保护

---

## 安装

```bash
npx skills add Stanley-baby/skill-publisher
```

---

## 自然语言使用示例

### Claude Code / Open Code / Codex

直接告诉你的 AI 助手你想要什么：

```
/publish-skill

# 或者用自然语言：
发布这个 skill 到 GitHub

# 发布到功能分支：
发布这个 skill 到 dev 分支

# 发布并开启分支保护：
发布这个 skill 并开启保护

# 先检查一下：
检查一下这个 skill 能不能发布
```

---

## CLI 参数选项

| 参数 | 说明 |
|------|------|
| `--private` | 创建私有仓库（默认公开） |
| `--dry-run` | 仅检查，不实际发布 |
| `--skip-verify` | 跳过 npx skills 验证 |
| `--branch BRANCH` | 发布到指定分支 |
| `--protect` | 开启分支保护 |
| `--update-readme` | 强制更新 README |

---

## 详细文档

# Skill Publisher

一键将 Claude Code Skill 发布到 GitHub，自动完成验证、补全、推送全流程。

## 前置条件

- `gh` CLI 已安装且已登录（`gh auth status`）
- Skill 目录包含有效的 `SKILL.md`（含 YAML frontmatter `name` + `description`）

## 发布流程

当用户要求发布 skill 时，运行发布脚本：

```bash
python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <skill_dir>
```

### 确定 skill 目录

- 如果用户说"发布这个 skill"且当前在某个 skill 目录 → 用当前目录
- 如果用户指定了 skill 名称 → 在 `~/.claude/skills/` 下查找
- 如果不确定 → 问用户要发布哪个 skill

### 脚本自动完成的步骤

1. **验证** SKILL.md 的 YAML frontmatter（name + description）
2. **检查** gh CLI 就绪状态
3. **创建** LICENSE（MIT，如果缺少）
4. **生成** README.md（从 SKILL.md 提取，如果缺少）
5. **初始化** git（如果需要）
6. **创建** GitHub 仓库并推送
7. **开启** 分支保护（可选）
8. **验证** `npx skills add` 可发现

### 参数选项

| 参数 | 说明 |
|------|------|
| `--private` | 创建私有仓库（默认公开） |
| `--dry-run` | 仅检查，不实际发布 |
| `--skip-verify` | 跳过 npx skills 验证 |
| `--github-user USER` | 指定 GitHub 用户名（默认自动获取） |
| `--branch BRANCH` | 发布到指定分支（默认 main，不存在则创建） |
| `--protect` | 开启分支保护（PR + 禁止强制推送） |

### 更新已发布的 skill

对已有 GitHub 仓库的 skill 再次运行同一命令，脚本会检测到仓库已存在，自动 commit + push 更新。

## 使用示例

```
用户：发布 yt-search-download 这个 skill
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py ~/.claude/skills/yt-search-download

用户：把当前 skill 发到 GitHub
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py .

用户：先检查一下能不能发布
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --dry-run

用户：发布到 dev 分支
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --branch dev

用户：发布并开启分支保护
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --protect

用户：发布到子分支并开启保护
执行：python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --branch dev --protect
```

## 分支保护说明

`--protect` 参数会为指定分支开启以下保护：

- ✅ **PR 必须通过** — 必须创建 Pull Request 才能合并
- ✅ **Code Owner 审核** — 必须有代码所有者审核
- ✅ **至少 1 人审核** — 合并前需要至少 1 人审批
- ✅ **禁止强制推送** — 禁止 `git push --force`
- ✅ **管理员也受限** — 管理员也必须遵守规则

## 发布完成后

向用户展示：
- GitHub 仓库 URL
- 安装命令：`npx skills add <user>/<skill-name>`
- 验证结果

---

## License

MIT
