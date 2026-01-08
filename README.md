# Portale Agente di Commercio v3.0

Gestionale Commerciale Professionale per Agenti Plurimandatari

## Novita v3.0
- Interfaccia professionale pulita (SENZA emoji)
- FIX: Campo DATA nel form appuntamenti calendario
- FIX: Funzione save_appuntamento corretta
- UI ottimizzata per mobile/iOS
- Design pulito e professionale

## Installazione
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Accesso
- Password: demo123

## Struttura
- streamlit_app.py - Applicazione principale
- db.py - Gestione database SQLite
- pdf_ordine.py - Generatore PDF ordini
- email_sender.py - Invio email
- schema.sql - Schema database

## Funzionalita
- Gestione ordini a 6 step
- Dashboard con KPI e grafici
- Anagrafica clienti e aziende
- Catalogo prodotti per azienda
- Calendario appuntamenti (con campo data)
- Promemoria con scadenze
- Generazione PDF ordini
- Invio email automatico (opzionale)
