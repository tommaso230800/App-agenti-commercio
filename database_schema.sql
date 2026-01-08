-- Schema Database App Agente di Commercio
-- =========================================
-- Esegui questo SQL nella console Supabase (SQL Editor)

-- Tabella Clienti
CREATE TABLE clienti (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome_azienda VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) DEFAULT 'distributore', -- distributore, grossista
    indirizzo TEXT,
    citta VARCHAR(100),
    provincia VARCHAR(50),
    cap VARCHAR(10),
    telefono VARCHAR(50),
    email VARCHAR(255),
    referente_nome VARCHAR(255),
    referente_ruolo VARCHAR(100),
    partita_iva VARCHAR(20),
    categoria CHAR(1) DEFAULT 'C', -- A, B, C
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella Visite
CREATE TABLE visite (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cliente_id UUID REFERENCES clienti(id) ON DELETE CASCADE,
    data_visita TIMESTAMP WITH TIME ZONE NOT NULL,
    esito VARCHAR(50), -- positivo, negativo, da_ricontattare
    ordine_effettuato BOOLEAN DEFAULT FALSE,
    importo_ordine DECIMAL(10,2),
    note TEXT,
    prossima_azione TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella Promemoria
CREATE TABLE promemoria (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titolo VARCHAR(255) NOT NULL,
    descrizione TEXT,
    cliente_id UUID REFERENCES clienti(id) ON DELETE SET NULL,
    tipo VARCHAR(50), -- chiamata, preventivo, sollecito, ricontatto, altro
    data_scadenza TIMESTAMP WITH TIME ZONE NOT NULL,
    priorita VARCHAR(20) DEFAULT 'media', -- alta, media, bassa
    completato BOOLEAN DEFAULT FALSE,
    completato_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella Visite Pianificate (Calendario)
CREATE TABLE visite_pianificate (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cliente_id UUID REFERENCES clienti(id) ON DELETE CASCADE,
    data_pianificata DATE NOT NULL,
    ora_inizio TIME,
    ora_fine TIME,
    note TEXT,
    completata BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici per performance
CREATE INDEX idx_clienti_provincia ON clienti(provincia);
CREATE INDEX idx_clienti_categoria ON clienti(categoria);
CREATE INDEX idx_visite_data ON visite(data_visita);
CREATE INDEX idx_visite_cliente ON visite(cliente_id);
CREATE INDEX idx_promemoria_scadenza ON promemoria(data_scadenza);
CREATE INDEX idx_promemoria_completato ON promemoria(completato);
CREATE INDEX idx_visite_pianificate_data ON visite_pianificate(data_pianificata);

-- Trigger per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clienti_updated_at
    BEFORE UPDATE ON clienti
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (opzionale, per sicurezza aggiuntiva)
-- ALTER TABLE clienti ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE visite ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE promemoria ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE visite_pianificate ENABLE ROW LEVEL SECURITY;
