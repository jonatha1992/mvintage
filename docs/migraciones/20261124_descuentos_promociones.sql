-- Migración: Descuentos y promociones en productos (Showroom Isabella)
-- Ejecutar manualmente en PostgreSQL de producción/test antes de desplegar el backend.
-- Es idempotente: se puede correr más de una vez sin error.

ALTER TABLE product ADD COLUMN IF NOT EXISTS has_discount BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE product ADD COLUMN IF NOT EXISTS discount_percentage DOUBLE PRECISION NULL;
ALTER TABLE product ADD COLUMN IF NOT EXISTS promo_label VARCHAR(20) NULL;
ALTER TABLE product ADD COLUMN IF NOT EXISTS discount_starts_at TIMESTAMP NULL;
ALTER TABLE product ADD COLUMN IF NOT EXISTS discount_ends_at TIMESTAMP NULL;
