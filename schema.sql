-- AMG Ho.Re.Ca Portal (SQLite schema)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS aziende (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  ragione_sociale TEXT,
  indirizzo TEXT,
  citta TEXT,
  provincia TEXT,
  cap TEXT,
  partita_iva TEXT,
  email TEXT,
  telefono TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clienti (
  id TEXT PRIMARY KEY,
  nome_azienda TEXT NOT NULL,
  tipo TEXT DEFAULT 'distributore',
  indirizzo TEXT,
  citta TEXT,
  provincia TEXT,
  cap TEXT,
  telefono TEXT,
  email TEXT,
  referente_nome TEXT,
  referente_ruolo TEXT,
  partita_iva TEXT,
  categoria TEXT DEFAULT 'C',
  note TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prodotti (
  id TEXT PRIMARY KEY,
  azienda_id TEXT NOT NULL REFERENCES aziende(id) ON DELETE CASCADE,
  codice TEXT NOT NULL,
  nome TEXT NOT NULL,
  prezzo_unitario REAL NOT NULL, -- prezzo per pezzo
  pezzi_per_cartone INTEGER NOT NULL DEFAULT 1,
  unita_minima TEXT DEFAULT 'cartone/bottiglia',
  attivo INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  UNIQUE(azienda_id, codice)
);

CREATE TABLE IF NOT EXISTS ordini (
  id TEXT PRIMARY KEY,
  numero TEXT NOT NULL, -- progressivo leggibile (AG-2026-0001)
  azienda_id TEXT NOT NULL REFERENCES aziende(id),
  cliente_id TEXT NOT NULL REFERENCES clienti(id),
  data_ordine TEXT NOT NULL,
  note TEXT,
  imponibile REAL NOT NULL DEFAULT 0,
  stato TEXT NOT NULL DEFAULT 'aperto', -- aperto, confermato, annullato
  created_at TEXT NOT NULL,
  UNIQUE(numero)
);

CREATE TABLE IF NOT EXISTS ordine_righe (
  id TEXT PRIMARY KEY,
  ordine_id TEXT NOT NULL REFERENCES ordini(id) ON DELETE CASCADE,
  prodotto_id TEXT NOT NULL REFERENCES prodotti(id),
  codice_prodotto TEXT,
  nome_prodotto TEXT,
  cartoni INTEGER NOT NULL DEFAULT 0,
  bottiglie INTEGER NOT NULL DEFAULT 0,
  pezzi_totali INTEGER NOT NULL DEFAULT 0,
  prezzo_unitario REAL NOT NULL,
  totale_riga REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS proforme (
  id TEXT PRIMARY KEY,
  ordine_id TEXT NOT NULL UNIQUE REFERENCES ordini(id) ON DELETE CASCADE,
  numero TEXT NOT NULL,
  data_proforma TEXT NOT NULL,
  imponibile REAL NOT NULL,
  pdf_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(numero)
);

-- Calendario / visite / promemoria (dal tuo progetto)
CREATE TABLE IF NOT EXISTS visite (
  id TEXT PRIMARY KEY,
  cliente_id TEXT REFERENCES clienti(id) ON DELETE CASCADE,
  data_visita TEXT NOT NULL,
  esito TEXT,
  ordine_effettuato INTEGER DEFAULT 0,
  importo_ordine REAL,
  note TEXT,
  prossima_azione TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS promemoria (
  id TEXT PRIMARY KEY,
  titolo TEXT NOT NULL,
  descrizione TEXT,
  cliente_id TEXT REFERENCES clienti(id) ON DELETE SET NULL,
  azienda_id TEXT REFERENCES aziende(id) ON DELETE SET NULL,
  tipo TEXT,
  data_scadenza TEXT NOT NULL,
  priorita TEXT DEFAULT 'media',
  completato INTEGER DEFAULT 0,
  completato_at TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS visite_pianificate (
  id TEXT PRIMARY KEY,
  cliente_id TEXT REFERENCES clienti(id) ON DELETE CASCADE,
  data_pianificata TEXT NOT NULL,
  ora_inizio TEXT,
  ora_fine TEXT,
  note TEXT,
  completata INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ordini_data ON ordini(data_ordine);
CREATE INDEX IF NOT EXISTS idx_ordini_azienda ON ordini(azienda_id);
CREATE INDEX IF NOT EXISTS idx_ordini_cliente ON ordini(cliente_id);
CREATE INDEX IF NOT EXISTS idx_prodotti_azienda ON prodotti(azienda_id);
