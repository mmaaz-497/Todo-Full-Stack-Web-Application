import 'dotenv/config';
import postgres from 'postgres';
import fs from 'fs';

const sql = postgres(process.env.DATABASE_URL);

try {
  const fixSql = fs.readFileSync('fix-session-table.sql', 'utf8');
  await sql.unsafe(fixSql);
  console.log('✅ Session table updated successfully');
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
} finally {
  await sql.end();
}
