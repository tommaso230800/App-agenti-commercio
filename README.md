# 💼 Portale Agente di Commercio

**Gestionale Commerciale Professionale per Agenti Plurimandatari**

Sistema completo per la gestione di ordini, clienti, aziende e attività commerciali.
Stile e flusso identico a Order Sender.

---

## 🎯 Funzionalità Principali

### 📋 Gestione Ordini
- **Flusso a 6 step** identico a Order Sender:
  1. **Fornitore** - Selezione azienda/mandante
  2. **Cliente** - Selezione cliente con ricerca
  3. **Sede** - Sede principale o alternativa
  4. **Articoli** - Inserimento prodotti con cartoni/pezzi/sconti
  5. **Dettagli** - Pagamento, consegna, note
  6. **Riepilogo** - Conferma e invio

- **Barra fissa inferiore** con:
  - Data ordine
  - Totale pezzi
  - Totale cartoni
  - Imponibile

- **Stati ordine**: Bozza 🟠 → Inviato 🟢 → Confermato 🔵 → Evaso ✅

### 📄 PDF Ordine Professionale
- Documento commerciale completo
- Layout professionale con logo
- Solo IMPONIBILE (no IVA)
- Tabella articoli dettagliata
- Condizioni di vendita
- Spazio firme
- Pronto per invio a cliente/casa madre

### 📊 Dashboard Business
- KPI principali (clienti, ordini, fatturato)
- Fatturato mese/anno
- Ultimi ordini
- Promemoria urgenti
- Grafici fatturato per azienda

### 📈 Report e Analisi
- Fatturato per azienda
- Fatturato per cliente (Top 20)
- Prodotti più venduti
- Totale agenzia

### 👥 Anagrafica Completa
- **Clienti**: dati fiscali, sedi, contatti, categoria
- **Aziende**: fornitori/mandanti con tutti i dati
- **Prodotti**: catalogo per azienda con prezzi e confezioni

### 🔔 Promemoria e Calendario
- Gestione scadenze
- Priorità (alta/media/bassa)
- Collegamento a clienti
- Vista attivi/completati

---

## 🚀 Installazione

### Requisiti
- Python 3.9+
- pip

### Setup Locale

```bash
# 1. Clona o scarica il progetto
cd portale-agente-perfetto

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Avvia l'applicazione
streamlit run streamlit_app.py
```

### Accesso
- **URL**: http://localhost:8501
- **Password**: `demo123`

---

## 📁 Struttura File

```
portale-agente-perfetto/
├── streamlit_app.py      # Applicazione principale
├── db.py                 # Gestione database SQLite
├── pdf_ordine.py         # Generatore PDF ordini
├── schema.sql            # Schema database
├── requirements.txt      # Dipendenze Python
├── README.md             # Documentazione
└── portale_agente.db     # Database (creato automaticamente)
```

---

## 🌐 Deploy su Streamlit Cloud

### 1. Carica su GitHub
```bash
git init
git add .
git commit -m "Portale Agente v1.0"
git remote add origin https://github.com/TUO-USERNAME/portale-agente.git
git push -u origin main
```

### 2. Deploy su Streamlit Cloud
1. Vai su [share.streamlit.io](https://share.streamlit.io)
2. Connetti il tuo repository GitHub
3. Seleziona `streamlit_app.py` come file principale
4. Clicca "Deploy"

---

## 💡 Utilizzo

### Primo Avvio
1. Accedi con password `demo123`
2. Vai su **Impostazioni** → inserisci i tuoi dati agente
3. Crea le **Aziende** (fornitori/mandanti)
4. Aggiungi i **Prodotti** per ogni azienda
5. Inserisci i **Clienti**
6. Inizia a creare **Ordini**!

### Flusso Ordine Tipico
1. Dashboard → **Nuovo Ordine**
2. Seleziona **Fornitore** (azienda)
3. Seleziona **Cliente**
4. Conferma **Sede** di consegna
5. Aggiungi **Articoli** (cartoni + pezzi sfusi)
6. Inserisci **Dettagli** (pagamento, note)
7. Controlla **Riepilogo**
8. **INVIA ORDINE** o Salva Bozza

### Generazione PDF
- Vai su **Lista Ordini**
- Espandi un ordine
- Clicca **📄 PDF** → **⬇️ Scarica PDF**

---

## 🔧 Personalizzazione

### Cambiare Password
In `streamlit_app.py`, modifica:
```python
APP_PASSWORD = "tua_nuova_password"
```

### Modificare Stili
Il CSS è incorporato in `streamlit_app.py` nella sezione `st.markdown("""<style>...</style>""")`

### Aggiungere Campi
1. Modifica `schema.sql` per la struttura DB
2. Aggiorna le funzioni in `db.py`
3. Modifica i form in `streamlit_app.py`

---

## 📊 Database

Il sistema usa **SQLite** con le seguenti tabelle:
- `aziende` - Fornitori/mandanti
- `clienti` - Anagrafica clienti
- `prodotti` - Catalogo prodotti
- `ordini` - Testata ordini
- `ordini_righe` - Dettaglio articoli ordine
- `promemoria` - Scadenze e attività
- `visite_pianificate` - Calendario visite
- `agente` - Dati agente

---

## 🛡️ Sicurezza

- Password di accesso
- Database locale (non esposto)
- Nessun dato sensibile in chiaro

Per produzione, considera:
- Variabili d'ambiente per password
- HTTPS su deploy
- Backup regolari del database

---

## 📝 Note Tecniche

- **Framework**: Streamlit 1.28+
- **Database**: SQLite3
- **PDF**: ReportLab
- **Grafici**: Plotly

Il database viene creato automaticamente al primo avvio.

---

## 🆘 Supporto

### Problemi Comuni

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Database locked"**
Riavvia l'applicazione.

**PDF non si genera**
Verifica che ReportLab sia installato:
```bash
pip install reportlab
```

---

## 📜 Licenza

Uso personale e commerciale consentito.

---

## 🔄 Versione

**v1.0.0** - Gennaio 2026
- Sistema ordini completo stile Order Sender
- PDF ordine professionale
- Dashboard e report
- Gestione clienti/aziende/prodotti
- Promemoria e calendario

---

**Sviluppato con ❤️ per Agenti di Commercio**
