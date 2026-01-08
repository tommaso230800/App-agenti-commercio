# 💼 App Agente di Commercio

App completa per la gestione clienti, visite e promemoria per agenti di commercio.

## 🚀 Funzionalità

- **🔐 Login sicuro** con password
- **👥 Gestione Clienti** - Anagrafica completa con filtro per provincia e categoria
- **📅 Calendario** - Pianificazione visite settimanale/mensile
- **🚗 Giro Giornaliero** - Lista visite del giorno con link a Google Maps
- **✅ Registrazione Visite** - Esito, ordini, note
- **🔔 Promemoria** - Scadenze, priorità, tipi
- **📈 Report** - Statistiche e grafici

## 📱 Ottimizzato per Mobile

L'app è progettata per essere usata principalmente da smartphone.

---

## 🛠️ Installazione Rapida (5 minuti)

### Opzione 1: Deploy su Streamlit Cloud (GRATIS - Consigliato)

1. **Crea account GitHub** (se non ce l'hai): https://github.com
2. **Crea un nuovo repository** e carica questi file
3. **Vai su** https://streamlit.io/cloud
4. **Collega il repository** e deploya

### Opzione 2: Esegui in Locale

```bash
# 1. Installa le dipendenze
pip install -r requirements.txt

# 2. Copia e configura il file .env
cp .env.example .env
# Modifica .env con la tua password

# 3. Avvia l'app
streamlit run app.py
```

---

## 💾 Setup Database (Opzionale - per dati persistenti)

L'app funziona subito con dati in memoria (demo mode).
Per salvare i dati in modo permanente:

### 1. Crea account Supabase (gratuito)
- Vai su https://supabase.com
- Crea un nuovo progetto

### 2. Crea le tabelle
- Vai su **SQL Editor** nel pannello Supabase
- Incolla il contenuto di `database_schema.sql`
- Esegui

### 3. Configura l'app
- Vai su **Settings > API**
- Copia `Project URL` e `anon public key`
- Inseriscili nel file `.env`:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

---

## 🔐 Sicurezza

- Cambia la password di default nel file `.env`
- L'app usa HTTPS quando deployata su Streamlit Cloud
- I dati su Supabase sono criptati

---

## 📁 Struttura File

```
agente-app/
├── app.py              # Applicazione principale
├── requirements.txt    # Dipendenze Python
├── .env.example        # Template configurazione
├── database_schema.sql # Schema database Supabase
└── README.md           # Questa guida
```

---

## 🆘 Supporto

Per problemi o domande, contatta il tuo sviluppatore.

---

## 📝 Note Versione

**v1.0** - Versione iniziale
- Gestione completa clienti con filtri
- Calendario e pianificazione visite
- Giro giornaliero con Maps
- Sistema promemoria
- Report e statistiche
