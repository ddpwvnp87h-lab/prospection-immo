-- Table pour sauvegarder les préférences de recherche des utilisateurs
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ville VARCHAR(255) DEFAULT 'Paris',
    rayon INTEGER DEFAULT 10,
    sites JSONB DEFAULT '["pap", "entreparticuliers", "leboncoin"]'::jsonb,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Index pour recherche rapide par user_id
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Politique RLS (Row Level Security) - optionnel mais recommandé
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Permettre aux utilisateurs de voir/modifier leurs propres préférences
CREATE POLICY "Users can manage their own preferences"
    ON user_preferences
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Pour l'accès via service key (notre app), on autorise tout
CREATE POLICY "Service role can manage all preferences"
    ON user_preferences
    FOR ALL
    USING (true)
    WITH CHECK (true);
