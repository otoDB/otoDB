# otoDB Browser Extension

This is the companion extension for [otodb.net](https://otodb.net).

## Build

Requires [Deno](https://deno.com).

```bash
deno install
deno task build:firefox
```

Build output will be located in the `dist/` directory.

To pack both the Chrome and Firefox versions into .zip archives for distribution:

```bash
deno task pack
```
