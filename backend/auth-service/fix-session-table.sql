-- Add missing fields to session table
ALTER TABLE "session" ADD COLUMN "token" text;
ALTER TABLE "session" ADD COLUMN "createdAt" timestamp DEFAULT NOW() NOT NULL;
ALTER TABLE "session" ADD COLUMN "updatedAt" timestamp DEFAULT NOW() NOT NULL;

-- Make token unique and not null for future records
UPDATE "session" SET "token" = id WHERE "token" IS NULL;
ALTER TABLE "session" ALTER COLUMN "token" SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS session_token_unique ON "session"("token");
