#!/usr/bin/env python3
"""
Skill Publisher — 检查并发布 Claude Code Skill 到 GitHub

用法:
  python3 publish_skill.py <skill_dir> [--github-user USER] [--public/--private] [--dry-run]

流程:
  1. 验证 SKILL.md (YAML frontmatter)
  2. 检查/创建 LICENSE
  3. 生成 README.md
  4. 初始化 git (如需)
  5. 创建 GitHub repo + push
  6. 验证 npx skills 可发现
"""

import os
import sys
import re
import subprocess
import argparse
import json
import datetime


def run(cmd, capture=True, check=True, cwd=None):
    """Run a shell command and return stdout."""
    if isinstance(cmd, list):
        r = subprocess.run(cmd, capture_output=capture, text=True, cwd=cwd)
    else:
        r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, cwd=cwd)
    if check and r.returncode != 0:
        return None
    return r.stdout.strip() if capture else ""


def check_prerequisites():
    """Check gh CLI is available and authenticated."""
    if not run("which gh"):
        print("[错误] 未找到 gh CLI。安装方式: brew install gh", file=sys.stderr)
        return False
    auth = run("gh auth status 2>&1", check=False)
    if auth is None or "not logged" in (auth or ""):
        print("[错误] gh 未登录。运行: gh auth login", file=sys.stderr)
        return False
    return True


def parse_yaml_frontmatter(skill_md_path):
    """Extract name and description from SKILL.md YAML frontmatter."""
    with open(skill_md_path, "r") as f:
        content = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None, None
    yaml_block = m.group(1)
    name_m = re.search(r"^name:\s*(.+)$", yaml_block, re.MULTILINE)
    name = name_m.group(1).strip().strip("'\"") if name_m else None

    # Extract description - handle multiple YAML formats:
    # 1. description: "single line"
    # 2. description: |
    #      multi-line indented text
    # 3. description: >
    #      folded text
    desc = None
    desc_m = re.search(r"^description:\s*[|>]\s*\n((?:[ \t]+.+\n?)+)", yaml_block, re.MULTILINE)
    if desc_m:
        # Multi-line: strip leading whitespace from each line and join
        lines = desc_m.group(1).split("\n")
        desc = " ".join(line.strip() for line in lines if line.strip())
    else:
        desc_m = re.search(r"^description:\s*(.+)$", yaml_block, re.MULTILINE)
        if desc_m:
            desc = desc_m.group(1).strip().strip("'\"")
    return name, desc


def get_github_user():
    """Get current GitHub username."""
    return run("gh api user --jq '.login'")


def validate_skill(skill_dir):
    """Validate skill directory structure."""
    errors = []
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md")
        return errors, None, None

    name, desc = parse_yaml_frontmatter(skill_md)
    if not name:
        errors.append("SKILL.md 缺少 YAML frontmatter 中的 name 字段")
    if not desc:
        errors.append("SKILL.md 缺少 YAML frontmatter 中的 description 字段")
    if desc and len(desc) < 20:
        errors.append(f"description 太短 ({len(desc)} 字符)，建议至少 50 字符")

    return errors, name, desc


def ensure_license(skill_dir, github_user):
    """Create MIT LICENSE if missing."""
    license_path = os.path.join(skill_dir, "LICENSE")
    if os.path.exists(license_path):
        return False
    year = datetime.datetime.now().year
    # Try to get full name from git config
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


def generate_readme(skill_dir, name, desc, github_user):
    """Generate README.md from SKILL.md content."""
    readme_path = os.path.join(skill_dir, "README.md")
    if os.path.exists(readme_path):
        return False

    # Read SKILL.md body (after frontmatter)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md, "r") as f:
        content = f.read()
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL).strip()

    # Extract first heading or use name
    first_heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = first_heading.group(1) if first_heading else name

    # Build short desc (first line of description)
    short_desc = desc.split("。")[0] + "。" if "。" in desc else desc[:100]

    readme = f"""# {name}

{short_desc}

## 安装

```bash
npx skills add {github_user}/{name}
```

{body}

## License

MIT

## 📱 关注作者

如果这个项目对你有帮助，欢迎关注我获取更多技术分享：

- **X (Twitter)**: [@vista8](https://x.com/vista8)
- **微信公众号「向阳乔木推荐看」**:

<p align="center">
  <img src="https://github.com/joeseesun/terminal-boost/raw/main/assets/wechat-qr.jpg?raw=true" alt="向阳乔木推荐看公众号二维码" width="300">
</p>
"""
    with open(readme_path, "w") as f:
        f.write(readme)
    return True


def init_git(skill_dir):
    """Initialize git repo if needed."""
    git_dir = os.path.join(skill_dir, ".git")
    if os.path.isdir(git_dir):
        return False
    run(f"git init", cwd=skill_dir)
    return True


def create_and_push(skill_dir, name, desc, github_user, public=True):
    """Create GitHub repo and push."""
    visibility = "--public" if public else "--private"

    # Check if repo already exists
    existing = run(f"gh repo view {github_user}/{name} --json url --jq '.url' 2>/dev/null", check=False)
    if existing and "github.com" in existing:
        print(f"[信息] 仓库已存在: {existing}")
        # Just push updates
        run("git add -A", cwd=skill_dir)
        status = run("git status --porcelain", cwd=skill_dir)
        if status:
            run('git commit -m "Update skill"', cwd=skill_dir)
        # Check if remote exists
        remote = run("git remote get-url origin 2>/dev/null", cwd=skill_dir, check=False)
        if not remote:
            run(f"git remote add origin https://github.com/{github_user}/{name}.git", cwd=skill_dir)
        run("git push -u origin main 2>&1", cwd=skill_dir, check=False)
        run("git push -u origin HEAD:main 2>&1", cwd=skill_dir, check=False)
        return existing

    # Short description for GitHub (max 350 chars)
    gh_desc = desc[:150] if len(desc) > 150 else desc

    # Commit all files
    run("git add -A", cwd=skill_dir)
    run(f'git commit -m "Initial release: {name}"', cwd=skill_dir)

    # Create repo and push
    result = run(
        ["gh", "repo", "create", f"{github_user}/{name}", visibility,
         "--description", gh_desc, "--source", ".", "--push"],
        cwd=skill_dir, check=False
    )
    if result and "github.com" in result:
        url = result.strip().split("\n")[0]
        return url
    print(f"[错误] 创建仓库失败: {result}", file=sys.stderr)
    return None


def verify_skill(github_user, name):
    """Verify skill is discoverable via npx skills."""
    result = run(f"npx skills add {github_user}/{name} --list 2>&1", check=False)
    if result and name in result:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="发布 Claude Code Skill 到 GitHub")
    parser.add_argument("skill_dir", help="Skill 目录路径")
    parser.add_argument("--github-user", help="GitHub 用户名 (默认自动获取)")
    parser.add_argument("--private", action="store_true", help="创建私有仓库 (默认公开)")
    parser.add_argument("--dry-run", action="store_true", help="仅检查，不实际发布")
    parser.add_argument("--skip-verify", action="store_true", help="跳过 npx skills 验证")
    args = parser.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)
    if not os.path.isdir(skill_dir):
        print(f"[错误] 目录不存在: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n🔍 检查 Skill: {skill_dir}\n")

    # Step 1: Validate
    errors, name, desc = validate_skill(skill_dir)
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    print(f"✅ SKILL.md 验证通过 (name: {name})")

    # Step 2: Prerequisites
    if not check_prerequisites():
        sys.exit(1)
    print("✅ gh CLI 已就绪")

    github_user = args.github_user or get_github_user()
    if not github_user:
        print("[错误] 无法获取 GitHub 用户名", file=sys.stderr)
        sys.exit(1)
    print(f"✅ GitHub 用户: {github_user}")

    # Step 3: Ensure LICENSE
    if ensure_license(skill_dir, github_user):
        print("📄 已创建 LICENSE (MIT)")
    else:
        print("✅ LICENSE 已存在")

    # Step 4: Generate README
    if generate_readme(skill_dir, name, desc, github_user):
        print("📄 已生成 README.md")
    else:
        print("✅ README.md 已存在")

    if args.dry_run:
        print(f"\n🏁 Dry run 完成。实际发布命令:")
        print(f"   python3 {__file__} {skill_dir}")
        return

    # Step 5: Git init
    if init_git(skill_dir):
        print("📦 已初始化 git 仓库")
    else:
        print("✅ git 仓库已存在")

    # Step 6: Create repo and push
    public = not args.private
    print(f"\n🚀 发布到 GitHub ({'公开' if public else '私有'})...")
    url = create_and_push(skill_dir, name, desc, github_user, public=public)
    if not url:
        print("❌ 发布失败", file=sys.stderr)
        sys.exit(1)
    print(f"✅ GitHub: {url}")

    # Step 7: Verify
    if not args.skip_verify:
        print("\n🔎 验证 npx skills 可发现...")
        if verify_skill(github_user, name):
            print("✅ 验证通过")
        else:
            print("⚠️  验证未通过（可能需要等待几秒后重试）")

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 发布成功！")
    print(f"   仓库: {url}")
    print(f"   安装: npx skills add {github_user}/{name}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
