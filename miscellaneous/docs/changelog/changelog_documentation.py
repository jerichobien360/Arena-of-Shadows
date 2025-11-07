#!/usr/bin/env python3
"""
CHANGELOG.md Automation Tool

This script helps automate the creation and maintenance of CHANGELOG.md files
following the Keep a Changelog format (https://keepachangelog.com/).

Usage:
    python changelog_automation.py init          # Initialize a new CHANGELOG.md
    python changelog_automation.py add           # Add a new entry interactively
    python changelog_automation.py release      # Create a new release
    python changelog_automation.py auto         # Auto-generate from git commits
    python changelog_automation.py validate     # Validate existing CHANGELOG.md
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
import argparse

class ChangelogAutomation:
    def __init__(self, changelog_path: str = "CHANGELOG.md"):
        self.changelog_path = changelog_path
        self.template = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
        
    def init_changelog(self) -> None:
        """Initialize a new CHANGELOG.md file."""
        if os.path.exists(self.changelog_path):
            response = input(f"{self.changelog_path} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        with open(self.changelog_path, 'w') as f:
            f.write(self.template)
        
        print(f"✅ Created {self.changelog_path}")
    
    def read_changelog(self) -> str:
        """Read the existing changelog content."""
        if not os.path.exists(self.changelog_path):
            print(f"❌ {self.changelog_path} not found. Run 'init' first.")
            sys.exit(1)
        
        with open(self.changelog_path, 'r') as f:
            return f.read()
    
    def write_changelog(self, content: str) -> None:
        """Write content to the changelog file."""
        with open(self.changelog_path, 'w') as f:
            f.write(content)
    
    def add_entry(self) -> None:
        """Add a new entry to the Unreleased section interactively."""
        content = self.read_changelog()
        
        print("\n📝 Adding a new changelog entry")
        print("Available categories:")
        categories = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        
        while True:
            try:
                choice = int(input("\nSelect category (1-6): "))
                if 1 <= choice <= 6:
                    category = categories[choice - 1]
                    break
                else:
                    print("Invalid choice. Please select 1-6.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        description = input("Enter description: ").strip()
        if not description:
            print("❌ Description cannot be empty.")
            return
        
        # Find the Unreleased section and add the entry
        unreleased_pattern = r'(## \[Unreleased\])\n'
        match = re.search(unreleased_pattern, content)
        
        if not match:
            print("❌ Could not find [Unreleased] section.")
            return
        
        # Check if the category already exists in Unreleased
        category_pattern = f'### {category}\n'
        unreleased_start = match.end()
        next_version_pattern = r'\n## \[\d+\.\d+\.\d+\]'
        next_version_match = re.search(next_version_pattern, content[unreleased_start:])
        
        if next_version_match:
            unreleased_end = unreleased_start + next_version_match.start()
            unreleased_section = content[unreleased_start:unreleased_end]
        else:
            unreleased_section = content[unreleased_start:]
        
        if category_pattern in unreleased_section:
            # Add to existing category
            category_match = re.search(f'(### {category}\n)', unreleased_section)
            if category_match:
                insert_pos = unreleased_start + category_match.end()
                new_entry = f"- {description}\n"
                content = content[:insert_pos] + new_entry + content[insert_pos:]
        else:
            # Create new category
            insert_pos = unreleased_start
            new_section = f"\n### {category}\n- {description}\n"
            content = content[:insert_pos] + new_section + content[insert_pos:]
        
        self.write_changelog(content)
        print(f"✅ Added '{description}' to {category} section")
    
    def create_release(self) -> None:
        """Create a new release by moving Unreleased items to a versioned section."""
        content = self.read_changelog()
        
        # Get version number
        version = input("Enter version number (e.g., 1.0.0): ").strip()
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print("❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)")
            return
        
        # Check if version already exists
        if f"## [{version}]" in content:
            print(f"❌ Version {version} already exists in changelog.")
            return
        
        # Get release date
        use_today = input("Use today's date? (Y/n): ").strip().lower()
        if use_today in ['', 'y', 'yes']:
            date = datetime.now().strftime('%Y-%m-%d')
        else:
            date = input("Enter release date (YYYY-MM-DD): ").strip()
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                print("❌ Invalid date format. Use YYYY-MM-DD")
                return
        
        # Find Unreleased section
        unreleased_pattern = r'(## \[Unreleased\])\n'
        match = re.search(unreleased_pattern, content)
        
        if not match:
            print("❌ Could not find [Unreleased] section.")
            return
        
        # Find the content between Unreleased and next version
        unreleased_start = match.end()
        next_version_pattern = r'\n## \[\d+\.\d+\.\d+\]'
        next_version_match = re.search(next_version_pattern, content[unreleased_start:])
        
        if next_version_match:
            unreleased_end = unreleased_start + next_version_match.start()
            unreleased_content = content[unreleased_start:unreleased_end].strip()
        else:
            unreleased_content = content[unreleased_start:].strip()
        
        if not unreleased_content or unreleased_content == "":
            print("❌ No changes in Unreleased section to release.")
            return
        
        # Create new release section
        new_release = f"## [{version}] - {date}\n\n{unreleased_content}\n\n"
        
        # Replace Unreleased section with empty one and add new release
        new_unreleased = "## [Unreleased]\n\n"
        
        if next_version_match:
            new_content = (content[:match.start()] + new_unreleased + new_release + 
                          content[unreleased_end:])
        else:
            new_content = content[:match.start()] + new_unreleased + new_release
        
        self.write_changelog(new_content)
        print(f"✅ Created release {version} ({date})")
    
    def auto_generate_from_git(self) -> None:
        """Auto-generate changelog entries from git commits since last release."""
        try:
            # Get the last release tag
            result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                last_tag = result.stdout.strip()
                commit_range = f"{last_tag}..HEAD"
            else:
                commit_range = "HEAD"
            
            # Get commits since last release
            result = subprocess.run(['git', 'log', '--pretty=format:%s', commit_range], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Not a git repository or git not available.")
                return
            
            commits = result.stdout.strip().split('\n')
            if not commits or commits == ['']:
                print("ℹ️  No new commits found.")
                return
            
            print(f"\n📝 Found {len(commits)} commits to process:")
            
            # Categorize commits based on conventional commit patterns
            categorized = {
                'Added': [],
                'Changed': [],
                'Fixed': [],
                'Security': [],
                'Removed': [],
                'Deprecated': []
            }
            
            for commit in commits:
                commit = commit.strip()
                if not commit:
                    continue
                
                # Basic categorization based on commit message patterns
                if commit.lower().startswith(('feat:', 'feature:')):
                    categorized['Added'].append(commit)
                elif commit.lower().startswith(('fix:', 'bugfix:')):
                    categorized['Fixed'].append(commit)
                elif commit.lower().startswith(('refactor:', 'update:', 'change:')):
                    categorized['Changed'].append(commit)
                elif commit.lower().startswith(('remove:', 'delete:')):
                    categorized['Removed'].append(commit)
                elif commit.lower().startswith('security:'):
                    categorized['Security'].append(commit)
                elif commit.lower().startswith('deprecate:'):
                    categorized['Deprecated'].append(commit)
                else:
                    # Default to Changed for unclear commits
                    categorized['Changed'].append(commit)
            
            # Show categorized commits and let user approve
            for category, items in categorized.items():
                if items:
                    print(f"\n{category}:")
                    for item in items:
                        print(f"  - {item}")
            
            confirm = input("\nAdd these entries to changelog? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborted.")
                return
            
            # Add entries to changelog
            content = self.read_changelog()
            unreleased_pattern = r'(## \[Unreleased\])\n'
            match = re.search(unreleased_pattern, content)
            
            if not match:
                print("❌ Could not find [Unreleased] section.")
                return
            
            insert_pos = match.end()
            new_content = ""
            
            for category, items in categorized.items():
                if items:
                    new_content += f"\n### {category}\n"
                    for item in items:
                        # Clean up conventional commit prefixes
                        clean_item = re.sub(r'^(feat|fix|refactor|update|change|remove|delete|security|deprecate):\s*', '', item, flags=re.IGNORECASE)
                        new_content += f"- {clean_item}\n"
            
            if new_content:
                new_content += "\n"
                content = content[:insert_pos] + new_content + content[insert_pos:]
                self.write_changelog(content)
                print("✅ Auto-generated changelog entries added")
            else:
                print("ℹ️  No entries to add")
                
        except FileNotFoundError:
            print("❌ Git not found. Please install git to use auto-generation.")
    
    def validate_changelog(self) -> None:
        """Validate the changelog format."""
        content = self.read_changelog()
        issues = []
        
        # Check for required sections
        if "# Changelog" not in content:
            issues.append("Missing main heading '# Changelog'")
        
        if "## [Unreleased]" not in content:
            issues.append("Missing '[Unreleased]' section")
        
        # Check for proper version format
        version_pattern = r'## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}'
        versions = re.findall(version_pattern, content)
        
        # Check for proper category headings
        valid_categories = {'Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security'}
        category_pattern = r'### (\w+)'
        categories = re.findall(category_pattern, content)
        
        invalid_categories = set(categories) - valid_categories
        if invalid_categories:
            issues.append(f"Invalid categories found: {', '.join(invalid_categories)}")
        
        if issues:
            print("❌ Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Changelog format is valid")
            if versions:
                print(f"ℹ️  Found {len(versions)} released versions")

def main():
    parser = argparse.ArgumentParser(description='CHANGELOG.md Automation Tool')
    parser.add_argument('command', choices=['init', 'add', 'release', 'auto', 'validate'],
                       help='Command to execute')
    parser.add_argument('--file', '-f', default='CHANGELOG.md',
                       help='Path to changelog file (default: CHANGELOG.md)')
    
    args = parser.parse_args()
    
    automation = ChangelogAutomation(args.file)
    
    if args.command == 'init':
        automation.init_changelog()
    elif args.command == 'add':
        automation.add_entry()
    elif args.command == 'release':
        automation.create_release()
    elif args.command == 'auto':
        automation.auto_generate_from_git()
    elif args.command == 'validate':
        automation.validate_changelog()

if __name__ == '__main__':
    main()
