import 'dotenv/config';
import postgres from 'postgres';
import fs from 'fs';

const sql = postgres(process.env.DATABASE_URL);

try {
  const fixSql = fs.readFileSync('fix-schema.sql', 'utf8');
  await sql.unsafe(fixSql);
  console.log('✅ Schema fixed successfully - columns are now nullable');
} catch (error) {
  console.error('❌ Error fixing schema:', error.message);
  process.exit(1);
} finally {
  await sql.end();
}
