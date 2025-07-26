# Contributing to Arena of Shadows

Thank you for your interest in contributing to Arena of Shadows! This guide will help you get started with contributing to the project.

## Ways to Contribute

- 🐛 **Bug Reports** - Found an issue? Let us know!
- ✨ **Feature Suggestions** - Have ideas for new features or improvements?
- 💻 **Code Contributions** - Help implement new features or fix bugs
- 📝 **Documentation** - Improve README, comments, or guides
- 🎮 **Testing** - Play the game and provide feedback

## Getting Started

### Prerequisites

Before contributing, make sure you have:
- Python 3.8+
- Git installed and configured
- A GitHub account

### Development Setup

#### Option 1: Code Contributions (Fork & Pull Request)

1. **Fork the repository** on GitHub by clicking the "Fork" button

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/jerichobien360/Arena-of-Shadows.git
   cd Arena-of-Shadows
   ```

3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/YOUR_FEATURE_NAME
   ```

4. **Set up the development environment**:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   
   # Install dependencies
   pip install pygame numpy numba
   # Note: sqlite3 is included with Python standard library
   ```

5. **Make your changes** and test them thoroughly

6. **Commit your changes** with a clear, descriptive message:
   ```bash
   git add .
   git commit -m "Add: brief description of your feature"
   ```
   
   Use conventional commit prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Docs:` for documentation changes

7. **Push to your branch**:
   ```bash
   git push origin feature/YOUR_FEATURE_NAME
   ```

8. **Open a Pull Request** on GitHub with:
   - Clear description of changes made
   - Screenshots or GIFs if there are visual changes
   - Reference to any related issues (e.g., "Fixes #123")
   - Steps to test your changes

#### Option 2: Issues & Feedback

1. **Report bugs** using [GitHub Issues](https://github.com/jerichobien360/Arena-of-Shadows/issues)
   - Use the bug report template
   - Include steps to reproduce
   - Provide system information (OS, Python version, etc.)

2. **Suggest features** with detailed descriptions
   - Explain the problem your feature would solve
   - Describe your proposed solution
   - Consider alternative solutions

3. **Contact directly** via the repository's Issues tab for general discussions

## Coding Standards

### Code Style

We follow [PEP 8](https://peps.python.org/pep-0008/) Python style guidelines. Key points:

- Use 4 spaces for indentation (no tabs)
- Maximum line length of 79 characters for code, 72 for comments
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Use type hints where appropriate

### Code Quality

- Write clean, readable code with meaningful comments
- Test your changes thoroughly before submitting
- Ensure your code doesn't break existing functionality
- Follow existing code patterns and conventions in the project

### Commit Guidelines

- Write clear, concise commit messages
- Use the present tense ("Add feature" not "Added feature")
- Reference issues and pull requests when applicable
- Keep commits focused on a single change

## Testing

Before submitting your contribution:

1. Test your changes in different scenarios
2. Ensure the game runs without errors
3. Verify that existing features still work
4. Test on different screen resolutions if UI changes are involved

## Questions?

If you have questions about contributing:

- Check existing [Issues](https://github.com/jerichobien360/Arena-of-Shadows/issues) and [Pull Requests](https://github.com/jerichobien360/Arena-of-Shadows/pulls)
- Open a new issue with the "question" label
- Contact the maintainers through GitHub

## Recognition

All contributors will be acknowledged in the project. Thank you for helping make Arena of Shadows better!

---

*Happy coding! 🎮*
