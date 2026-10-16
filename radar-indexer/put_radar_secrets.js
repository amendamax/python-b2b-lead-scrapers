const { execSync } = require('child_process');
const fs = require('fs');

const secrets = [
  { name: 'SECRET_JOBSCAM', path: 'C:\\Users\\bratu\\Downloads\\jobscam-dedicated-5dd0ad164181.json' },
  { name: 'SECRET_PILLSCAM', path: 'C:\\Users\\bratu\\Documents\\antigravity\\amazing-borg\\pill-scam-radar\\pill-bot-1-4d5f1834bade.json' },
  { name: 'SECRET_BROKER', path: 'C:\\Users\\bratu\\Documents\\antigravity\\amazing-borg\\dating-photo-checker\\keys\\broker-indexing-key.json' },
  { name: 'SECRET_DATING', path: 'C:\\Users\\bratu\\Documents\\antigravity\\amazing-borg\\dating-photo-checker\\keys\\dating-indexing-key.json' },
];

for (const s of secrets) {
  if (!fs.existsSync(s.path)) {
    console.error(`Missing file: ${s.path}`);
    continue;
  }
  const content = fs.readFileSync(s.path, 'utf8');
  console.log(`Setting secret ${s.name} for radar-indexer...`);
  try {
    execSync(`npx wrangler secret put ${s.name} --name radar-indexer`, {
      input: content,
      stdio: ['pipe', 'inherit', 'inherit'],
    });
    console.log(`  -> ${s.name} SET SUCCESSFULLY!`);
  } catch (err) {
    console.error(`  -> ERROR setting ${s.name}:`, err.message);
  }
}

console.log("Toate secretele au fost configurate!");
