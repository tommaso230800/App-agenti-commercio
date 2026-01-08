import os
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from db import (
    get_conn, init_db,
    list_aziende, upsert_azienda, delete_azienda, get_azienda,
    list_clienti, upsert_cliente, delete_cliente, get_cliente,
    list_prodotti, upsert_prodotto, delete_prodotto, list_prodotti_gia_acquistati,
    create_ordine, list_ordini, get_ordine, create_proforma_record,
)
from pdf_proforma import genera_proforma_pdf

load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD", "demo123")
AGENCY_NAME = os.getenv("AGENCY_NAME", "AMG Ho.Re.Ca Business & Strategy")
LOGO_PATH = str(Path(__file__).resolve().parent / "assets" / "logo.jpg")
GENERATED_DIR = Path(__file__).resolve().parent / "generated" / "proforme"

st.set_page_config(page_title="AMG Portal", page_icon="🧾", layout="wide", initial_sidebar_state="expanded")

# ---- Stile (tema moderno) ----
st.markdown("""
<style>
:root{
  --brand:#0f766e; /* teal */
  --brand2:#111827; /* slate */
}
div[data-testid="stSidebar"] { background: #0b1220; }
div[data-testid="stSidebar"] * { color: #e5e7eb !important; }
.stButton>button { border-radius: 10px; }
h1,h2,h3 { letter-spacing: -0.02em; }
.badge { padding:2px 10px;border-radius:999px;font-size:12px;display:inline-block; }
.badge-ok{ background:rgba(16,185,129,.15); color:#065f46;}
.badge-warn{ background:rgba(245,158,11,.18); color:#92400e;}
.card{ background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;padding:14px; }
.small{ color:#6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---- DB ----
conn = get_conn()
init_db(conn)

# ---- Auth ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

def login_view():
    st.markdown("# 🧾 AMG Portal")
    st.markdown("### Accesso")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi", type="primary", use_container_width=True):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata")

def sidebar():
    with st.sidebar:
        st.markdown("## AMG Portal")
        st.markdown("<div class='small'>CRM + Ordini + Report + Giro + Promemoria</div>", unsafe_allow_html=True)
        st.markdown("---")

        pages = [
            "Dashboard",
            "Aziende",
            "Clienti",
            "Prodotti",
            "Nuovo Ordine",
            "Ordini",
            "Calendario",
            "Giro visite",
            "Promemoria",
            "Report",
        ]
        for p in pages:
            if st.button(p, use_container_width=True, type="primary" if st.session_state.page == p else "secondary"):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

def money(x: float) -> str:
    try:
        return f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "€ 0,00"

# -------------------- DASHBOARD --------------------

def view_dashboard():
    st.markdown("# 📊 Dashboard")
    aziende = list_aziende(conn)
    clienti = list_clienti(conn)
    ordini = list_ordini(conn)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Aziende", len(aziende))
    col2.metric("Clienti", len(clienti))
    col3.metric("Ordini", len(ordini))
    totale = sum([float(o["imponibile"] or 0) for o in ordini])
    col4.metric("Imponibile Totale Agenzia", money(totale))

    st.markdown("### Ultimi ordini")
    if not ordini:
        st.info("Nessun ordine ancora. Vai su **Nuovo Ordine**.")
        return

    df = pd.DataFrame(ordini)[["numero", "data_ordine", "azienda_nome", "cliente_nome", "imponibile", "stato"]].copy()
    df["data_ordine"] = pd.to_datetime(df["data_ordine"]).dt.strftime("%Y-%m-%d %H:%M")
    df["imponibile"] = df["imponibile"].astype(float)
    st.dataframe(df, use_container_width=True, hide_index=True)

# -------------------- AZIENDE --------------------

def view_aziende():
    st.markdown("# 🏭 Aziende")
    aziende = list_aziende(conn)

    with st.expander("➕ Aggiungi / Modifica azienda", expanded=not aziende):
        edit = st.selectbox("Seleziona (opzionale)", ["(nuova)"] + [a["nome"] for a in aziende])
        current = None
        if edit != "(nuova)":
            current = next(a for a in aziende if a["nome"] == edit)

        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome *", value=(current or {}).get("nome",""))
        ragione = c2.text_input("Ragione sociale", value=(current or {}).get("ragione_sociale",""))
        indirizzo = st.text_input("Indirizzo", value=(current or {}).get("indirizzo",""))
        c3, c4, c5 = st.columns(3)
        citta = c3.text_input("Città", value=(current or {}).get("citta",""))
        provincia = c4.text_input("Provincia", value=(current or {}).get("provincia",""))
        cap = c5.text_input("CAP", value=(current or {}).get("cap",""))
        c6, c7, c8 = st.columns(3)
        piva = c6.text_input("P.IVA", value=(current or {}).get("partita_iva",""))
        email = c7.text_input("Email", value=(current or {}).get("email",""))
        tel = c8.text_input("Telefono", value=(current or {}).get("telefono",""))

        if st.button("Salva azienda", type="primary", use_container_width=True):
            if not nome.strip():
                st.error("Il nome è obbligatorio")
            else:
                upsert_azienda(conn, {
                    "id": (current or {}).get("id"),
                    "nome": nome,
                    "ragione_sociale": ragione,
                    "indirizzo": indirizzo,
                    "citta": citta,
                    "provincia": provincia,
                    "cap": cap,
                    "partita_iva": piva,
                    "email": email,
                    "telefono": tel,
                    "created_at": (current or {}).get("created_at"),
                })
                st.success("Salvato")
                st.rerun()

    st.markdown("### Elenco aziende")
    if not aziende:
        st.info("Nessuna azienda inserita.")
        return
    df = pd.DataFrame(aziende)[["nome","ragione_sociale","citta","provincia","partita_iva","email","telefono"]]
    st.dataframe(df, use_container_width=True, hide_index=True)

    del_name = st.selectbox("Elimina azienda", ["(seleziona)"] + [a["nome"] for a in aziende])
    if del_name != "(seleziona)":
        if st.button("Conferma eliminazione", type="secondary"):
            a = next(x for x in aziende if x["nome"] == del_name)
            delete_azienda(conn, a["id"])
            st.success("Eliminata")
            st.rerun()

# -------------------- CLIENTI --------------------

def view_clienti():
    st.markdown("# 👥 Clienti")
    clienti = list_clienti(conn)

    with st.expander("➕ Aggiungi / Modifica cliente", expanded=not clienti):
        edit = st.selectbox("Seleziona (opzionale)", ["(nuovo)"] + [c["nome_azienda"] for c in clienti])
        current = None
        if edit != "(nuovo)":
            current = next(c for c in clienti if c["nome_azienda"] == edit)

        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome azienda *", value=(current or {}).get("nome_azienda",""))
        tipo = c2.selectbox("Tipo", ["distributore","grossista","horeca","altro"], index=["distributore","grossista","horeca","altro"].index((current or {}).get("tipo","distributore")))

        indirizzo = st.text_input("Indirizzo", value=(current or {}).get("indirizzo",""))
        c3, c4, c5 = st.columns(3)
        citta = c3.text_input("Città", value=(current or {}).get("citta",""))
        provincia = c4.text_input("Provincia", value=(current or {}).get("provincia",""))
        cap = c5.text_input("CAP", value=(current or {}).get("cap",""))
        c6, c7 = st.columns(2)
        tel = c6.text_input("Telefono", value=(current or {}).get("telefono",""))
        email = c7.text_input("Email", value=(current or {}).get("email",""))
        c8, c9 = st.columns(2)
        ref = c8.text_input("Referente", value=(current or {}).get("referente_nome",""))
        ruolo = c9.text_input("Ruolo", value=(current or {}).get("referente_ruolo",""))
        c10, c11 = st.columns(2)
        piva = c10.text_input("P.IVA", value=(current or {}).get("partita_iva",""))
        categoria = c11.selectbox("Categoria", ["A","B","C"], index=["A","B","C"].index((current or {}).get("categoria","C")))
        note = st.text_area("Note", value=(current or {}).get("note",""), height=80)

        if st.button("Salva cliente", type="primary", use_container_width=True):
            if not nome.strip():
                st.error("Il nome è obbligatorio")
            else:
                upsert_cliente(conn, {
                    "id": (current or {}).get("id"),
                    "nome_azienda": nome,
                    "tipo": tipo,
                    "indirizzo": indirizzo,
                    "citta": citta,
                    "provincia": provincia,
                    "cap": cap,
                    "telefono": tel,
                    "email": email,
                    "referente_nome": ref,
                    "referente_ruolo": ruolo,
                    "partita_iva": piva,
                    "categoria": categoria,
                    "note": note,
                    "created_at": (current or {}).get("created_at"),
                })
                st.success("Salvato")
                st.rerun()

    st.markdown("### Elenco clienti")
    if not clienti:
        st.info("Nessun cliente inserito.")
        return
    df = pd.DataFrame(clienti)[["nome_azienda","tipo","citta","provincia","categoria","telefono","email"]]
    st.dataframe(df, use_container_width=True, hide_index=True)

    del_name = st.selectbox("Elimina cliente", ["(seleziona)"] + [c["nome_azienda"] for c in clienti])
    if del_name != "(seleziona)":
        if st.button("Conferma eliminazione cliente", type="secondary"):
            c = next(x for x in clienti if x["nome_azienda"] == del_name)
            delete_cliente(conn, c["id"])
            st.success("Eliminato")
            st.rerun()

# -------------------- PRODOTTI --------------------

def view_prodotti():
    st.markdown("# 📦 Prodotti")
    aziende = list_aziende(conn)
    if not aziende:
        st.warning("Prima inserisci almeno un'azienda.")
        return

    azienda_nome = st.selectbox("Azienda", [a["nome"] for a in aziende])
    azienda = next(a for a in aziende if a["nome"] == azienda_nome)
    prodotti = list_prodotti(conn, azienda_id=azienda["id"], only_active=False)

    with st.expander("➕ Aggiungi / Modifica prodotto", expanded=not prodotti):
        edit = st.selectbox("Seleziona (opzionale)", ["(nuovo)"] + [f'{p["codice"]} - {p["nome"]}' for p in prodotti])
        current = None
        if edit != "(nuovo)":
            code = edit.split(" - ")[0]
            current = next(p for p in prodotti if p["codice"] == code)

        c1, c2 = st.columns(2)
        codice = c1.text_input("Codice *", value=(current or {}).get("codice",""))
        nome = c2.text_input("Nome *", value=(current or {}).get("nome",""))
        c3, c4, c5 = st.columns(3)
        prezzo = c3.number_input("Prezzo unitario (€/pezzo) *", min_value=0.0, step=0.1, value=float((current or {}).get("prezzo_unitario") or 0.0))
        ppc = c4.number_input("Pezzi per cartone *", min_value=1, step=1, value=int((current or {}).get("pezzi_per_cartone") or 1))
        unita = c5.text_input("Unità minima", value=(current or {}).get("unita_minima","cartone/bottiglia"))
        attivo = st.checkbox("Prodotto attivo", value=bool((current or {}).get("attivo", 1)))

        if st.button("Salva prodotto", type="primary", use_container_width=True):
            if not codice.strip() or not nome.strip():
                st.error("Codice e Nome sono obbligatori")
            else:
                upsert_prodotto(conn, {
                    "id": (current or {}).get("id"),
                    "azienda_id": azienda["id"],
                    "codice": codice,
                    "nome": nome,
                    "prezzo_unitario": prezzo,
                    "pezzi_per_cartone": ppc,
                    "unita_minima": unita,
                    "attivo": attivo,
                    "created_at": (current or {}).get("created_at"),
                })
                st.success("Salvato")
                st.rerun()

    st.markdown("### Elenco prodotti")
    if not prodotti:
        st.info("Nessun prodotto per questa azienda.")
        return
    df = pd.DataFrame(prodotti)[["codice","nome","prezzo_unitario","pezzi_per_cartone","attivo"]].copy()
    df["prezzo_unitario"] = df["prezzo_unitario"].astype(float).apply(money)
    df["attivo"] = df["attivo"].apply(lambda x: "✅" if int(x)==1 else "⛔")
    st.dataframe(df, use_container_width=True, hide_index=True)

    del_prod = st.selectbox("Elimina prodotto", ["(seleziona)"] + [f'{p["codice"]} - {p["nome"]}' for p in prodotti])
    if del_prod != "(seleziona)":
        if st.button("Conferma eliminazione prodotto", type="secondary"):
            code = del_prod.split(" - ")[0]
            p = next(x for x in prodotti if x["codice"] == code)
            delete_prodotto(conn, p["id"])
            st.success("Eliminato")
            st.rerun()

# -------------------- NUOVO ORDINE --------------------

def _init_cart():
    if "cart" not in st.session_state:
        st.session_state.cart = []  # list of {"prodotto": {...}, "cartoni":int, "bottiglie":int}

def view_nuovo_ordine():
    st.markdown("# 🛒 Nuovo Ordine")
    _init_cart()

    aziende = list_aziende(conn)
    clienti = list_clienti(conn)

    if not aziende or not clienti:
        st.warning("Per creare un ordine devi avere almeno **1 azienda** e **1 cliente**.")
        return

    colA, colB = st.columns(2)
    azienda_nome = colA.selectbox("1) Seleziona Azienda", [a["nome"] for a in aziende])
    azienda = next(a for a in aziende if a["nome"] == azienda_nome)

    cliente_nome = colB.selectbox("2) Seleziona Cliente", [c["nome_azienda"] for c in clienti])
    cliente = next(c for c in clienti if c["nome_azienda"] == cliente_nome)

    only_prev = st.checkbox("✅ Cerca solo tra i prodotti già acquistati in passato (come Zuegg)", value=False)

    prodotti_all = list_prodotti(conn, azienda_id=azienda["id"], only_active=True)
    if not prodotti_all:
        st.info("Non ci sono prodotti per questa azienda. Vai su **Prodotti**.")
        return

    if only_prev:
        ids = set(list_prodotti_gia_acquistati(conn, azienda["id"], cliente["id"]))
        prodotti = [p for p in prodotti_all if p["id"] in ids]
    else:
        prodotti = prodotti_all

    st.markdown("### 3) Seleziona prodotti")
    search = st.text_input("Cerca (codice o nome)", value="")
    if search.strip():
        s = search.strip().lower()
        prodotti = [p for p in prodotti if s in (p["codice"] or "").lower() or s in (p["nome"] or "").lower()]

    if not prodotti:
        st.warning("Nessun prodotto trovato con i filtri attivi.")
        return

    # Product picker
    prod_label = st.selectbox("Prodotto", [f'{p["codice"]} - {p["nome"]} ({money(float(p["prezzo_unitario"]))}/pz, {p["pezzi_per_cartone"]} pz/cart)' for p in prodotti])
    codice = prod_label.split(" - ")[0].strip()
    prodotto = next(p for p in prodotti if p["codice"] == codice)

    c1, c2, c3 = st.columns([1,1,1])
    cartoni = c1.number_input("Quantità cartoni", min_value=0, step=1, value=0)
    bottiglie = c2.number_input("Quantità bottiglie sfuse", min_value=0, step=1, value=0)
    if st.button("➕ Aggiungi al carrello", use_container_width=True, type="primary"):
        if cartoni == 0 and bottiglie == 0:
            st.error("Inserisci almeno cartoni o bottiglie.")
        else:
            st.session_state.cart.append({"prodotto": prodotto, "cartoni": int(cartoni), "bottiglie": int(bottiglie)})
            st.success("Aggiunto al carrello")
            st.rerun()

    st.markdown("### 4) Carrello")
    if not st.session_state.cart:
        st.info("Carrello vuoto.")
        return

    # show cart
    rows = []
    imponibile = 0.0
    for i, item in enumerate(st.session_state.cart):
        p = item["prodotto"]
        ppc = int(p["pezzi_per_cartone"] or 1)
        pezzi = int(item["cartoni"])*ppc + int(item["bottiglie"])
        prezzo = float(p["prezzo_unitario"] or 0)
        totale = pezzi*prezzo
        imponibile += totale
        rows.append({
            "#": i+1,
            "Codice": p["codice"],
            "Prodotto": p["nome"],
            "Cartoni": item["cartoni"],
            "Bottiglie": item["bottiglie"],
            "Pezzi": pezzi,
            "Prezzo": money(prezzo),
            "Totale": money(totale),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown(f"**Imponibile ordine:** {money(imponibile)}")
    note = st.text_area("Note ordine (opzionale)", height=70)

    colx, coly = st.columns(2)
    if colx.button("🧹 Svuota carrello", use_container_width=True):
        st.session_state.cart = []
        st.rerun()

    if coly.button("✅ Conferma ordine e genera PDF Proforma", use_container_width=True, type="primary"):
        ordine = create_ordine(conn, azienda["id"], cliente["id"], st.session_state.cart, note=note)
        # Genera PDF e record proforma
        proforma_path = GENERATED_DIR / f'PROFORMA_{ordine["numero"]}.pdf'
        # numero proforma: lo assegniamo dal record, quindi prima creiamo record "provvisorio"
        # Per avere numero nel pdf, creiamo record dopo e rigeneriamo con numero reale.
        # Workaround: prima generiamo con placeholder, poi update -> qui più semplice: creiamo record con path e numero dopo.
        # creiamo record proforma (genera numero) poi scriviamo pdf con numero reale.
        pro = create_proforma_record(conn, ordine["id"], str(proforma_path))
        genera_proforma_pdf(
            file_path=str(proforma_path),
            logo_path=LOGO_PATH if Path(LOGO_PATH).exists() else None,
            proforma_numero=pro["numero"],
            data_proforma=pro["data_proforma"][:10],
            azienda=ordine["azienda"],
            cliente=ordine["cliente"],
            righe=ordine["righe"],
            imponibile=float(ordine["imponibile"]),
            agenzia_nome=AGENCY_NAME,
        )

        st.session_state.cart = []
        st.success(f"Ordine creato ({ordine['numero']}) e Proforma generata ({pro['numero']}).")
        # Download
        with open(proforma_path, "rb") as f:
            st.download_button("⬇️ Scarica PDF Proforma", f, file_name=proforma_path.name, mime="application/pdf")
        st.markdown("Vai su **Ordini** per rivederlo quando vuoi.")

# -------------------- ORDINI --------------------

def view_ordini():
    st.markdown("# 📄 Ordini & Proforme")
    aziende = list_aziende(conn)
    filtro = st.selectbox("Filtra per azienda", ["(tutte)"] + [a["nome"] for a in aziende])

    azienda_id = None
    if filtro != "(tutte)":
        azienda_id = next(a["id"] for a in aziende if a["nome"] == filtro)

    ordini = list_ordini(conn, azienda_id=azienda_id)
    if not ordini:
        st.info("Nessun ordine trovato.")
        return

    df = pd.DataFrame(ordini)[["numero","data_ordine","azienda_nome","cliente_nome","imponibile","stato","id"]].copy()
    df["data_ordine"] = pd.to_datetime(df["data_ordine"]).dt.strftime("%Y-%m-%d %H:%M")
    df["imponibile"] = df["imponibile"].astype(float).apply(money)

    st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

    sel = st.selectbox("Apri dettaglio ordine", ["(seleziona)"] + [o["numero"] for o in ordini])
    if sel == "(seleziona)":
        return
    ordine_id = next(o["id"] for o in ordini if o["numero"] == sel)
    ordine = get_ordine(conn, ordine_id)
    if not ordine:
        st.error("Ordine non trovato")
        return

    st.markdown("### Dettaglio")
    c1, c2, c3 = st.columns(3)
    c1.metric("Numero", ordine["numero"])
    c2.metric("Imponibile", money(float(ordine["imponibile"])))
    c3.metric("Stato", ordine["stato"])

    righe = pd.DataFrame(ordine["righe"])
    if not righe.empty:
        righe_view = righe[["codice_prodotto","nome_prodotto","cartoni","bottiglie","pezzi_totali","prezzo_unitario","totale_riga"]].copy()
        righe_view["prezzo_unitario"] = righe_view["prezzo_unitario"].astype(float).apply(money)
        righe_view["totale_riga"] = righe_view["totale_riga"].astype(float).apply(money)
        st.dataframe(righe_view, use_container_width=True, hide_index=True)

    if ordine.get("proforma"):
        p = ordine["proforma"]
        st.markdown(f"**Proforma:** {p['numero']} — {p['data_proforma'][:10]}")
        path = p["pdf_path"]
        if path and Path(path).exists():
            with open(path, "rb") as f:
                st.download_button("⬇️ Scarica PDF Proforma", f, file_name=Path(path).name, mime="application/pdf")
        else:
            st.warning("PDF non trovato su disco (controlla cartella generated/proforme).")
    else:
        st.warning("Proforma non presente per questo ordine.")

# -------------------- CALENDARIO / GIRO / PROMEMORIA --------------------
# MVP: utilizziamo le tabelle visite_pianificate e promemoria.

import sqlite3
from db import uid, now_iso

def _fetch_df(q: str, params=()):
    cur = conn.execute(q, params)
    return pd.DataFrame([dict(r) for r in cur.fetchall()])

def view_calendario():
    st.markdown("# 📅 Calendario visite")
    clienti = list_clienti(conn)
    if not clienti:
        st.info("Inserisci prima almeno un cliente.")
        return

    with st.expander("➕ Pianifica visita", expanded=False):
        cliente_nome = st.selectbox("Cliente", [c["nome_azienda"] for c in clienti], key="cal_cliente")
        cliente = next(c for c in clienti if c["nome_azienda"] == cliente_nome)
        d = st.date_input("Data", value=date.today())
        c1, c2 = st.columns(2)
        ora_inizio = c1.text_input("Ora inizio (HH:MM)", value="09:00")
        ora_fine = c2.text_input("Ora fine (HH:MM)", value="10:00")
        note = st.text_area("Note", height=70)
        if st.button("Salva visita", type="primary", use_container_width=True):
            conn.execute("""
                INSERT INTO visite_pianificate (id, cliente_id, data_pianificata, ora_inizio, ora_fine, note, completata, created_at)
                VALUES (?,?,?,?,?,?,0,?);
            """, (uid(), cliente["id"], d.isoformat(), ora_inizio, ora_fine, note, now_iso()))
            conn.commit()
            st.success("Visita pianificata")
            st.rerun()

    st.markdown("### Settimana corrente")
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    df = _fetch_df("""
        SELECT vp.*, c.nome_azienda, c.indirizzo, c.citta, c.provincia
        FROM visite_pianificate vp
        JOIN clienti c ON c.id=vp.cliente_id
        WHERE date(vp.data_pianificata) BETWEEN date(?) AND date(?)
        ORDER BY vp.data_pianificata ASC, vp.ora_inizio ASC;
    """, (start.isoformat(), end.isoformat()))

    if df.empty:
        st.info("Nessuna visita pianificata questa settimana.")
        return

    df_view = df[["data_pianificata","ora_inizio","ora_fine","nome_azienda","citta","provincia","completata"]].copy()
    df_view["completata"] = df_view["completata"].apply(lambda x: "✅" if int(x)==1 else "⏳")
    st.dataframe(df_view, use_container_width=True, hide_index=True)

def view_giro():
    st.markdown("# 🚗 Giro visite (oggi)")
    today = date.today().isoformat()
    df = _fetch_df("""
        SELECT vp.*, c.nome_azienda, c.indirizzo, c.citta, c.provincia
        FROM visite_pianificate vp
        JOIN clienti c ON c.id=vp.cliente_id
        WHERE date(vp.data_pianificata)=date(?)
        ORDER BY vp.ora_inizio ASC;
    """, (today,))

    if df.empty:
        st.info("Nessuna visita pianificata per oggi.")
        return

    for _, r in df.iterrows():
        indirizzo = " ".join([str(r.get("indirizzo") or ""), str(r.get("citta") or ""), str(r.get("provincia") or "")]).strip()
        maps = f"https://www.google.com/maps/search/?api=1&query={indirizzo.replace(' ', '+')}" if indirizzo else ""
        st.markdown(f"### {r['ora_inizio'] or ''} — {r['nome_azienda']}")
        st.markdown(f"<div class='small'>{indirizzo}</div>", unsafe_allow_html=True)
        if maps:
            st.link_button("Apri su Google Maps", maps, use_container_width=True)
        st.markdown("---")

def view_promemoria():
    st.markdown("# 🔔 Promemoria")
    clienti = list_clienti(conn)
    aziende = list_aziende(conn)

    with st.expander("➕ Nuovo promemoria", expanded=False):
        titolo = st.text_input("Titolo")
        descrizione = st.text_area("Descrizione", height=70)
        c1, c2 = st.columns(2)
        cliente_nome = c1.selectbox("Cliente (opzionale)", ["(nessuno)"] + [c["nome_azienda"] for c in clienti])
        azienda_nome = c2.selectbox("Azienda (opzionale)", ["(nessuna)"] + [a["nome"] for a in aziende])
        tipo = st.selectbox("Tipo", ["chiamata","preventivo","sollecito","ricontatto","altro"])
        c3, c4 = st.columns(2)
        scad = c3.date_input("Scadenza", value=date.today())
        priorita = c4.selectbox("Priorità", ["alta","media","bassa"], index=1)
        if st.button("Salva promemoria", type="primary", use_container_width=True):
            cliente_id = None if cliente_nome == "(nessuno)" else next(c["id"] for c in clienti if c["nome_azienda"] == cliente_nome)
            azienda_id = None if azienda_nome == "(nessuna)" else next(a["id"] for a in aziende if a["nome"] == azienda_nome)
            conn.execute("""
                INSERT INTO promemoria (id,titolo,descrizione,cliente_id,azienda_id,tipo,data_scadenza,priorita,completato,created_at)
                VALUES (?,?,?,?,?,?,?,?,0,?);
            """, (uid(), titolo, descrizione, cliente_id, azienda_id, tipo, scad.isoformat(), priorita, now_iso()))
            conn.commit()
            st.success("Salvato")
            st.rerun()

    st.markdown("### Lista")
    df = _fetch_df("""
        SELECT p.*, c.nome_azienda as cliente_nome, a.nome as azienda_nome
        FROM promemoria p
        LEFT JOIN clienti c ON c.id=p.cliente_id
        LEFT JOIN aziende a ON a.id=p.azienda_id
        ORDER BY date(p.data_scadenza) ASC;
    """)
    if df.empty:
        st.info("Nessun promemoria.")
        return

    df_view = df[["titolo","data_scadenza","priorita","cliente_nome","azienda_nome","completato","id"]].copy()
    df_view["completato"] = df_view["completato"].apply(lambda x: "✅" if int(x)==1 else "⏳")
    st.dataframe(df_view.drop(columns=["id"]), use_container_width=True, hide_index=True)

    sel = st.selectbox("Segna completato", ["(seleziona)"] + [f'{r["titolo"]} — {r["data_scadenza"]}' for _, r in df.iterrows() if int(r["completato"])==0])
    if sel != "(seleziona)":
        rid = next(r["id"] for _, r in df.iterrows() if f'{r["titolo"]} — {r["data_scadenza"]}' == sel)
        if st.button("✅ Completa", type="primary"):
            conn.execute("UPDATE promemoria SET completato=1, completato_at=? WHERE id=?;", (now_iso(), rid))
            conn.commit()
            st.success("Completato")
            st.rerun()

# -------------------- REPORT --------------------

def view_report():
    st.markdown("# 📈 Report (Business Unit)")
    aziende = list_aziende(conn)
    ordini = list_ordini(conn)
    if not ordini:
        st.info("Nessun ordine: i report si popolano quando salvi ordini.")
        return

    df = pd.DataFrame(ordini)
    df["data_ordine"] = pd.to_datetime(df["data_ordine"])
    df["imponibile"] = df["imponibile"].astype(float)
    df["mese"] = df["data_ordine"].dt.to_period("M").astype(str)

    st.markdown("## Totale Agenzia (tutte le aziende)")
    total = df["imponibile"].sum()
    st.metric("Imponibile totale", money(total))

    per_mese = df.groupby("mese")["imponibile"].sum().reset_index().sort_values("mese")
    st.line_chart(per_mese.set_index("mese"))

    st.markdown("## Seleziona Business Unit (Azienda)")
    azienda_nome = st.selectbox("Azienda", [a["nome"] for a in aziende])
    sub = df[df["azienda_nome"] == azienda_nome].copy()
    st.metric("Imponibile azienda", money(sub["imponibile"].sum()))

    # per mese
    per_mese2 = sub.groupby("mese")["imponibile"].sum().reset_index().sort_values("mese")
    st.bar_chart(per_mese2.set_index("mese"))

    # top clienti
    top_clienti = sub.groupby("cliente_nome")["imponibile"].sum().sort_values(ascending=False).head(10).reset_index()
    st.markdown("### Top clienti (imponibile)")
    st.dataframe(top_clienti, use_container_width=True, hide_index=True)

    # fatturato per prodotto (da righe)
    st.markdown("### Fatturato per prodotto")
    # carichiamo righe per ordini dell'azienda
    righe_all = []
    for oid in sub["id"].tolist():
        o = get_ordine(conn, oid)
        if o and o["righe"]:
            for r in o["righe"]:
                righe_all.append({
                    "prodotto": r.get("nome_prodotto"),
                    "codice": r.get("codice_prodotto"),
                    "totale": float(r.get("totale_riga") or 0),
                    "pezzi": int(r.get("pezzi_totali") or 0),
                })
    if righe_all:
        dr = pd.DataFrame(righe_all)
        agg = dr.groupby(["codice","prodotto"]).agg(totale=("totale","sum"), pezzi=("pezzi","sum")).reset_index()
        agg = agg.sort_values("totale", ascending=False)
        agg["totale"] = agg["totale"].apply(money)
        st.dataframe(agg, use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna riga prodotto trovata.")

# -------------------- ROUTER --------------------

def router():
    sidebar()
    page = st.session_state.page
    if page == "Dashboard":
        view_dashboard()
    elif page == "Aziende":
        view_aziende()
    elif page == "Clienti":
        view_clienti()
    elif page == "Prodotti":
        view_prodotti()
    elif page == "Nuovo Ordine":
        view_nuovo_ordine()
    elif page == "Ordini":
        view_ordini()
    elif page == "Calendario":
        view_calendario()
    elif page == "Giro visite":
        view_giro()
    elif page == "Promemoria":
        view_promemoria()
    elif page == "Report":
        view_report()
    else:
        view_dashboard()


if not st.session_state.authenticated:
    login_view()
else:
    router()
