#!/usr/bin/env python3
"""
Skill Publisher - Publish Claude Code Skills to GitHub
"""

import os
import sys
import re
import subprocess
import argparse
import json
import datetime
import fnmatch

PRIVACY_PATTERNS = ['memory/', 'data/', 'private/', '.env', '*.log']


def filter_privacy_files(skill_dir):
    filtered = []
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if any(fnmatch.fnmatch(d, p.rstrip('/')) for p in PRIVACY_PATTERNS):
                filtered.append(os.path.join(root, d))
        for f in files:
            if any(fnmatch.fnmatch(f, p) for p in PRIVACY_PATTERNS):
                filtered.append(os.path.join(root, f))
    return filtered


def run(cmd, capture=True, check=True, cwd=None):
    if isinstance(cmd, list):
        r = subprocess.run(cmd, capture_output=capture, text=True, cwd=cwd)
    else:
        r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, cwd=cwd)
    if check and r.returncode != 0:
        return None
    return r.stdout.strip() if capture else ""


def check_prerequisites():
    if not run("which gh"):
        print("[ERROR] gh CLI not found. Install: brew install gh", file=sys.stderr)
        return False
    auth = run("gh auth status 2>&1", check=False)
    if auth is None or "not logged" in (auth or ""):
        print("[ERROR] gh not logged in. Run: gh auth login", file=sys.stderr)
        return False
    return True


def parse_yaml_frontmatter(skill_md_path):
    with open(skill_md_path, "r") as f:
        content = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None, None
    yaml_block = m.group(1)
    name_m = re.search(r"^name:\s*(.+)$", yaml_block, re.MULTILINE)
    name = name_m.group(1).strip().strip("'\"") if name_m else None

    desc = None
    desc_m = re.search(r"^description:\s*[|>]\s*\n((?:[ \t]+.+\n?)+)", yaml_block, re.MULTILINE)
    if desc_m:
        lines = desc_m.group(1).split("\n")
        desc = " ".join(line.strip() for line in lines if line.strip())
    else:
        desc_m = re.search(r"^description:\s*(.+)$", yaml_block, re.MULTILINE)
        if desc_m:
            desc = desc_m.group(1).strip().strip("'\"")
    return name, desc


def get_github_user():
    return run("gh api user --jq '.login'")


def validate_skill(skill_dir):
    errors = []
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return errors, None, None

    name, desc = parse_yaml_frontmatter(skill_md)
    if not name:
        errors.append("SKILL.md missing name field")
    if not desc:
        errors.append("SKILL.md missing description field")
    if desc and len(desc) < 20:
        errors.append(f"description too short ({len(desc)} chars), recommend 50+")

    return errors, name, desc


def ensure_license(skill_dir, github_user):
    license_path = os.path.join(skill_dir, "LICENSE")
    if os.path.exists(license_path):
        return False
    year = datetime.datetime.now().year
    full_name = run("git config user.name") or github_user
    content = f"""MIT License

Copyright (c) {year} {full_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    with open(license_path, "w") as f:
        f.write(content)
    return True


def generate_readme(skill_dir, name, desc, github_user, force=False):
    """Generate bilingual README.md and README_zh.md from SKILL.md content."""
    readme_path = os.path.join(skill_dir, "README.md")
    readme_zh_path = os.path.join(skill_dir, "README_zh.md")
    if os.path.exists(readme_path) and os.path.exists(readme_zh_path) and not force:
        return False
    
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md, "r") as f:
        content = f.read()
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL).strip()
    
    first_heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = first_heading.group(1) if first_heading else name
    
    short_desc = desc.split("。")[0] + "." if "。" in desc else desc[:100]
    
    # English README
    readme_en = f"""# {name}

<p align="center">
  <h1>{title}</h1>
  <p>{short_desc}</p>
</p>

[[English](README.md)] | [[中文](README_zh.md)]

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
npx skills add {github_user}/{name}
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

RH|For complete documentation, see [README_zh.md](README_zh.md).
TV|

---

## License

MIT
"""
    
    # Chinese README
    readme_zh = f"""# {name}

<p align="center">
  <h1>{title}</h1>
  <p>{short_desc}</p>
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
npx skills add {github_user}/{name}
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

{body}

---

## License

MIT
"""
    
    with open(readme_path, "w") as f:
        f.write(readme_en)
    
    with open(readme_zh_path, "w") as f:
        f.write(readme_zh)
    
    return True


def init_git(skill_dir):
    git_dir = os.path.join(skill_dir, ".git")
    if os.path.isdir(git_dir):
        return False
    run(f"git init", cwd=skill_dir)
    return True


def protect_branch(github_user, repo, branch="main"):
    print(f"[INFO] Enabling branch protection: {branch}")

    protection_data = {
        "required_pull_request_reviews": {
            "required_approving_review_count": 1
        },
        "required_status_checks": None,
        "restrictions": None,
        "enforce_admins": True,
        "allow_force_pushes": False
    }

    check = run(
        f"gh api repos/{github_user}/{repo}/branches/{branch}/protection",
        check=False
    )

    if check and "url" in (check or ""):
        print(f"[INFO] Branch {branch} protection already exists")
        return True

    json_str = json.dumps(protection_data)
    create_result = run(
        f'echo \'{json_str}\' | gh api -X PUT repos/{github_user}/{repo}/branches/{branch}/protection --input -',
        check=False
    )

    if create_result and ("url" in (create_result or "") or "html_url" in (create_result or "")):
        print(f"[OK] Branch {branch} protection enabled (PR + no force push)")
        return True

    print(f"[WARNING] Branch protection may not be fully applied")
    return False


def create_and_push(skill_dir, name, desc, github_user, public=True, branch=None, protect=False):
    visibility = "--public" if public else "--private"
    target_branch = branch or "main"

    existing = run(f"gh repo view {github_user}/{name} --json url --jq '.url' 2>/dev/null", check=False)
    if existing and "github.com" in existing:
        print(f"[INFO] Repo exists: {existing}")
        run("git add -A", cwd=skill_dir)
        status = run("git status --porcelain", cwd=skill_dir)
        if status:
            run('git commit -m "Update skill"', cwd=skill_dir)
        remote = run("git remote get-url origin 2>/dev/null", cwd=skill_dir, check=False)
        if not remote:
            run(f"git remote add origin https://github.com/{github_user}/{name}.git", cwd=skill_dir)
        remote_branch = run(f"git ls-remote --heads origin {target_branch}", cwd=skill_dir, check=False)
        if not remote_branch:
            print(f"[INFO] Branch {target_branch} not found, will create")
        run(f"git push -u origin HEAD:{target_branch} 2>&1", cwd=skill_dir, check=False)

        if protect:
            protect_branch(github_user, name, target_branch)

        return existing

    gh_desc = desc[:150] if len(desc) > 150 else desc

    run("git add -A", cwd=skill_dir)
    run(f'git commit -m "Initial release: {name}"', cwd=skill_dir)

    result = run(
        ["gh", "repo", "create", f"{github_user}/{name}", visibility,
         "--description", gh_desc, "--source", ".", "--push"],
        cwd=skill_dir, check=False
    )
    if result and "github.com" in result:
        url = result.strip().split("\n")[0]
        if branch and branch != "main":
            print(f"[INFO] Push to branch: {branch}")
            run(f"git push -u origin HEAD:{branch} 2>&1", cwd=skill_dir, check=False)

        if protect:
            protect_branch(github_user, name, target_branch)

        return url
    print(f"[ERROR] Failed to create repo: {result}", file=sys.stderr)
    return None


def verify_skill(github_user, name):
    result = run(f"npx skills add {github_user}/{name} --list 2>&1", check=False)
    if result and name in result:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Publish Claude Code Skill to GitHub")
    parser.add_argument("skill_dir", help="Skill directory path")
    parser.add_argument("--github-user", help="GitHub username (default: auto-detect)")
    parser.add_argument("--private", action="store_true", help="Create private repo (default: public)")
    parser.add_argument("--dry-run", action="store_true", help="Check only, do not publish")
    parser.add_argument("--skip-verify", action="store_true", help="Skip npx skills verification")
    parser.add_argument("--branch", help="Publish to specified branch (default: main)")
    parser.add_argument("--protect", action="store_true", help="Enable branch protection")
    parser.add_argument("--update-readme", action="store_true", help="Force update README")
    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)
    if not os.path.isdir(skill_dir):
        print(f"[ERROR] Directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[CHECK] Skill: {skill_dir}\n")

    errors, name, desc = validate_skill(skill_dir)
    if errors:
        print("[FAIL] Validation failed:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    print(f"[OK] SKILL.md validated (name: {name})")

    if not check_prerequisites():
        sys.exit(1)
    print("[OK] gh CLI ready")

    github_user = args.github_user or get_github_user()
    if not github_user:
        print("[ERROR] Cannot get GitHub username", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] GitHub user: {github_user}")

    if ensure_license(skill_dir, github_user):
        print("[FILE] LICENSE created (MIT)")
    else:
        print("[OK] LICENSE exists")

    if generate_readme(skill_dir, name, desc, github_user, force=args.update_readme):
        print("[FILE] README generated")
    else:
        if args.update_readme:
            print("[FILE] README updated")
        else:
            print("[OK] README exists")

    filtered = filter_privacy_files(skill_dir)
    if filtered:
        print(f"[WARN] Privacy files/dirs detected: {len(filtered)} (will be excluded)")
        for f in filtered[:5]:
            print(f"   - {os.path.relpath(f, skill_dir)}")
        if len(filtered) > 5:
            print(f"   ... and {len(filtered)-5} more")
        print()

    if args.dry_run:
        print(f"\n[DRY-RUN] Use this command to publish:")
        print(f"   python3 {__file__} {skill_dir}")
        return

    if init_git(skill_dir):
        print("[GIT] Repository initialized")
    else:
        print("[OK] Git repository exists")

    public = not args.private
    print(f"\n[PUBLISH] Publishing to GitHub ({'public' if public else 'private'})...")
    url = create_and_push(skill_dir, name, desc, github_user, public=public,
                         branch=args.branch, protect=args.protect)
    if not url:
        print("[ERROR] Publish failed", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] GitHub: {url}")

    if not args.skip_verify:
        print("\n[VERIFY] Checking npx skills discoverability...")
        if verify_skill(github_user, name):
            print("[OK] Verification passed")
        else:
            print("[WARN] Verification may need retry")

    print(f"\n{'='*60}")
    print(f"[SUCCESS] Published!")
    print(f"   Repo: {url}")
    print(f"   Install: npx skills add {github_user}/{name}")
    if args.protect:
        branch_name = args.branch or "main"
        print(f"   Protection: {branch_name} branch protected")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
