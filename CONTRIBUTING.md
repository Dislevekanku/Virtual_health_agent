# Contributing to Virtual Health Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## 📋 Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## 🔧 Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   - Set up service account key
   - Update `agent_info.json` (not committed to repo)

3. **Run tests:**
   ```bash
   python tests/test_agent.py
   ```

## 📝 Coding Standards

### Python
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

### Documentation
- Update README.md for user-facing changes
- Add docstrings to new functions
- Update relevant documentation files

## 🧪 Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Test edge cases and error conditions
- Update test scenarios if needed

## 📦 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (if applicable)
5. **Request review** from maintainers

### PR Title Format
```
[Type] Brief description
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### PR Description
- What changes were made
- Why the changes were needed
- How to test the changes
- Screenshots (if UI changes)

## 🐛 Bug Reports

When reporting bugs, please include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

## ✨ Feature Requests

For new features:
- Describe the feature
- Explain the use case
- Propose implementation approach (if applicable)
- Consider backward compatibility

## 🔐 Security

- **Never commit** credentials or API keys
- Report security issues privately
- Follow security best practices
- Review security implications of changes

## 📚 Documentation

- Keep documentation up to date
- Use clear, concise language
- Include code examples
- Update setup guides if needed

## ✅ Checklist

Before submitting:
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No sensitive data committed
- [ ] Changes are backward compatible (or documented)
- [ ] PR description is complete

## 🙏 Thank You!

Your contributions help make this project better. Thank you for taking the time to contribute!

