import sharp from "sharp";
const jobs = [
  ["avatar.svg", "avatar-512.png", 512, 512],
  ["avatar.svg", "avatar-1024.png", 1024, 1024],
  ["social-preview.svg", "social-preview.png", 1280, 640],
];
for (const [src, out, w, h] of jobs) {
  await sharp(src, { density: 384 }).resize(w, h).png().toFile(out);
  console.log("wrote", out);
}
