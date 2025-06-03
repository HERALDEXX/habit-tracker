# Contributing to HERALDEXX Habit Tracker

First off, thank you for considering contributing to HERALDEXX Habit Tracker! It's people like you that make it such a great tool.

## Development Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

## Working with Files

The application uses a file protection system. Before making changes:

1. Unlock files for development:

```bash
python main.py --dev
```

2. Make your changes

3. Lock files before committing:

```bash
python main.py --lock
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update version number in:
   - habit_engine/**init**.py
3. The PR will be merged once you have the sign-off of another developer

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Accepting constructive criticism
- Focusing on what is best for the community

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## Questions?

Feel free to open an issue for:

- Bug reports
- Feature requests
- Support questions
