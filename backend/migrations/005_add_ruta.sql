-- 005: Add ruta column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS ruta VARCHAR(150);
