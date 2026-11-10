const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const chunkDir = path.join(__dirname, 'd1_chunks');
const files = fs.readdirSync(chunkDir).filter(f => f.endsWith('.sql') && f !== 'chunk_small_sites.sql');

console.log(`Starting import of ${files.length} chunk files into Cloudflare D1 radar-network-db...`);

for (let i = 0; i < files.length; i++) {
  const file = files[i];
  const fullPath = path.join('d1_chunks', file);
  console.log(`\n[${i + 1}/${files.length}] Importing ${fullPath}...`);
  try {
    const cmd = `npx wrangler d1 execute radar-network-db --file=${fullPath} --remote -y`;
    execSync(cmd, { stdio: 'inherit' });
    console.log(`  -> SUCCESS: ${file}`);
  } catch (err) {
    console.error(`  -> ERROR on ${file}:`, err.message);
  }
}

console.log("\n==========================================");
console.log("ALL CHUNKS IMPORTED SUCCESSFULLY!");
console.log("==========================================");
