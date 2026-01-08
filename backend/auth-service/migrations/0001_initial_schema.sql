-- Initial Better Auth Schema Migration
-- Created: 2025-12-15
-- Description: Creates user, session, account, and verification tables for Better Auth

-- Create user table with custom profile fields
CREATE TABLE IF NOT EXISTS "user" (
  "id" TEXT PRIMARY KEY,
  "email" TEXT NOT NULL UNIQUE,
  "emailVerified" BOOLEAN NOT NULL DEFAULT false,
  "name" TEXT,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "image" TEXT,
  -- Custom fields for user background
  "experience_level" TEXT NOT NULL DEFAULT 'beginner',
  "professional_role" TEXT NOT NULL DEFAULT 'student',
  "role_other" TEXT,
  "organization" TEXT,
  -- Constraints
  CONSTRAINT "experience_level_check" CHECK ("experience_level" IN ('beginner', 'intermediate', 'advanced')),
  CONSTRAINT "professional_role_check" CHECK ("professional_role" IN ('student', 'researcher', 'engineer', 'hobbyist', 'other'))
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS "user_email_idx" ON "user"("email");

-- Create session table
CREATE TABLE IF NOT EXISTS "session" (
  "id" TEXT PRIMARY KEY,
  "expiresAt" TIMESTAMP NOT NULL,
  "ipAddress" TEXT,
  "userAgent" TEXT,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "activeOrganizationId" TEXT,
  "impersonatedBy" TEXT
);

-- Create index on userId for faster session lookups
CREATE INDEX IF NOT EXISTS "session_userId_idx" ON "session"("userId");

-- Create account table (for OAuth providers and password storage)
CREATE TABLE IF NOT EXISTS "account" (
  "id" TEXT PRIMARY KEY,
  "accountId" TEXT NOT NULL,
  "providerId" TEXT NOT NULL,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "accessToken" TEXT,
  "refreshToken" TEXT,
  "idToken" TEXT,
  "expiresAt" TIMESTAMP,
  "password" TEXT
);

-- Create index on userId for faster account lookups
CREATE INDEX IF NOT EXISTS "account_userId_idx" ON "account"("userId");

-- Create unique index on accountId and providerId
CREATE UNIQUE INDEX IF NOT EXISTS "account_accountId_providerId_idx" ON "account"("accountId", "providerId");

-- Create verification table (for email verification tokens)
CREATE TABLE IF NOT EXISTS "verification" (
  "id" TEXT PRIMARY KEY,
  "identifier" TEXT NOT NULL,
  "value" TEXT NOT NULL,
  "expiresAt" TIMESTAMP NOT NULL,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on identifier for faster verification lookups
CREATE INDEX IF NOT EXISTS "verification_identifier_idx" ON "verification"("identifier");

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to user table
DROP TRIGGER IF EXISTS update_user_updated_at ON "user";
CREATE TRIGGER update_user_updated_at
  BEFORE UPDATE ON "user"
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to verification table
DROP TRIGGER IF EXISTS update_verification_updated_at ON "verification";
CREATE TRIGGER update_verification_updated_at
  BEFORE UPDATE ON "verification"
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
  RAISE NOTICE 'Better Auth tables created successfully!';
  RAISE NOTICE 'Tables: user, session, account, verification';
  RAISE NOTICE 'Indexes and triggers have been set up.';
END $$;
