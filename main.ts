// News-image entry: copy the rendered front page to the output dir,
// after checking it is a real PNG inside the gate limits.
// Node 22, standard library only. No network, no input, deterministic:
// the same entry.png bytes go out on every run.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const IMAGE = new URL("./entry.png", import.meta.url);

const png = readFileSync(IMAGE);

// A PNG starts with 89 50 4E 47 0D 0A 1A 0A.
const SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
for (let i = 0; i < SIGNATURE.length; i++) {
  if (png[i] !== SIGNATURE[i]) {
    throw new Error("entry.png is not a PNG file");
  }
}

// The IHDR chunk holds width and height as big-endian u32 at
// offsets 16 and 20. The gate wants a square image, at most 1024
// pixels on a side and at most 1 MiB in total.
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width !== height) {
  throw new Error(`image is ${width}x${height}, it must be square`);
}
if (width > 1024 || height > 1024) {
  throw new Error(`image is ${width}x${height}, over the 1024x1024 limit`);
}
if (png.length > 1048576) {
  throw new Error(`image is ${png.length} bytes, over the 1 MiB limit`);
}

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(join(OUT_DIR, "entry.png"), png);
console.log(`wrote entry.png: ${width}x${height}, ${png.length} bytes`);
