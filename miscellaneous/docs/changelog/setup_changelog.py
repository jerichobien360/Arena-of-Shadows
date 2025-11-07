#!/usr/bin/env python3
"""
Setup script for changelog automation.
This will set up git hooks and create necessary files.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def create_git_hooks():
    """Create git hooks for automatic changelog updates."""
    hooks_dir = Path('.git/hooks')
    
    if not hooks_dir.exists():
        print("❌ Not in a git repository. Initialize git first.")
        return False
    
    # Pre-commit hook to validate changelog
    pre_commit_content = '''#!/bin/sh
# Auto-generated pre-commit hook for changelog validation

python3 changelog_automation.py validate
if [ $? -ne 0 ]; then
    echo "❌ Changelog validation failed. Please fix issues before committing."
    exit 1
fi
'''
    
    pre_commit_path = hooks_dir / 'pre-commit'
    with open(pre_commit_path, 'w') as f:
        f.write(pre_commit_content)
    
    # Make hook executable
    os.chmod(pre_commit_path, 0o755)
    
    # Post-commit hook to suggest changelog updates
    post_commit_content = '''#!/bin/sh
# Auto-generated post-commit hook for changelog reminders

echo "💡 Don't forget to update CHANGELOG.md with your changes!"
echo "   Run: python3 changelog_automation.py add"
'''
    
    post_commit_path = hooks_dir / 'post-commit'
    with open(post_commit_path, 'w') as f:
        f.write(post_commit_content)
    
    os.chmod(post_commit_path, 0o755)
    
    print("✅ Git hooks created successfully")
    return True

def create_makefile():
    """Create a Makefile with changelog commands."""
    makefile_content = '''# Changelog automation commands

.PHONY: changelog-init changelog-add changelog-release changelog-auto changelog-validate

changelog-init:
	@python3 changelog_automation.py init

changelog-add:
	@python3 changelog_automation.py add

changelog-release:
	@python3 changelog_automation.py release

changelog-auto:
	@python3 changelog_automation.py auto

changelog-validate:
	@python3 changelog_automation.py validate

# Shortcuts
cl-init: changelog-init
cl-add: changelog-add
cl-release: changelog-release
cl-auto: changelog-auto
cl-validate: changelog-validate

help-changelog:
	@echo "Changelog commands:"
	@echo "  make changelog-init     - Initialize new CHANGELOG.md"
	@echo "  make changelog-add      - Add new entry interactively"
	@echo "  make changelog-release  - Create a new release"
	@echo "  make changelog-auto     - Auto-generate from git commits"
	@echo "  make changelog-validate - Validate changelog format"
	@echo ""
	@echo "Shortcuts: cl-init, cl-add, cl-release, cl-auto, cl-validate"
'''
    
    makefile_path = Path('Makefile.changelog')
    with open(makefile_path, 'w') as f:
        f.write(makefile_content)
    
    print("✅ Created Makefile.changelog")
    print("   Include it in your main Makefile with: include Makefile.changelog")

def create_vscode_tasks():
    """Create VS Code tasks for changelog operations."""
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    tasks_config = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Changelog: Add Entry",
                "type": "shell",
                "command": "python3",
                "args": ["changelog_automation.py", "add"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Changelog: Create Release",
                "type": "shell",
                "command": "python3",
                "args": ["changelog_automation.py", "release"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Changelog: Auto Generate",
                "type": "shell",
                "command": "python3",
                "args": ["changelog_automation.py", "auto"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Changelog: Validate",
                "type": "shell",
                "command": "python3",
                "args": ["changelog_automation.py", "validate"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            }
        ]
    }
    
    tasks_path = vscode_dir / 'tasks.json'
    
    # If tasks.json exists, merge with existing tasks
    if tasks_path.exists():
        try:
            with open(tasks_path, 'r') as f:
                existing_config = json.load(f)
            
            if 'tasks' not in existing_config:
                existing_config['tasks'] = []
            
            # Add our tasks to existing ones
            existing_config['tasks'].extend(tasks_config['tasks'])
            tasks_config = existing_config
        except json.JSONDecodeError:
            print("⚠️  Existing tasks.json is malformed. Creating backup.")
            backup_path = tasks_path.with_suffix('.json.backup')
            tasks_path.rename(backup_path)
    
    with open(tasks_path, 'w') as f:
        json.dump(tasks_config, f, indent=2)
    
    print("✅ VS Code tasks created/updated")

def create_github_workflow():
    """Create GitHub Actions workflow for changelog validation."""
    workflows_dir = Path('.github/workflows')
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Changelog Validation

on:
  pull_request:
    branches: [ main, master, develop ]
  push:
    branches: [ main, master, develop ]

jobs:
  validate-changelog:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Validate Changelog
      run: |
        python3 changelog_automation.py validate
    
    - name: Check for Unreleased Changes
      run: |
        if ! grep -q "## \[Unreleased\]" CHANGELOG.md; then
          echo "❌ Missing [Unreleased] section in CHANGELOG.md"
          exit 1
        fi
        
        # Check if there are changes in Unreleased (for PRs)
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          unreleased_content=$(sed -n '/## \[Unreleased\]/,/## \[/p' CHANGELOG.md | head -n -1 | tail -n +2)
          if [ -z "$unreleased_content" ] || [ "$unreleased_content" = " " ]; then
            echo "⚠️  No changes found in [Unreleased] section. Consider adding changelog entries."
          else
            echo "✅ Changes found in [Unreleased] section"
          fi
        fi
'''
    
    workflow_path = workflows_dir / 'changelog.yml'
    with open(workflow_path, 'w') as f:
        f.write(workflow_content)
    
    print("✅ GitHub Actions workflow created")

def main():
    print("🚀 Setting up changelog automation...")
    
    # Check if we're in a Python project
    if not (Path('setup.py').exists() or Path('pyproject.toml').exists() or Path('requirements.txt').exists()):
        print("⚠️  This doesn't appear to be a Python project. Continue anyway? (y/N): ", end='')
        if input().lower() != 'y':
            sys.exit(0)
    
    # Create changelog files if they don't exist
    if not Path('changelog_automation.py').exists():
        print("❌ changelog_automation.py not found. Please ensure it's in the current directory.")
        sys.exit(1)
    
    if not Path('changelog_config.py').exists():
        print("❌ changelog_config.py not found. Please ensure it's in the current directory.")
        sys.exit(1)
    
    # Initialize changelog if it doesn't exist
    if not Path('CHANGELOG.md').exists():
        print("📝 Initializing CHANGELOG.md...")
        subprocess.run([sys.executable, 'changelog_automation.py', 'init'])
    
    # Create git hooks
    if Path('.git').exists():
        create_git_hooks()
        create_github_workflow()
    else:
        print("⚠️  Not a git repository. Skipping git hooks and GitHub workflow.")
    
    # Create development tools
    create_makefile()
    create_vscode_tasks()
    
    # Create alias script for convenience
    alias_content = '''#!/bin/bash
# Changelog automation aliases

alias cl-init="python3 changelog_automation.py init"
alias cl-add="python3 changelog_automation.py add"
alias cl-release="python3 changelog_automation.py release"
alias cl-auto="python3 changelog_automation.py auto"
alias cl-validate="python3 changelog_automation.py validate"

echo "Changelog aliases loaded:"
echo "  cl-init, cl-add, cl-release, cl-auto, cl-validate"
'''
    
    with open('.changelog_aliases.sh', 'w') as f:
        f.write(alias_content)
    
    print("✅ Created .changelog_aliases.sh")
    print("   Source it with: source .changelog_aliases.sh")
    
    print("\n🎉 Changelog automation setup complete!")
    print("\nQuick start:")
    print("1. Initialize: python3 changelog_automation.py init")
    print("2. Add entry: python3 changelog_automation.py add")
    print("3. Auto-generate: python3 changelog_automation.py auto")
    print("4. Create release: python3 changelog_automation.py release")
    print("5. Validate: python3 changelog_automation.py validate")
    
    print("\nOr use shortcuts (after sourcing aliases):")
    print("cl-add, cl-auto, cl-release, cl-validate")

if __name__ == '__main__':
    main()
