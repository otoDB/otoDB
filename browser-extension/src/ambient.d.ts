// Asset imports used by shared frontend modules (e.g. $lib/themes/themes.ts).
// Replaces the `vite/client` types that SvelteKit's generated tsconfig pulled in.
declare module '*.webp' {
    const src: string;
    export default src;
}
