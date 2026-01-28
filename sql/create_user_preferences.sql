-- Migration: Ajout des colonnes manquantes à search_params
-- Exécuter dans Supabase SQL Editor
-- La table search_params existe déjà, on ajoute juste les nouvelles colonnes

-- Ajouter la colonne sites (liste des sites sélectionnés)
ALTER TABLE search_params
ADD COLUMN IF NOT EXISTS sites JSONB DEFAULT '["pap", "entreparticuliers", "leboncoin"]'::jsonb;

-- Ajouter les colonnes de coordonnées GPS
ALTER TABLE search_params
ADD COLUMN IF NOT EXISTS lat DOUBLE PRECISION;

ALTER TABLE search_params
ADD COLUMN IF NOT EXISTS lon DOUBLE PRECISION;
