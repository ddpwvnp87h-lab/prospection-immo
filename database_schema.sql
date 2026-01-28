-- Schéma de base de données pour Prospection Immo Team Maureen
-- À exécuter sur Supabase

-- Table des utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des paramètres de recherche par utilisateur
CREATE TABLE search_params (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ville TEXT NOT NULL,
    rayon INTEGER DEFAULT 10,
    region TEXT DEFAULT 'France métropolitaine',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Table des annonces immobilières
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Identification et déduplication
    hash TEXT NOT NULL,
    url TEXT NOT NULL,

    -- Informations principales
    title TEXT NOT NULL,
    price INTEGER NOT NULL,
    location TEXT NOT NULL,
    source TEXT NOT NULL,

    -- Détails
    photos TEXT[],
    phone TEXT,
    surface INTEGER,
    rooms INTEGER,
    description TEXT,

    -- Métadonnées
    status TEXT DEFAULT 'Nouveau' CHECK (status IN ('Nouveau', 'Contacté', 'Réponse reçue', 'Pas de réponse', 'Pas intéressé')),
    published_date DATE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT unique_url_per_user UNIQUE(user_id, url)
);

-- Index pour les performances
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_created_at ON listings(created_at);
CREATE INDEX idx_listings_url ON listings(url);
CREATE INDEX idx_listings_hash ON listings(hash);
CREATE INDEX idx_listings_last_seen ON listings(last_seen_at);

-- Fonction de nettoyage automatique (à appeler via cron ou manuellement)
CREATE OR REPLACE FUNCTION cleanup_old_listings()
RETURNS TABLE(deleted_count INTEGER) AS $$
DECLARE
    total_deleted INTEGER := 0;
BEGIN
    -- Supprimer les annonces "Pas intéressé"
    DELETE FROM listings WHERE status = 'Pas intéressé';
    GET DIAGNOSTICS total_deleted = ROW_COUNT;

    -- Supprimer les annonces de plus de 90 jours
    DELETE FROM listings WHERE created_at < NOW() - INTERVAL '90 days';
    GET DIAGNOSTICS total_deleted = total_deleted + ROW_COUNT;

    RETURN QUERY SELECT total_deleted;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_params_updated_at BEFORE UPDATE ON search_params
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour les statistiques par utilisateur
CREATE OR REPLACE VIEW user_stats AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(l.id) as total_listings,
    COUNT(l.id) FILTER (WHERE l.status = 'Nouveau') as nouveaux,
    COUNT(l.id) FILTER (WHERE l.status = 'Contacté') as contactes,
    COUNT(l.id) FILTER (WHERE l.status = 'Réponse reçue') as reponses_recues,
    COUNT(l.id) FILTER (WHERE l.status = 'Pas de réponse') as pas_de_reponse,
    COUNT(l.id) FILTER (WHERE l.status = 'Pas intéressé') as pas_interesses
FROM users u
LEFT JOIN listings l ON u.id = l.user_id
GROUP BY u.id, u.email;

-- Politique RLS (Row Level Security) pour isoler les données par utilisateur
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_params ENABLE ROW LEVEL SECURITY;

-- Les utilisateurs ne peuvent voir que leurs propres annonces
CREATE POLICY user_listings_policy ON listings
    FOR ALL
    USING (auth.uid() = user_id);

-- Les utilisateurs ne peuvent voir que leurs propres paramètres
CREATE POLICY user_search_params_policy ON search_params
    FOR ALL
    USING (auth.uid() = user_id);

-- Commentaires pour documentation
COMMENT ON TABLE listings IS 'Annonces immobilières scrapées, isolées par utilisateur';
COMMENT ON TABLE users IS 'Utilisateurs de l application';
COMMENT ON TABLE search_params IS 'Paramètres de recherche personnalisés par utilisateur';
COMMENT ON COLUMN listings.hash IS 'Hash MD5 de titre+prix+localisation pour déduplication';
COMMENT ON COLUMN listings.last_seen_at IS 'Dernière fois que l annonce a été vue lors d un scraping';
