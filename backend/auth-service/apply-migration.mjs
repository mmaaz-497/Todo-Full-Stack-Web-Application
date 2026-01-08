import 'dotenv/config';
import postgres from 'postgres';
import fs from 'fs';

const sql = postgres(process.env.DATABASE_URL);

try {
  const migrationSql = fs.readFileSync('add-account-timestamps.sql', 'utf8');
  await sql.unsafe(migrationSql);
  console.log('✅ Account table updated successfully');
} catch (error) {
  console.error('❌ Error applying migration:', error.message);
  process.exit(1);
} finally {
  await sql.end();
}
