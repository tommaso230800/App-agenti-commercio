-- ============================================
-- PORTALE AGENTE DI COMMERCIO
-- Schema Database Completo
-- ============================================

-- Tabella AZIENDE (Fornitori/Mandanti)
CREATE TABLE IF NOT EXISTS aziende (
    id TEXT PRIMARY KEY,
    codice TEXT UNIQUE,
    nome TEXT NOT NULL,
    ragione_sociale TEXT,
    indirizzo TEXT,
    citta TEXT,
    provincia TEXT,
    cap TEXT,
    telefono TEXT,
    email TEXT,
    pec TEXT,
    partita_iva TEXT,
    codice_fiscale TEXT,
    iban TEXT,
    banca TEXT,
    note TEXT,
    logo_path TEXT,
    -- Logo embedded (per Streamlit Cloud: salviamo base64 nel DB)
    logo_b64 TEXT,
    logo_mime TEXT,
    attivo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella APPUNTAMENTI (Calendario)
CREATE TABLE IF NOT EXISTS appuntamenti (
    id TEXT PRIMARY KEY,
    titolo TEXT NOT NULL,
    data DATE NOT NULL,
    ora TEXT,
    cliente_id TEXT,
    luogo TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id) ON DELETE SET NULL
);

-- Tabella CLIENTI (Committenti/Acquirenti)
CREATE TABLE IF NOT EXISTS clienti (
    id TEXT PRIMARY KEY,
    codice TEXT,
    ragione_sociale TEXT NOT NULL,
    nome_commerciale TEXT,
    indirizzo TEXT,
    citta TEXT,
    provincia TEXT,
    cap TEXT,
    telefono TEXT,
    cellulare TEXT,
    email TEXT,
    pec TEXT,
    partita_iva TEXT,
    codice_fiscale TEXT,
    codice_sdi TEXT,
    iban TEXT,
    banca TEXT,
    -- Sede di consegna alternativa
    sede_consegna_indirizzo TEXT,
    sede_consegna_citta TEXT,
    sede_consegna_provincia TEXT,
    sede_consegna_cap TEXT,
    sede_consegna_note TEXT,
    -- Condizioni commerciali
    pagamento_default TEXT,
    sconto_default REAL DEFAULT 0,
    listino TEXT,
    fido REAL,
    -- Referente
    referente_nome TEXT,
    referente_ruolo TEXT,
    referente_telefono TEXT,
    referente_email TEXT,
    -- Classificazione
    categoria TEXT DEFAULT 'C',  -- A, B, C
    zona TEXT,
    canale TEXT,  -- GDO, HORECA, DETTAGLIO, etc.
    note TEXT,
    attivo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella PRODOTTI (Catalogo per azienda)
CREATE TABLE IF NOT EXISTS prodotti (
    id TEXT PRIMARY KEY,
    azienda_id TEXT NOT NULL,
    codice TEXT NOT NULL,
    nome TEXT NOT NULL,
    descrizione TEXT,
    categoria TEXT,
    sottocategoria TEXT,
    -- Unità e confezioni
    unita_misura TEXT DEFAULT 'PZ',  -- PZ, KG, LT, etc.
    -- In questa app: 1 cartone = 6 pezzi (regola fissa)
    pezzi_per_cartone INTEGER DEFAULT 6,
    peso_unitario REAL,
    volume_unitario REAL,
    -- Prezzi
    prezzo_listino REAL NOT NULL,
    prezzo_minimo REAL,
    -- Stato
    disponibile INTEGER DEFAULT 1,
    in_promozione INTEGER DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (azienda_id) REFERENCES aziende(id) ON DELETE CASCADE,
    UNIQUE(azienda_id, codice)
);

-- Tabella ORDINI (Testata)
CREATE TABLE IF NOT EXISTS ordini (
    id TEXT PRIMARY KEY,
    numero TEXT UNIQUE NOT NULL,
    data_ordine DATE NOT NULL,
    -- Riferimenti
    azienda_id TEXT NOT NULL,
    cliente_id TEXT NOT NULL,
    -- Sede consegna (può essere diversa da sede cliente)
    consegna_indirizzo TEXT,
    consegna_citta TEXT,
    consegna_provincia TEXT,
    consegna_cap TEXT,
    consegna_note TEXT,
    -- Condizioni
    pagamento TEXT,
    consegna_tipo TEXT,  -- Franco, Assegnato, etc.
    resa TEXT,
    spedizione TEXT,
    banca TEXT,
    -- Totali
    totale_pezzi INTEGER DEFAULT 0,
    totale_cartoni REAL DEFAULT 0,
    imponibile REAL DEFAULT 0,
    sconto_chiusura REAL DEFAULT 0,
    totale_finale REAL DEFAULT 0,
    -- Stato
    stato TEXT DEFAULT 'bozza',  -- bozza, inviato, confermato, evaso, annullato
    -- Note
    note TEXT,
    note_interne TEXT,
    -- Tracking
    data_invio TIMESTAMP,
    data_conferma TIMESTAMP,
    data_evasione TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (azienda_id) REFERENCES aziende(id),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);

-- Tabella ORDINI_RIGHE (Dettaglio articoli)
CREATE TABLE IF NOT EXISTS ordini_righe (
    id TEXT PRIMARY KEY,
    ordine_id TEXT NOT NULL,
    prodotto_id TEXT NOT NULL,
    -- Quantità
    quantita_cartoni INTEGER DEFAULT 0,
    quantita_pezzi INTEGER DEFAULT 0,
    quantita_totale INTEGER DEFAULT 0,
    -- Prezzi
    prezzo_unitario REAL NOT NULL,
    sconto_riga REAL DEFAULT 0,
    prezzo_finale REAL NOT NULL,
    importo_riga REAL NOT NULL,
    -- Ordinamento
    posizione INTEGER DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ordine_id) REFERENCES ordini(id) ON DELETE CASCADE,
    FOREIGN KEY (prodotto_id) REFERENCES prodotti(id)
);

-- ============================================================
-- PREFILL: ultimi prezzi/quantità usati dal cliente per prodotto
-- (per precompilare l'ordine successivo, sempre modificabile)
-- ============================================================
CREATE TABLE IF NOT EXISTS cliente_prodotto_pref (
    cliente_id TEXT NOT NULL,
    azienda_id TEXT NOT NULL,
    prodotto_id TEXT NOT NULL,
    prezzo_unitario REAL NOT NULL,
    sconto_riga REAL DEFAULT 0,
    quantita_cartoni INTEGER DEFAULT 0,
    quantita_pezzi INTEGER DEFAULT 0,
    updated_at TEXT,
    PRIMARY KEY (cliente_id, azienda_id, prodotto_id),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (azienda_id) REFERENCES aziende(id),
    FOREIGN KEY (prodotto_id) REFERENCES prodotti(id)
);

-- Tabella VISITE (Storico visite clienti)
CREATE TABLE IF NOT EXISTS visite (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    data_visita DATE NOT NULL,
    ora_visita TIME,
    -- Esito
    esito TEXT,  -- positivo, negativo, ricontattare
    ordine_effettuato INTEGER DEFAULT 0,
    ordine_id TEXT,
    importo_ordine REAL,
    -- Note
    note TEXT,
    prossima_azione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (ordine_id) REFERENCES ordini(id)
);

-- Tabella VISITE_PIANIFICATE (Calendario visite)
CREATE TABLE IF NOT EXISTS visite_pianificate (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    data_pianificata DATE NOT NULL,
    ora_inizio TIME,
    ora_fine TIME,
    tipo TEXT DEFAULT 'visita',  -- visita, telefonata, altro
    priorita TEXT DEFAULT 'normale',  -- alta, normale, bassa
    note TEXT,
    completata INTEGER DEFAULT 0,
    visita_id TEXT,  -- collegamento a visita effettuata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (visita_id) REFERENCES visite(id)
);

-- Tabella PROMEMORIA
CREATE TABLE IF NOT EXISTS promemoria (
    id TEXT PRIMARY KEY,
    titolo TEXT NOT NULL,
    descrizione TEXT,
    cliente_id TEXT,
    ordine_id TEXT,
    tipo TEXT DEFAULT 'generico',  -- chiamata, preventivo, sollecito, ricontatto, scadenza, generico
    data_scadenza DATE NOT NULL,
    ora_scadenza TIME,
    priorita TEXT DEFAULT 'media',  -- alta, media, bassa
    completato INTEGER DEFAULT 0,
    data_completamento TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (ordine_id) REFERENCES ordini(id)
);

-- Tabella AGENTE (Dati agente per documenti)
CREATE TABLE IF NOT EXISTS agente (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    ragione_sociale TEXT,
    indirizzo TEXT,
    citta TEXT,
    provincia TEXT,
    cap TEXT,
    telefono TEXT,
    cellulare TEXT,
    email TEXT,
    pec TEXT,
    partita_iva TEXT,
    codice_fiscale TEXT,
    codice_enasarco TEXT,
    iban TEXT,
    banca TEXT,
    logo_path TEXT,
    firma_path TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella IMPOSTAZIONI
CREATE TABLE IF NOT EXISTS impostazioni (
    chiave TEXT PRIMARY KEY,
    valore TEXT,
    tipo TEXT DEFAULT 'string',  -- string, int, float, bool, json
    descrizione TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDICI PER PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_prodotti_azienda ON prodotti(azienda_id);
CREATE INDEX IF NOT EXISTS idx_ordini_azienda ON ordini(azienda_id);
CREATE INDEX IF NOT EXISTS idx_ordini_cliente ON ordini(cliente_id);
CREATE INDEX IF NOT EXISTS idx_ordini_stato ON ordini(stato);
CREATE INDEX IF NOT EXISTS idx_ordini_data ON ordini(data_ordine);
CREATE INDEX IF NOT EXISTS idx_ordini_righe_ordine ON ordini_righe(ordine_id);
CREATE INDEX IF NOT EXISTS idx_visite_cliente ON visite(cliente_id);
CREATE INDEX IF NOT EXISTS idx_visite_data ON visite(data_visita);
CREATE INDEX IF NOT EXISTS idx_visite_pianificate_data ON visite_pianificate(data_pianificata);
CREATE INDEX IF NOT EXISTS idx_promemoria_scadenza ON promemoria(data_scadenza);
CREATE INDEX IF NOT EXISTS idx_promemoria_completato ON promemoria(completato);

-- ============================================
-- IMPOSTAZIONI DEFAULT
-- ============================================

INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo, descrizione) VALUES
    ('numero_ordine_prefisso', 'ORD', 'string', 'Prefisso numero ordine'),
    ('numero_ordine_anno', '1', 'bool', 'Includere anno nel numero ordine'),
    ('numero_ordine_progressivo', '1', 'int', 'Ultimo progressivo ordine'),
    ('valuta', 'EUR', 'string', 'Valuta predefinita'),
    ('decimali_prezzi', '2', 'int', 'Decimali per i prezzi'),
    ('decimali_quantita', '0', 'int', 'Decimali per le quantità'),
    ('iva_default', '22', 'float', 'Aliquota IVA default (non usata per imponibile)'),
    ('pagamento_default', 'Bonifico 30gg', 'string', 'Pagamento predefinito'),
    ('consegna_default', 'Franco destino', 'string', 'Tipo consegna predefinito'),
    ('tema', 'light', 'string', 'Tema interfaccia');

-- ============================================
-- VISTE UTILI
-- ============================================

-- Vista ordini con dettagli
CREATE VIEW IF NOT EXISTS v_ordini_completi AS
SELECT 
    o.*,
    a.nome AS azienda_nome,
    a.ragione_sociale AS azienda_ragione_sociale,
    c.ragione_sociale AS cliente_ragione_sociale,
    c.citta AS cliente_citta,
    c.provincia AS cliente_provincia,
    (SELECT COUNT(*) FROM ordini_righe WHERE ordine_id = o.id) AS num_righe
FROM ordini o
LEFT JOIN aziende a ON o.azienda_id = a.id
LEFT JOIN clienti c ON o.cliente_id = c.id;

-- Vista fatturato per azienda
CREATE VIEW IF NOT EXISTS v_fatturato_azienda AS
SELECT 
    a.id,
    a.nome,
    COUNT(DISTINCT o.id) AS num_ordini,
    SUM(o.totale_finale) AS fatturato_totale,
    AVG(o.totale_finale) AS fatturato_medio
FROM aziende a
LEFT JOIN ordini o ON a.id = o.azienda_id AND o.stato IN ('inviato', 'confermato', 'evaso')
GROUP BY a.id, a.nome;

-- Vista fatturato per cliente
CREATE VIEW IF NOT EXISTS v_fatturato_cliente AS
SELECT 
    c.id,
    c.ragione_sociale,
    c.citta,
    c.provincia,
    COUNT(DISTINCT o.id) AS num_ordini,
    SUM(o.totale_finale) AS fatturato_totale,
    MAX(o.data_ordine) AS ultimo_ordine
FROM clienti c
LEFT JOIN ordini o ON c.id = o.cliente_id AND o.stato IN ('inviato', 'confermato', 'evaso')
GROUP BY c.id, c.ragione_sociale, c.citta, c.provincia;

-- Vista promemoria attivi
CREATE VIEW IF NOT EXISTS v_promemoria_attivi AS
SELECT 
    p.*,
    c.ragione_sociale AS cliente_nome
FROM promemoria p
LEFT JOIN clienti c ON p.cliente_id = c.id
WHERE p.completato = 0
ORDER BY p.data_scadenza ASC, p.priorita DESC;
