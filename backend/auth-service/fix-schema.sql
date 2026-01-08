-- Make the extra columns nullable to fix the signup issue
ALTER TABLE "user" ALTER COLUMN "experience_level" DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN "professional_role" DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN "role_other" DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN "organization" DROP NOT NULL;
