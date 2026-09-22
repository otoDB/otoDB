# otoDB Browser Extension

This is the companion extension for [otodb.net](https://otodb.net).

## Build

Requires [Bun](https://bun.sh).

```bash
bun i
bun run build
```

Build output will be located in the `dist/` directory. The same build works in both Chrome and Firefox.

To rebuild on changes during development (load `dist/` as an unpacked/temporary extension):

```bash
bun run watch
```

To pack the build into a .zip archive for distribution:

```bash
bun run pack
```
