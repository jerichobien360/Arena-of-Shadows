"""
Configuration file for changelog automation.
Customize these settings for your project.
"""

# Project configuration
PROJECT_NAME = "Arena-of-Shadows"
PROJECT_URL = "https://github.com/jerichobien360/Arena-of-Shadows"

# Changelog settings
CHANGELOG_FILE = "CHANGELOG.md"
DATE_FORMAT = "%Y-%m-%d"

# Git commit categorization rules
# These patterns will be used to automatically categorize git commits
COMMIT_CATEGORIES = {
    'Added': [
        r'^feat(\(.+\))?:',
        r'^feature(\(.+\))?:',
        r'^add(\(.+\))?:',
        r'^new(\(.+\))?:',
    ],
    'Changed': [
        r'^refactor(\(.+\))?:',
        r'^update(\(.+\))?:',
        r'^change(\(.+\))?:',
        r'^improve(\(.+\))?:',
        r'^enhance(\(.+\))?:',
    ],
    'Fixed': [
        r'^fix(\(.+\))?:',
        r'^bugfix(\(.+\))?:',
        r'^hotfix(\(.+\))?:',
        r'^patch(\(.+\))?:',
    ],
    'Security': [
        r'^security(\(.+\))?:',
        r'^sec(\(.+\))?:',
    ],
    'Removed': [
        r'^remove(\(.+\))?:',
        r'^delete(\(.+\))?:',
        r'^drop(\(.+\))?:',
    ],
    'Deprecated': [
        r'^deprecate(\(.+\))?:',
        r'^deprecated(\(.+\))?:',
    ]
}

# Default category for commits that don't match any pattern
DEFAULT_CATEGORY = 'Changed'

# Custom changelog template
CHANGELOG_TEMPLATE = f"""# Changelog

All notable changes to {PROJECT_NAME} will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""

# Release template for version sections
RELEASE_TEMPLATE = """## [{version}] - {date}

"""

# Valid changelog categories (Keep a Changelog standard)
VALID_CATEGORIES = [
    'Added',      # for new features
    'Changed',    # for changes in existing functionality
    'Deprecated', # for soon-to-be removed features
    'Removed',    # for now removed features
    'Fixed',      # for any bug fixes
    'Security'    # in case of vulnerabilities
]

# Commit message cleanup patterns
# These regex patterns will be removed from commit messages when generating changelog
CLEANUP_PATTERNS = [
    r'^(feat|fix|refactor|update|change|remove|delete|security|deprecate|add|new|improve|enhance|bugfix|hotfix|patch|sec|drop|deprecated)(\(.+\))?:\s*',
    r'^\[.+\]\s*',  # Remove tags like [WIP], [BREAKING], etc.
    r'^\s*-\s*',    # Remove leading dashes
    r'\s*\(#\d+\)$', # Remove pull request numbers at the end
]

# Auto-release settings
AUTO_RELEASE = {
    'enabled': False,  # Set to True to enable automatic releases
    'version_bump': 'patch',  # 'major', 'minor', or 'patch'
    'create_git_tag': True,
    'push_changes': False,
}

# Integration settings
INTEGRATIONS = {
    'github': {
        'enabled': False,
        'create_release': False,
        'release_notes': True,
    },
    'slack': {
        'enabled': False,
        'webhook_url': '',
        'channel': '#releases',
    }
}
