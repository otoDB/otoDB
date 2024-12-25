/* LKRM_STD */
const _$ = console.log.bind(console);

const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

// const lerp =(x: number, a: number, b: number): number => a + x * (b - a);
// const { sqrt, log: ln, pow, min, max, sin, cos, tan, asin, acos, atan, atan2, PI, E } = Math;
// const to_radians = (x: number) => x / 180 * PI;
// const to_degrees = (x: number) => x / PI * 180;
// const clamp = (x: number, minimum: number, maximum: number): number => min(max(x, minimum), maximum);
// const clamp_lerp = (x: number, a: number, b: number) => lerp(clamp(x, 0, 1), a, b);
// const lerp_range = (f: number, x: number, y: number, a: number, b: number) => lerp((f - x) / (y - x), a, b);
// const clamp_lerp_range = (f: number, x: number, y: number, a: number, b: number) => clamp_lerp((f - x) / (y - x), a, b);

// const animate = (func: (fac: number) => void, time: number) => {
//     let start: number, previous_timestamp: number;

//     return new Promise<void>((resolve: () => void) => window.requestAnimationFrame(function step(timestamp) {
//         if (start === undefined)
//             start = timestamp;
//         const elapsed = timestamp - start;
    
//         if (previous_timestamp !== timestamp)
//             func(min(elapsed/time, 1.0));
    
//         if (elapsed < time) {
//             previous_timestamp = timestamp;
//             window.requestAnimationFrame(step);
//         }
//         else
//             resolve();
//     }));
// };