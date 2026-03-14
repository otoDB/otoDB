# otoDB Browser Extension

This is the companion extension for [otodb.net](https://otodb.net).

## Build

Requires [Bun](https://bun.sh).

```bash
bun i
bun run build:firefox
```

Build output will be located in the `dist/` directory.

To pack both the Chrome and Firefox versions into .zip archives for distribution:

```bash
bun run pack
```
