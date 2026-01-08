# AMG Ho.Re.Ca Portal (Streamlit)

Portale agente per:
- **Aziende** (catalogo separato per azienda)
- **Prodotti** (prezzo €/pezzo, pezzi/cartone, attivo)
- **Clienti** (anagrafica)
- **Nuovo Ordine** (carrello + quantità cartoni/bottiglie)
- **Filtro prodotti già acquistati** dal cliente (per azienda)
- **Generazione PDF Proforma** automatica ad ogni ordine (solo **imponibile**, no IVA)
- **Ordini** + download PDF
- **Calendario visite** + **Giro visite** (link Google Maps)
- **Promemoria**
- **Report**: business unit per azienda + totale agenzia (imponibile, top clienti, fatturato per prodotto)

## Avvio rapido (locale)

```bash
python -m venv .venv
source .venv/bin/activate  # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Credenziali
- Password di default: `demo123`
- Puoi cambiarla con variabile ambiente:

```bash
export APP_PASSWORD="la_tua_password"
export AGENCY_NAME="AMG Ho.Re.Ca Business & Strategy"
```

### Database
Di default usa **SQLite** in `data/app.db`.

## PDF Proforma
Il PDF viene salvato in `generated/proforme/` e include:
- Logo (assets/logo.jpg)
- Dati **Azienda (Fornitore)**
- Dati **Cliente (Acquirente)**
- Tabella prodotti con quantità cartoni/bottiglie/pezzi, prezzo e totale riga
- **Totale imponibile**

> Nota: documento non valido ai fini fiscali (solo imponibile).

## GitHub
Carica l'intera cartella del progetto su GitHub.
