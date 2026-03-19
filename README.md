# skill-publisher

<p align="center">
  <h1>Skill Publisher</h1>
  <p>One-click publish Claude Code Skills to GitHub, auto-validate, complete files, create repos, push and verify installation.</p>
</p>

[English] | [[中文](README_zh.md)]

---

## Features

- One-click publish, high automation
- Automatic SKILL.md format validation
- Support private/public repositories
- Support custom branches
- Optional branch protection

---

## Installation

```bash
npx skills add Stanley-baby/skill-publisher
```

---

## Natural Language Usage Examples

### Claude Code / Open Code / Codex

Just tell your AI assistant what you want:

```
/publish-skill

# Or in natural language:
publish this skill to GitHub

# Publish to a feature branch:
push this skill to dev branch

# Publish with branch protection:
publish this skill with protection

# Dry run first:
check if this skill can be published
```

---

## CLI Options

| Option | Description |
|--------|-------------|
| `--private` | Create private repo (default: public) |
| `--dry-run` | Check only, do not publish |
| `--skip-verify` | Skip npx skills verification |
| `--branch BRANCH` | Publish to specified branch |
| `--protect` | Enable branch protection |
| `--update-readme` | Force update README |

---

## Detailed Documentation

## Usage

When user wants to publish a skill to GitHub, execute the following steps:

1. Run the publish script
2. Validate SKILL.md format (name, description required)
3. Create LICENSE file (MIT)
4. Generate README.md and README_zh.md
5. Initialize git repository (if not exists)
6. Create GitHub repository via `gh repo create`
7. Push code to GitHub
8. Verify with `npx skills add`

### Parameter Options

| Parameters | Description |
|------|------|
| `--private` | Create a private repository (default: public) |
| `--dry-run` | Only check, do not actually publish |
| `--skip-verify` | Skip npx skills verification |
| `--github-user USER` | Specify GitHub username (auto-detect by default) |
| `--branch BRANCH` | Publish to specified branch (default: main, create if not exist) |
| `--protect` | Enable branch protection (PR + disable force push) |

### Update Published Skill

Run the same command on a skill that already has a GitHub repository. The script will detect that the repository already exists and automatically commit + push the update.

### Usage Example

```
User: Publish the yt-search-download skill
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py ~/.claude/skills/yt-search-download

User: Send the current skill to GitHub
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py .

User: First check if it can be published
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --dry-run

User: publish to dev branch
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --branch dev

User: Publish and enable branch protection
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --protect

User: Publish to sub-branch and turn on protection
Execution: python3 ~/.claude/skills/skill-publisher/scripts/publish_skill.py <dir> --branch dev --protect
```

### Branch Protection Instructions

The `--protect` parameter enables the following protection for the specified branch:

- ✅ **PR Required** — Must create a Pull Request to merge
- ✅ **At Least 1 Reviewer** — At least 1 person required to approve before merging
- ✅ **Force Push Disabled** — Disable `git push --force`
- ✅ **Admins Also Restricted** — Admins must also follow the rules

### After Publishing

Display to user:
- GitHub repository URL
- Installation command: `npx skills add <user>/<skill-name>`
- Verification result

---

## License

MIT
