-- Add missing createdAt and updatedAt columns to account table
ALTER TABLE "account" ADD COLUMN "createdAt" timestamp DEFAULT NOW() NOT NULL;
ALTER TABLE "account" ADD COLUMN "updatedAt" timestamp DEFAULT NOW() NOT NULL;
