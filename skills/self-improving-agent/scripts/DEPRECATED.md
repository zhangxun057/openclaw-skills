# Deprecated Shell Scripts

**Status:** Deprecated - Use Node.js CLI instead

These shell scripts are kept for backward compatibility but are no longer maintained.

## Migration Guide

### Old (Shell Scripts)
```bash
./scripts/activator.sh
./scripts/error-detector.sh
./scripts/extract-skill.sh skill-name
```

### New (Node.js CLI)
```bash
node src/cli.js activator
node src/cli.js error-hook
node src/cli.js extract -n skill-name
```

## New Architecture

The skill has been migrated to a modular Node.js architecture:

- **CLI:** `src/cli.js` - Command-line interface
- **Services:** `src/services/` - Business logic
- **Hooks:** `src/hooks/` - OpenClaw hook handlers
- **Utils:** `src/utils/` - Utility functions
- **Tests:** `tests/` - Comprehensive test suite

See `docs/README.md` for full documentation.
