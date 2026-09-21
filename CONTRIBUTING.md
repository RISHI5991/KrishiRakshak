# Contributing to Dhurandhar

Thank you for your interest in contributing to the Dhurandhar agricultural robotics project! This guide will help you get started.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Dhurandhar.git
   cd Dhurandhar
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up** the development environment:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8. Use type hints where practical.
- **Kotlin**: Follow the official [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html).
- **Arduino C++**: Use consistent indentation (4 spaces), meaningful variable names, and comment hardware-specific logic.
- **Documentation**: Use clear, concise language. Include code examples where helpful.

### Branch Naming

- `feature/` — new features (e.g., `feature/nutrient-inference-handler`)
- `fix/` — bug fixes (e.g., `fix/uart-buffer-overflow`)
- `docs/` — documentation changes (e.g., `docs/update-wiring-diagram`)
- `refactor/` — code refactoring (e.g., `refactor/flask-route-split`)

### Commit Messages

Use clear, descriptive commit messages:

```
<type>(<scope>): <description>

Examples:
feat(firmware): add ESP32-S3 soil moisture calibration
fix(flask-api): handle missing image field gracefully
docs(hardware): update ESP32-CAM wiring diagram
test(api): add irrigation endpoint unit tests
```

## Pull Request Process

1. **Ensure** your code builds and passes tests:
   ```bash
   ./scripts/test-all.sh
   ```
2. **Update** documentation if your changes affect the API, hardware, or setup process.
3. **Create** a Pull Request with a clear title and description.
4. **Link** any related issues in your PR description.

## Areas for Contribution

### ML Models
- Improve model accuracy on edge cases
- Add new crop/disease classes
- Optimize model size for ESP32 deployment
- Add data augmentation strategies

### Firmware
- Improve sensor calibration routines
- Add OTA (Over-The-Air) firmware update support
- Implement low-power sleep modes
- Add error recovery mechanisms

### Flask API
- Add rate limiting and authentication
- Improve error handling and validation
- Add WebSocket support for real-time sensor streaming
- Write comprehensive integration tests

### Android App
- Improve UI/UX for field conditions
- Add offline mode with local model inference
- Implement sensor data visualization
- Add multi-language support

### Documentation
- Improve setup guides with troubleshooting tips
- Add assembly photos and videos
- Create user guides for farmers
- Translate documentation

## Reporting Issues

When reporting bugs, please include:

1. **Description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs **actual behavior**
4. **Environment** (OS, Python version, ESP32 board variant, Arduino IDE version)
5. **Logs** or error messages (if applicable)

## Code of Conduct

Be respectful, inclusive, and constructive. We're building something to help farmers — let's keep the community positive.

## Questions?

Open a [GitHub Discussion](../../discussions) for general questions or ideas.
