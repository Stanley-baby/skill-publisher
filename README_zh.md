# skill-publisher

<p align="center">
  <h1>Skill Publisher</h1>
  <p>一键发布 Claude Code Skill 到 GitHub，自动验证、补全文件、创建仓库、推送并验证可安装.</p>
</p>

[[English](README.md)] | [[中文](README_zh.md)]

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

一键将 Claude Code Skill 发布到 GitHub ，自动完成验证、补全、推送全流程。

# #

 前置条件- `gh` CLI 已安装且已登录（ `gh auth status` ）
-技能目录包含有效的`SKILL.md` （含 YAML frontmatter `name` + `description` ）

# #

 发布流程当用户要求发布 skill 时，技能运行发布脚本：

`` `bash
python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <skill_dir>
`` `

# # #确定技能 目录

- 如果用户说“发布这个技能”且当前在某个技能 目录 → 用当前目录
- 如果用户指定了 skill 名称 → 在 `~/.claude/skills/` 下查找
-如果不确定 → 问用户要发布哪个 技能

### 脚本自动完成的步骤

1. * *验证 * * SKILL.md 的 YAML frontmatter （ na

---

## License

MIT
