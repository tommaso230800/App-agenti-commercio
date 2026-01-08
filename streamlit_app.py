"""
PORTALE AGENTE DI COMMERCIO
Applicazione Principale Streamlit
VERSIONE PERFETTA - Stile Order Sender
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
import plotly.express as px
import plotly.graph_objects as go

# Import moduli locali
import db
from pdf_ordine import genera_pdf_ordine_download

# ============================================
# CONFIGURAZIONE PAGINA
# ============================================

st.set_page_config(
    page_title="Portale Agente",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZZATO - STILE PREMIUM
# ============================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1e3a5f;
        --primary-light: #2d5a87;
        --secondary: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-500: #6b7280;
        --gray-700: #374151;
        --gray-800: #1f2937;
    }
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, var(--primary) 0%, var(--primary-light) 100%); }
    [data-testid="stSidebar"] .stMarkdown { color: white; }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid var(--gray-200);
        text-align: center;
    }
    
    .metric-value { font-size: 1.75rem; font-weight: 700; color: var(--primary); }
    .metric-label { font-size: 0.8rem; color: var(--gray-500); text-transform: uppercase; }
    
    .page-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }
    
    .page-header h1 { margin: 0; font-size: 1.75rem; font-weight: 700; }
    .page-header p { margin: 0.5rem 0 0 0; opacity: 0.9; }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid var(--gray-200);
        margin-bottom: 1rem;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-bozza { background: #fef3c7; color: #92400e; }
    .badge-inviato { background: #d1fae5; color: #065f46; }
    .badge-alta { background: #fee2e2; color: #991b1b; }
    .badge-media { background: #fef3c7; color: #92400e; }
    .badge-bassa { background: #d1fae5; color: #065f46; }
    
    .ordine-row {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    .ordine-row:hover { border-color: var(--secondary); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    
    .stButton > button { border-radius: 8px; font-weight: 500; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================
# INIZIALIZZAZIONE SESSION STATE
# ============================================

def init_session_state():
    """Inizializza tutte le variabili di sessione"""
    defaults = {
        'authenticated': False,
        'current_page': 'dashboard',
        'ordine_step': 1,
        'ordine_azienda_id': None,
        'ordine_cliente_id': None,
        'ordine_sede_alternativa': False,
        'ordine_righe': [],
        'ordine_dettagli': {},
        'ordine_id': None,
        'search_cliente': '',
        'search_prodotto': '',
        'solo_prodotti_acquistati': False,
        'show_form': False,
        'editing_id': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

APP_PASSWORD = "demo123"


# ============================================
# FUNZIONI HELPER
# ============================================

def format_currency(value) -> str:
    try:
        value = float(value) if value else 0
        return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "€ 0,00"

def format_date(date_value) -> str:
    if not date_value:
        return "-"
    try:
        if isinstance(date_value, str):
            if 'T' in date_value:
                date_value = date_value.split('T')[0]
            d = datetime.strptime(date_value, '%Y-%m-%d')
        else:
            d = date_value
        return d.strftime('%d/%m/%Y')
    except:
        return str(date_value)

def reset_ordine():
    st.session_state.ordine_step = 1
    st.session_state.ordine_azienda_id = None
    st.session_state.ordine_cliente_id = None
    st.session_state.ordine_sede_alternativa = False
    st.session_state.ordine_righe = []
    st.session_state.ordine_dettagli = {}
    st.session_state.ordine_id = None

def calcola_totali_ordine() -> dict:
    totale_pezzi = 0
    totale_cartoni = 0
    imponibile = 0
    for riga in st.session_state.ordine_righe:
        totale_pezzi += riga.get('quantita_totale', 0)
        totale_cartoni += riga.get('quantita_cartoni', 0)
        imponibile += riga.get('importo_riga', 0)
    sconto = st.session_state.ordine_dettagli.get('sconto_chiusura', 0) or 0
    sconto_euro = imponibile * (sconto / 100) if sconto > 0 else 0
    return {
        'totale_pezzi': totale_pezzi,
        'totale_cartoni': totale_cartoni,
        'imponibile': imponibile,
        'sconto_chiusura': sconto,
        'totale_finale': imponibile - sconto_euro
    }


# ============================================
# COMPONENTI UI
# ============================================

def render_page_header(title: str, subtitle: str = None):
    subtitle_html = f'<p>{subtitle}</p>' if subtitle else ''
    st.markdown(f'<div class="page-header"><h1>{title}</h1>{subtitle_html}</div>', unsafe_allow_html=True)

def render_metric_card(label: str, value: str):
    st.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

def render_step_indicator(current: int, steps: list):
    cols = st.columns(len(steps))
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current:
                st.success(f"✓ {i}. {name}")
            elif i == current:
                st.info(f"● {i}. {name}")
            else:
                st.write(f"○ {i}. {name}")


# ============================================
# SIDEBAR
# ============================================

def render_sidebar():
    with st.sidebar:
        st.markdown('<div style="text-align:center;padding:1rem 0;"><span style="font-size:2.5rem;">💼</span><h2 style="color:white;margin:0;">Portale Agente</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        menu = [
            ('dashboard', '📊 Dashboard'),
            ('ordini', '📋 Lista Ordini'),
            ('nuovo_ordine', '➕ Nuovo Ordine'),
            ('clienti', '👥 Clienti'),
            ('aziende', '🏭 Aziende'),
            ('prodotti', '📦 Prodotti'),
            ('calendario', '📅 Calendario'),
            ('promemoria', '🔔 Promemoria'),
            ('report', '📈 Report'),
            ('impostazioni', '⚙️ Impostazioni'),
        ]
        
        for page_id, label in menu:
            if st.button(label, key=f"nav_{page_id}", use_container_width=True, 
                        type="primary" if st.session_state.current_page == page_id else "secondary"):
                st.session_state.current_page = page_id
                if page_id == 'nuovo_ordine':
                    reset_ordine()
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()


# ============================================
# PAGINA LOGIN
# ============================================

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align:center;padding:3rem 0;"><span style="font-size:4rem;">💼</span><h1 style="color:#1e3a5f;">Portale Agente</h1><p style="color:#6b7280;">Gestionale Commerciale Professionale</p></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            password = st.text_input("Password", type="password")
            if st.form_submit_button("🔐 Accedi", use_container_width=True, type="primary"):
                if password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Password non corretta")
        st.caption("Password demo: demo123")


# ============================================
# DASHBOARD
# ============================================

def render_dashboard():
    render_page_header("Dashboard", f"Benvenuto! Oggi è {date.today().strftime('%A %d %B %Y')}")
    
    # Statistiche
    stats = db.get_statistiche_dashboard()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Clienti", str(stats.get('totale_clienti', 0)))
    with col2:
        render_metric_card("Ordini Mese", str(stats.get('ordini_mese', 0)))
    with col3:
        render_metric_card("Fatturato Mese", format_currency(stats.get('fatturato_mese', 0)))
    with col4:
        render_metric_card("Fatturato Anno", format_currency(stats.get('fatturato_anno', 0)))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Azioni rapide
    st.subheader("⚡ Azioni Rapide")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Nuovo Ordine", use_container_width=True, type="primary"):
            st.session_state.current_page = 'nuovo_ordine'
            reset_ordine()
            st.rerun()
    with col2:
        if st.button("👥 Nuovo Cliente", use_container_width=True):
            st.session_state.current_page = 'clienti'
            st.session_state.show_form = True
            st.rerun()
    with col3:
        if st.button("📅 Calendario", use_container_width=True):
            st.session_state.current_page = 'calendario'
            st.rerun()
    with col4:
        if st.button("🔔 Promemoria", use_container_width=True):
            st.session_state.current_page = 'promemoria'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ultimi ordini e alert
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Ultimi Ordini")
        ordini = db.get_ordini(limit=5)
        if ordini:
            for o in ordini:
                stato_emoji = "🟠" if o['stato'] == 'bozza' else "🟢"
                st.markdown(f"""
                    <div class="ordine-row">
                        <strong>{o['numero']}</strong> {stato_emoji} {o['stato'].upper()}<br>
                        <span style="color:#6b7280;">{o.get('cliente_ragione_sociale', 'N/D')}</span><br>
                        <strong style="color:#1e3a5f;">{format_currency(o['totale_finale'])}</strong>
                        <span style="color:#9ca3af;"> - {format_date(o['data_ordine'])}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nessun ordine presente")
    
    with col2:
        st.subheader("🔔 Promemoria Urgenti")
        promemoria = db.get_promemoria(solo_attivi=True)
        oggi = date.today()
        urgenti = [p for p in promemoria if p['data_scadenza'] and datetime.strptime(p['data_scadenza'].split('T')[0] if 'T' in p['data_scadenza'] else p['data_scadenza'], '%Y-%m-%d').date() <= oggi + timedelta(days=3)][:5]
        
        if urgenti:
            for p in urgenti:
                data_scad = datetime.strptime(p['data_scadenza'].split('T')[0] if 'T' in p['data_scadenza'] else p['data_scadenza'], '%Y-%m-%d').date()
                if data_scad < oggi:
                    badge = "🔴 SCADUTO"
                elif data_scad == oggi:
                    badge = "🟠 OGGI"
                else:
                    badge = "🟡 Prossimo"
                
                st.markdown(f"""
                    <div class="ordine-row">
                        <strong>{p['titolo']}</strong> <span class="badge">{badge}</span><br>
                        <span style="color:#6b7280;">{p.get('cliente_nome', '')}</span>
                        <span style="color:#9ca3af;"> - {format_date(p['data_scadenza'])}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✨ Nessun promemoria urgente!")
    
    # Fatturato per azienda
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏭 Fatturato per Azienda")
    
    fatturato_aziende = db.get_fatturato_per_azienda()
    if fatturato_aziende and any(a['fatturato'] for a in fatturato_aziende):
        df = pd.DataFrame(fatturato_aziende)
        df = df[df['fatturato'] > 0]
        
        if not df.empty:
            fig = px.bar(df, x='nome', y='fatturato', 
                        title='', 
                        labels={'nome': 'Azienda', 'fatturato': 'Fatturato €'},
                        color='fatturato',
                        color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessun dato di fatturato disponibile")


# ============================================
# LISTA ORDINI
# ============================================

def render_ordini():
    render_page_header("Lista Ordini", "Gestione ordini inseriti")
    
    # Filtri
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stato_filter = st.selectbox("Stato", ["Tutti", "Bozza", "Inviato", "Confermato", "Evaso"])
    with col2:
        aziende = db.get_aziende()
        azienda_options = {"": "Tutte le aziende"} | {a['id']: a['nome'] for a in aziende}
        azienda_filter = st.selectbox("Azienda", options=list(azienda_options.keys()), format_func=lambda x: azienda_options[x])
    with col3:
        data_da = st.date_input("Da", value=date.today() - timedelta(days=30))
    with col4:
        data_a = st.date_input("A", value=date.today())
    
    # Ottieni ordini
    stato_map = {"Tutti": None, "Bozza": "bozza", "Inviato": "inviato", "Confermato": "confermato", "Evaso": "evaso"}
    ordini = db.get_ordini(
        stato=stato_map.get(stato_filter),
        azienda_id=azienda_filter if azienda_filter else None,
        data_da=data_da.isoformat() if data_da else None,
        data_a=data_a.isoformat() if data_a else None
    )
    
    st.markdown(f"**{len(ordini)} ordini trovati**")
    st.markdown("---")
    
    if not ordini:
        st.info("Nessun ordine trovato con i filtri selezionati")
        return
    
    for ordine in ordini:
        stato_emoji = {"bozza": "🟠", "inviato": "🟢", "confermato": "🔵", "evaso": "✅"}.get(ordine['stato'], "⚪")
        
        with st.expander(f"{stato_emoji} **{ordine['numero']}** - {ordine.get('cliente_ragione_sociale', 'N/D')} - {format_currency(ordine['totale_finale'])} - {format_date(ordine['data_ordine'])}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                    **Cliente:** {ordine.get('cliente_ragione_sociale', 'N/D')}<br>
                    **Azienda:** {ordine.get('azienda_nome', 'N/D')}<br>
                    **Stato:** {ordine['stato'].upper()}
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    **Totale Pezzi:** {ordine.get('totale_pezzi', 0)}<br>
                    **Imponibile:** {format_currency(ordine.get('imponibile', 0))}<br>
                    **Totale:** {format_currency(ordine['totale_finale'])}
                """, unsafe_allow_html=True)
            
            with col3:
                # Azioni
                if st.button("📄 PDF", key=f"pdf_{ordine['id']}"):
                    pdf_bytes, filename = genera_pdf_ordine_download(ordine['id'])
                    if pdf_bytes:
                        st.download_button("⬇️ Scarica PDF", pdf_bytes, filename, "application/pdf", key=f"dl_{ordine['id']}")
                
                if ordine['stato'] == 'bozza':
                    if st.button("✅ Invia", key=f"invia_{ordine['id']}"):
                        db.update_stato_ordine(ordine['id'], 'inviato')
                        st.success("Ordine inviato!")
                        st.rerun()
                
                new_stato = st.selectbox("Cambia stato", ["bozza", "inviato", "confermato", "evaso"], 
                                        index=["bozza", "inviato", "confermato", "evaso"].index(ordine['stato']),
                                        key=f"stato_{ordine['id']}")
                if new_stato != ordine['stato']:
                    if st.button("Aggiorna", key=f"upd_{ordine['id']}"):
                        db.update_stato_ordine(ordine['id'], new_stato)
                        st.rerun()


# ============================================
# NUOVO ORDINE - WIZARD COMPLETO
# ============================================

def render_nuovo_ordine():
    render_page_header("Nuovo Ordine", "Inserimento ordine step by step")
    
    steps = ["Fornitore", "Cliente", "Sede", "Articoli", "Dettagli", "Riepilogo"]
    render_step_indicator(st.session_state.ordine_step, steps)
    
    st.markdown("---")
    
    # STEP 1: FORNITORE
    if st.session_state.ordine_step == 1:
        st.subheader("1️⃣ Seleziona Fornitore (Azienda)")
        
        aziende = db.get_aziende()
        if not aziende:
            st.warning("⚠️ Nessuna azienda disponibile. Crea prima un'azienda.")
            if st.button("➕ Crea Azienda"):
                st.session_state.current_page = 'aziende'
                st.rerun()
            return
        
        cols = st.columns(3)
        for i, azienda in enumerate(aziende):
            with cols[i % 3]:
                selected = st.session_state.ordine_azienda_id == azienda['id']
                if st.button(
                    f"🏭 {azienda['nome']}", 
                    key=f"az_{azienda['id']}", 
                    use_container_width=True,
                    type="primary" if selected else "secondary"
                ):
                    st.session_state.ordine_azienda_id = azienda['id']
                    st.session_state.ordine_step = 2
                    st.rerun()
    
    # STEP 2: CLIENTE
    elif st.session_state.ordine_step == 2:
        st.subheader("2️⃣ Seleziona Cliente")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Cerca cliente", placeholder="Ragione sociale, città...")
        with col2:
            if st.button("⬅️ Indietro"):
                st.session_state.ordine_step = 1
                st.rerun()
        
        clienti = db.get_clienti(search=search if search else None)
        
        if not clienti:
            st.warning("Nessun cliente trovato")
            return
        
        for cliente in clienti[:20]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{cliente['ragione_sociale']}**")
                st.caption(f"{cliente.get('indirizzo', '')} - {cliente.get('citta', '')} ({cliente.get('provincia', '')})")
            with col2:
                if st.button("Seleziona", key=f"cl_{cliente['id']}"):
                    st.session_state.ordine_cliente_id = cliente['id']
                    st.session_state.ordine_step = 3
                    st.rerun()
    
    # STEP 3: SEDE
    elif st.session_state.ordine_step == 3:
        st.subheader("3️⃣ Sede di Consegna")
        
        cliente = db.get_cliente(st.session_state.ordine_cliente_id)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("⬅️ Indietro"):
                st.session_state.ordine_step = 2
                st.rerun()
        
        st.markdown(f"**Cliente:** {cliente['ragione_sociale']}")
        st.markdown(f"**Sede principale:** {cliente.get('indirizzo', '')} - {cliente.get('citta', '')} ({cliente.get('provincia', '')})")
        
        usa_alternativa = st.checkbox("Usa sede di consegna alternativa", value=st.session_state.ordine_sede_alternativa)
        st.session_state.ordine_sede_alternativa = usa_alternativa
        
        if usa_alternativa:
            if cliente.get('sede_consegna_indirizzo'):
                st.info(f"Sede alternativa: {cliente.get('sede_consegna_indirizzo')} - {cliente.get('sede_consegna_citta')}")
            else:
                st.warning("Nessuna sede alternativa configurata per questo cliente")
        
        if st.button("Avanti ➡️", type="primary"):
            st.session_state.ordine_step = 4
            st.rerun()
    
    # STEP 4: ARTICOLI
    elif st.session_state.ordine_step == 4:
        render_step_articoli()
    
    # STEP 5: DETTAGLI
    elif st.session_state.ordine_step == 5:
        render_step_dettagli()
    
    # STEP 6: RIEPILOGO
    elif st.session_state.ordine_step == 6:
        render_step_riepilogo()
    
    # Barra inferiore con totali
    if st.session_state.ordine_step >= 4 and st.session_state.ordine_righe:
        totali = calcola_totali_ordine()
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Data Ordine", date.today().strftime('%d/%m/%Y'))
        with col2:
            st.metric("Totale Pezzi", totali['totale_pezzi'])
        with col3:
            st.metric("Totale Cartoni", f"{totali['totale_cartoni']:.1f}")
        with col4:
            st.metric("IMPONIBILE", format_currency(totali['imponibile']))


def render_step_articoli():
    """Step 4: Selezione articoli"""
    st.subheader("4️⃣ Seleziona Articoli")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⬅️ Indietro"):
            st.session_state.ordine_step = 3
            st.rerun()
    
    # Filtri
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("🔍 Cerca prodotto", placeholder="Nome o codice...")
    with col2:
        solo_acquistati = st.checkbox("Solo prodotti già acquistati dal cliente", value=st.session_state.solo_prodotti_acquistati)
        st.session_state.solo_prodotti_acquistati = solo_acquistati
    with col3:
        if st.button("Avanti ➡️", type="primary", disabled=len(st.session_state.ordine_righe) == 0):
            st.session_state.ordine_step = 5
            st.rerun()
    
    # Prodotti dell'azienda selezionata
    prodotti = db.get_prodotti(azienda_id=st.session_state.ordine_azienda_id, search=search if search else None)
    
    # Filtra per già acquistati
    if solo_acquistati:
        prodotti_acquistati_ids = db.get_prodotti_acquistati_cliente(
            st.session_state.ordine_cliente_id, 
            st.session_state.ordine_azienda_id
        )
        prodotti = [p for p in prodotti if p['id'] in prodotti_acquistati_ids]
    
    if not prodotti:
        st.warning("Nessun prodotto trovato")
        return
    
    st.markdown(f"**{len(prodotti)} prodotti disponibili**")
    
    # Lista prodotti con input quantità
    for prodotto in prodotti:
        # Verifica se già nel carrello
        riga_esistente = next((r for r in st.session_state.ordine_righe if r['prodotto_id'] == prodotto['id']), None)
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{prodotto['nome']}**")
                st.caption(f"Cod: {prodotto['codice']} | {prodotto['pezzi_per_cartone']} pz/cartone | {format_currency(prodotto['prezzo_listino'])}")
            
            with col2:
                cartoni = st.number_input("Cartoni", min_value=0, value=riga_esistente['quantita_cartoni'] if riga_esistente else 0, key=f"cart_{prodotto['id']}")
            
            with col3:
                pezzi = st.number_input("Pezzi", min_value=0, value=riga_esistente['quantita_pezzi'] if riga_esistente else 0, key=f"pz_{prodotto['id']}")
            
            with col4:
                sconto = st.number_input("Sc.%", min_value=0.0, max_value=100.0, value=riga_esistente['sconto_riga'] if riga_esistente else 0.0, key=f"sc_{prodotto['id']}")
            
            with col5:
                if st.button("➕" if not riga_esistente else "✏️", key=f"add_{prodotto['id']}"):
                    if cartoni > 0 or pezzi > 0:
                        qta_totale = (cartoni * prodotto['pezzi_per_cartone']) + pezzi
                        prezzo_unitario = prodotto['prezzo_listino']
                        prezzo_scontato = prezzo_unitario * (1 - sconto/100)
                        importo = qta_totale * prezzo_scontato
                        
                        nuova_riga = {
                            'prodotto_id': prodotto['id'],
                            'prodotto_codice': prodotto['codice'],
                            'prodotto_nome': prodotto['nome'],
                            'unita_misura': prodotto.get('unita_misura', 'PZ'),
                            'pezzi_per_cartone': prodotto['pezzi_per_cartone'],
                            'quantita_cartoni': cartoni,
                            'quantita_pezzi': pezzi,
                            'quantita_totale': qta_totale,
                            'prezzo_unitario': prezzo_unitario,
                            'sconto_riga': sconto,
                            'prezzo_finale': prezzo_scontato,
                            'importo_riga': importo
                        }
                        
                        # Aggiorna o aggiungi
                        if riga_esistente:
                            st.session_state.ordine_righe = [r if r['prodotto_id'] != prodotto['id'] else nuova_riga for r in st.session_state.ordine_righe]
                        else:
                            st.session_state.ordine_righe.append(nuova_riga)
                        
                        st.rerun()
            
            st.markdown("---")
    
    # Riepilogo carrello
    if st.session_state.ordine_righe:
        st.subheader("🛒 Carrello")
        for i, riga in enumerate(st.session_state.ordine_righe):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{riga['prodotto_nome']}**")
            with col2:
                st.markdown(f"{riga['quantita_cartoni']} cart. + {riga['quantita_pezzi']} pz = **{riga['quantita_totale']} pz** → {format_currency(riga['importo_riga'])}")
            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.ordine_righe.pop(i)
                    st.rerun()


def render_step_dettagli():
    """Step 5: Dettagli ordine"""
    st.subheader("5️⃣ Dettagli Ordine")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⬅️ Indietro"):
            st.session_state.ordine_step = 4
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        pagamento = st.selectbox("Pagamento", ["Bonifico 30gg", "Bonifico 60gg", "Bonifico 90gg", "Rimessa diretta", "Contanti"], 
                                index=0, key="det_pagamento")
        consegna = st.selectbox("Consegna", ["Franco destino", "Franco partenza", "Ritiro"], key="det_consegna")
        resa = st.text_input("Resa", value="", key="det_resa")
    
    with col2:
        spedizione = st.text_input("Spedizione", value="", key="det_spedizione")
        banca = st.text_input("Banca", value="", key="det_banca")
        sconto_chiusura = st.number_input("Sconto Chiusura %", min_value=0.0, max_value=50.0, value=0.0, key="det_sconto")
    
    note = st.text_area("Note Ordine", value="", key="det_note")
    
    # Salva dettagli
    st.session_state.ordine_dettagli = {
        'pagamento': pagamento,
        'consegna_tipo': consegna,
        'resa': resa,
        'spedizione': spedizione,
        'banca': banca,
        'sconto_chiusura': sconto_chiusura,
        'note': note
    }
    
    if st.button("Avanti ➡️", type="primary"):
        st.session_state.ordine_step = 6
        st.rerun()


def render_step_riepilogo():
    """Step 6: Riepilogo e conferma"""
    st.subheader("6️⃣ Riepilogo Ordine")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⬅️ Indietro"):
            st.session_state.ordine_step = 5
            st.rerun()
    
    azienda = db.get_azienda(st.session_state.ordine_azienda_id)
    cliente = db.get_cliente(st.session_state.ordine_cliente_id)
    totali = calcola_totali_ordine()
    
    # Info generali
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            **FORNITORE**<br>
            {azienda['nome']}<br>
            {azienda.get('ragione_sociale', '')}
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            **CLIENTE**<br>
            {cliente['ragione_sociale']}<br>
            {cliente.get('indirizzo', '')} - {cliente.get('citta', '')} ({cliente.get('provincia', '')})
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabella articoli
    st.markdown("**ARTICOLI**")
    df_righe = pd.DataFrame(st.session_state.ordine_righe)
    if not df_righe.empty:
        df_display = df_righe[['prodotto_codice', 'prodotto_nome', 'quantita_cartoni', 'quantita_pezzi', 'quantita_totale', 'prezzo_unitario', 'sconto_riga', 'importo_riga']].copy()
        df_display.columns = ['Codice', 'Prodotto', 'Cartoni', 'Pezzi', 'Tot.Pz', 'Pr.Unit.', 'Sc.%', 'Importo']
        df_display['Pr.Unit.'] = df_display['Pr.Unit.'].apply(format_currency)
        df_display['Importo'] = df_display['Importo'].apply(format_currency)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Totali
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Pezzi", totali['totale_pezzi'])
    with col2:
        st.metric("Imponibile", format_currency(totali['imponibile']))
    with col3:
        if totali['sconto_chiusura'] > 0:
            st.metric("Sconto Chiusura", f"{totali['sconto_chiusura']}%")
    
    st.markdown(f"### TOTALE ORDINE: {format_currency(totali['totale_finale'])}")
    
    # Condizioni
    det = st.session_state.ordine_dettagli
    st.markdown(f"""
        **Condizioni:** {det.get('pagamento', '')} | {det.get('consegna_tipo', '')} | {det.get('resa', '')}
    """)
    
    if det.get('note'):
        st.markdown(f"**Note:** {det.get('note')}")
    
    st.markdown("---")
    
    # Azioni
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salva Bozza", use_container_width=True):
            salva_ordine('bozza')
    
    with col2:
        if st.button("📤 INVIA ORDINE", type="primary", use_container_width=True):
            salva_ordine('inviato')
    
    with col3:
        if st.button("❌ Annulla", use_container_width=True):
            reset_ordine()
            st.session_state.current_page = 'dashboard'
            st.rerun()


def salva_ordine(stato: str):
    """Salva l'ordine nel database"""
    azienda = db.get_azienda(st.session_state.ordine_azienda_id)
    cliente = db.get_cliente(st.session_state.ordine_cliente_id)
    totali = calcola_totali_ordine()
    det = st.session_state.ordine_dettagli
    
    # Prepara testata
    testata = {
        'numero': db.get_prossimo_numero_ordine(),
        'data_ordine': date.today().isoformat(),
        'azienda_id': st.session_state.ordine_azienda_id,
        'cliente_id': st.session_state.ordine_cliente_id,
        'pagamento': det.get('pagamento'),
        'consegna_tipo': det.get('consegna_tipo'),
        'resa': det.get('resa'),
        'spedizione': det.get('spedizione'),
        'banca': det.get('banca'),
        'totale_pezzi': totali['totale_pezzi'],
        'totale_cartoni': totali['totale_cartoni'],
        'imponibile': totali['imponibile'],
        'sconto_chiusura': totali['sconto_chiusura'],
        'totale_finale': totali['totale_finale'],
        'stato': stato,
        'note': det.get('note'),
    }
    
    # Sede consegna
    if st.session_state.ordine_sede_alternativa and cliente.get('sede_consegna_indirizzo'):
        testata['consegna_indirizzo'] = cliente.get('sede_consegna_indirizzo')
        testata['consegna_citta'] = cliente.get('sede_consegna_citta')
        testata['consegna_provincia'] = cliente.get('sede_consegna_provincia')
        testata['consegna_cap'] = cliente.get('sede_consegna_cap')
    
    # Salva
    ordine_id = db.save_ordine(testata, st.session_state.ordine_righe)
    
    if stato == 'inviato':
        st.success(f"✅ Ordine {testata['numero']} INVIATO con successo!")
    else:
        st.success(f"💾 Ordine {testata['numero']} salvato come BOZZA")
    
    # Reset e vai a lista
    reset_ordine()
    st.session_state.current_page = 'ordini'
    st.rerun()


# ============================================
# CLIENTI
# ============================================

def render_clienti():
    render_page_header("Clienti", "Anagrafica clienti")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Cerca", placeholder="Ragione sociale, città...")
    with col2:
        if st.button("➕ Nuovo Cliente", type="primary"):
            st.session_state.show_form = True
            st.session_state.editing_id = None
    
    # Form nuovo/modifica
    if st.session_state.show_form:
        render_form_cliente()
        return
    
    clienti = db.get_clienti(search=search if search else None)
    
    st.markdown(f"**{len(clienti)} clienti**")
    
    for cliente in clienti:
        with st.expander(f"🏢 {cliente['ragione_sociale']} - {cliente.get('citta', '')} ({cliente.get('provincia', '')})"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                    **Codice:** {cliente.get('codice', '-')}<br>
                    **Indirizzo:** {cliente.get('indirizzo', '-')}<br>
                    **Città:** {cliente.get('citta', '-')} ({cliente.get('provincia', '-')}) {cliente.get('cap', '')}
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    **Telefono:** {cliente.get('telefono', '-')}<br>
                    **Email:** {cliente.get('email', '-')}<br>
                    **P.IVA:** {cliente.get('partita_iva', '-')}
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("✏️ Modifica", key=f"edit_cl_{cliente['id']}"):
                    st.session_state.show_form = True
                    st.session_state.editing_id = cliente['id']
                    st.rerun()
                
                if cliente.get('indirizzo'):
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={cliente['indirizzo']}, {cliente.get('citta', '')}"
                    st.link_button("🗺️ Maps", maps_url)


def render_form_cliente():
    """Form per nuovo/modifica cliente"""
    cliente = None
    if st.session_state.editing_id:
        cliente = db.get_cliente(st.session_state.editing_id)
        st.subheader("✏️ Modifica Cliente")
    else:
        st.subheader("➕ Nuovo Cliente")
    
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            codice = st.text_input("Codice", value=cliente.get('codice', '') if cliente else '')
            ragione_sociale = st.text_input("Ragione Sociale *", value=cliente.get('ragione_sociale', '') if cliente else '')
            indirizzo = st.text_input("Indirizzo", value=cliente.get('indirizzo', '') if cliente else '')
            citta = st.text_input("Città", value=cliente.get('citta', '') if cliente else '')
            provincia = st.text_input("Provincia", value=cliente.get('provincia', '') if cliente else '', max_chars=2)
            cap = st.text_input("CAP", value=cliente.get('cap', '') if cliente else '', max_chars=5)
        
        with col2:
            telefono = st.text_input("Telefono", value=cliente.get('telefono', '') if cliente else '')
            cellulare = st.text_input("Cellulare", value=cliente.get('cellulare', '') if cliente else '')
            email = st.text_input("Email", value=cliente.get('email', '') if cliente else '')
            partita_iva = st.text_input("Partita IVA", value=cliente.get('partita_iva', '') if cliente else '')
            codice_fiscale = st.text_input("Codice Fiscale", value=cliente.get('codice_fiscale', '') if cliente else '')
            categoria = st.selectbox("Categoria", ["A", "B", "C"], index=["A", "B", "C"].index(cliente.get('categoria', 'C')) if cliente else 2)
        
        note = st.text_area("Note", value=cliente.get('note', '') if cliente else '')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salva", type="primary"):
                if not ragione_sociale:
                    st.error("La ragione sociale è obbligatoria")
                else:
                    data = {
                        'codice': codice,
                        'ragione_sociale': ragione_sociale,
                        'indirizzo': indirizzo,
                        'citta': citta,
                        'provincia': provincia.upper(),
                        'cap': cap,
                        'telefono': telefono,
                        'cellulare': cellulare,
                        'email': email,
                        'partita_iva': partita_iva,
                        'codice_fiscale': codice_fiscale,
                        'categoria': categoria,
                        'note': note
                    }
                    if st.session_state.editing_id:
                        data['id'] = st.session_state.editing_id
                    db.save_cliente(data)
                    st.success("Cliente salvato!")
                    st.session_state.show_form = False
                    st.session_state.editing_id = None
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Annulla"):
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()


# ============================================
# AZIENDE
# ============================================

def render_aziende():
    render_page_header("Aziende", "Gestione fornitori/mandanti")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nuova Azienda", type="primary"):
            st.session_state.show_form = True
            st.session_state.editing_id = None
    
    if st.session_state.show_form:
        render_form_azienda()
        return
    
    aziende = db.get_aziende()
    
    if not aziende:
        st.info("Nessuna azienda. Clicca 'Nuova Azienda' per iniziare.")
        return
    
    cols = st.columns(3)
    for i, azienda in enumerate(aziende):
        with cols[i % 3]:
            num_prodotti = len(db.get_prodotti(azienda_id=azienda['id']))
            
            st.markdown(f"""
                <div class="card">
                    <h3 style="margin:0 0 0.5rem 0;">{azienda['nome']}</h3>
                    <p style="color:#6b7280;margin:0;">{azienda.get('ragione_sociale', '') or 'N/D'}</p>
                    <p style="margin:0.5rem 0;">📦 {num_prodotti} prodotti</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️", key=f"edit_az_{azienda['id']}"):
                    st.session_state.show_form = True
                    st.session_state.editing_id = azienda['id']
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_az_{azienda['id']}"):
                    if st.session_state.get(f'confirm_del_{azienda["id"]}'):
                        db.delete_azienda(azienda['id'])
                        st.rerun()
                    else:
                        st.session_state[f'confirm_del_{azienda["id"]}'] = True
                        st.warning("Clicca di nuovo per confermare")


def render_form_azienda():
    """Form per nuova/modifica azienda"""
    azienda = None
    if st.session_state.editing_id:
        azienda = db.get_azienda(st.session_state.editing_id)
        st.subheader("✏️ Modifica Azienda")
    else:
        st.subheader("➕ Nuova Azienda")
    
    with st.form("form_azienda"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome *", value=azienda.get('nome', '') if azienda else '')
            ragione_sociale = st.text_input("Ragione Sociale", value=azienda.get('ragione_sociale', '') if azienda else '')
            indirizzo = st.text_input("Indirizzo", value=azienda.get('indirizzo', '') if azienda else '')
            citta = st.text_input("Città", value=azienda.get('citta', '') if azienda else '')
            provincia = st.text_input("Provincia", value=azienda.get('provincia', '') if azienda else '', max_chars=2)
        
        with col2:
            telefono = st.text_input("Telefono", value=azienda.get('telefono', '') if azienda else '')
            email = st.text_input("Email", value=azienda.get('email', '') if azienda else '')
            partita_iva = st.text_input("Partita IVA", value=azienda.get('partita_iva', '') if azienda else '')
            iban = st.text_input("IBAN", value=azienda.get('iban', '') if azienda else '')
            banca = st.text_input("Banca", value=azienda.get('banca', '') if azienda else '')
        
        note = st.text_area("Note", value=azienda.get('note', '') if azienda else '')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salva", type="primary"):
                if not nome:
                    st.error("Il nome è obbligatorio")
                else:
                    data = {
                        'nome': nome,
                        'ragione_sociale': ragione_sociale,
                        'indirizzo': indirizzo,
                        'citta': citta,
                        'provincia': provincia.upper(),
                        'telefono': telefono,
                        'email': email,
                        'partita_iva': partita_iva,
                        'iban': iban,
                        'banca': banca,
                        'note': note
                    }
                    if st.session_state.editing_id:
                        data['id'] = st.session_state.editing_id
                    db.save_azienda(data)
                    st.success("Azienda salvata!")
                    st.session_state.show_form = False
                    st.session_state.editing_id = None
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Annulla"):
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()


# ============================================
# PRODOTTI
# ============================================

def render_prodotti():
    render_page_header("Prodotti", "Catalogo prodotti per azienda")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        aziende = db.get_aziende()
        azienda_options = {"": "Tutte"} | {a['id']: a['nome'] for a in aziende}
        filter_azienda = st.selectbox("Filtra per azienda", options=list(azienda_options.keys()), format_func=lambda x: azienda_options[x])
    with col2:
        search = st.text_input("🔍 Cerca", placeholder="Nome o codice...")
    with col3:
        if st.button("➕ Nuovo Prodotto", type="primary", disabled=len(aziende) == 0):
            st.session_state.show_form = True
            st.session_state.editing_id = None
    
    if len(aziende) == 0:
        st.warning("⚠️ Crea prima almeno un'azienda")
        return
    
    if st.session_state.show_form:
        render_form_prodotto()
        return
    
    prodotti = db.get_prodotti(
        azienda_id=filter_azienda if filter_azienda else None,
        search=search if search else None,
        solo_disponibili=False
    )
    
    st.markdown(f"**{len(prodotti)} prodotti**")
    
    if not prodotti:
        st.info("Nessun prodotto trovato")
        return
    
    # Tabella prodotti
    df = pd.DataFrame(prodotti)
    df_display = df[['codice', 'nome', 'azienda_nome', 'prezzo_listino', 'pezzi_per_cartone', 'disponibile']].copy()
    df_display.columns = ['Codice', 'Nome', 'Azienda', 'Prezzo', 'Pz/Cart', 'Disp.']
    df_display['Prezzo'] = df_display['Prezzo'].apply(format_currency)
    df_display['Disp.'] = df_display['Disp.'].apply(lambda x: '✅' if x else '❌')
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Azioni su prodotti
    st.markdown("---")
    st.subheader("Gestione Prodotti")
    
    for prodotto in prodotti[:10]:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"**{prodotto['codice']}** - {prodotto['nome']}")
        with col2:
            if st.button("✏️", key=f"edit_pr_{prodotto['id']}"):
                st.session_state.show_form = True
                st.session_state.editing_id = prodotto['id']
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"del_pr_{prodotto['id']}"):
                db.delete_prodotto(prodotto['id'])
                st.rerun()


def render_form_prodotto():
    """Form per nuovo/modifica prodotto"""
    prodotto = None
    if st.session_state.editing_id:
        prodotto = db.get_prodotto(st.session_state.editing_id)
        st.subheader("✏️ Modifica Prodotto")
    else:
        st.subheader("➕ Nuovo Prodotto")
    
    aziende = db.get_aziende()
    
    with st.form("form_prodotto"):
        col1, col2 = st.columns(2)
        
        with col1:
            azienda_id = st.selectbox(
                "Azienda *",
                options=[a['id'] for a in aziende],
                format_func=lambda x: next(a['nome'] for a in aziende if a['id'] == x),
                index=next((i for i, a in enumerate(aziende) if a['id'] == prodotto.get('azienda_id')), 0) if prodotto else 0
            )
            codice = st.text_input("Codice *", value=prodotto.get('codice', '') if prodotto else '')
            nome = st.text_input("Nome *", value=prodotto.get('nome', '') if prodotto else '')
            descrizione = st.text_input("Descrizione", value=prodotto.get('descrizione', '') if prodotto else '')
        
        with col2:
            prezzo = st.number_input("Prezzo Listino €", min_value=0.0, value=float(prodotto.get('prezzo_listino', 0)) if prodotto else 0.0, step=0.01)
            pezzi_cartone = st.number_input("Pezzi per Cartone", min_value=1, value=int(prodotto.get('pezzi_per_cartone', 1)) if prodotto else 1)
            unita = st.selectbox("Unità di Misura", ["PZ", "KG", "LT", "CF"], index=["PZ", "KG", "LT", "CF"].index(prodotto.get('unita_misura', 'PZ')) if prodotto else 0)
            disponibile = st.checkbox("Disponibile", value=prodotto.get('disponibile', True) if prodotto else True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salva", type="primary"):
                if not codice or not nome:
                    st.error("Codice e nome sono obbligatori")
                else:
                    data = {
                        'azienda_id': azienda_id,
                        'codice': codice,
                        'nome': nome,
                        'descrizione': descrizione,
                        'prezzo_listino': prezzo,
                        'pezzi_per_cartone': pezzi_cartone,
                        'unita_misura': unita,
                        'disponibile': 1 if disponibile else 0
                    }
                    if st.session_state.editing_id:
                        data['id'] = st.session_state.editing_id
                    db.save_prodotto(data)
                    st.success("Prodotto salvato!")
                    st.session_state.show_form = False
                    st.session_state.editing_id = None
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Annulla"):
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()


# ============================================
# PROMEMORIA
# ============================================

def render_promemoria():
    render_page_header("Promemoria", "Gestione scadenze e attività")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nuovo Promemoria", type="primary"):
            st.session_state.show_form = True
            st.session_state.editing_id = None
    
    if st.session_state.show_form:
        render_form_promemoria()
        return
    
    tab1, tab2 = st.tabs(["📋 Attivi", "✅ Completati"])
    
    with tab1:
        promemoria = db.get_promemoria(solo_attivi=True)
        oggi = date.today()
        
        if not promemoria:
            st.success("✨ Nessun promemoria attivo!")
        else:
            for p in promemoria:
                data_scad = datetime.strptime(p['data_scadenza'].split('T')[0] if 'T' in p['data_scadenza'] else p['data_scadenza'], '%Y-%m-%d').date()
                
                if data_scad < oggi:
                    badge = "🔴 SCADUTO"
                    bg_color = "#fee2e2"
                elif data_scad == oggi:
                    badge = "🟠 OGGI"
                    bg_color = "#fef3c7"
                else:
                    badge = f"🟢 {format_date(p['data_scadenza'])}"
                    bg_color = "#d1fae5"
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"""
                        <div style="background:{bg_color};padding:1rem;border-radius:8px;margin-bottom:0.5rem;">
                            <strong>{p['titolo']}</strong> <span>{badge}</span><br>
                            <span style="color:#6b7280;">{p.get('cliente_nome', '')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"compl_{p['id']}"):
                        db.completa_promemoria(p['id'])
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_p_{p['id']}"):
                        db.delete_promemoria(p['id'])
                        st.rerun()
    
    with tab2:
        completati = db.get_promemoria(solo_attivi=False)
        completati = [p for p in completati if p.get('completato')]
        
        if not completati:
            st.info("Nessun promemoria completato")
        else:
            for p in completati[:20]:
                st.markdown(f"✅ ~~{p['titolo']}~~ - {format_date(p.get('data_completamento', ''))}")


def render_form_promemoria():
    """Form per nuovo promemoria"""
    st.subheader("➕ Nuovo Promemoria")
    
    clienti = db.get_clienti()
    
    with st.form("form_promemoria"):
        titolo = st.text_input("Titolo *")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["chiamata", "preventivo", "sollecito", "ricontatto", "scadenza", "generico"])
            data_scadenza = st.date_input("Data Scadenza", value=date.today() + timedelta(days=1))
        with col2:
            priorita = st.selectbox("Priorità", ["alta", "media", "bassa"], index=1)
            cliente_options = {"": "Nessuno"} | {c['id']: c['ragione_sociale'] for c in clienti}
            cliente_id = st.selectbox("Cliente", options=list(cliente_options.keys()), format_func=lambda x: cliente_options[x])
        
        descrizione = st.text_area("Descrizione")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salva", type="primary"):
                if not titolo:
                    st.error("Il titolo è obbligatorio")
                else:
                    data = {
                        'titolo': titolo,
                        'descrizione': descrizione,
                        'cliente_id': cliente_id if cliente_id else None,
                        'tipo': tipo,
                        'data_scadenza': data_scadenza.isoformat(),
                        'priorita': priorita,
                        'completato': 0
                    }
                    db.save_promemoria(data)
                    st.success("Promemoria creato!")
                    st.session_state.show_form = False
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Annulla"):
                st.session_state.show_form = False
                st.rerun()


# ============================================
# CALENDARIO
# ============================================

def render_calendario():
    render_page_header("Calendario", "Pianificazione visite")
    st.info("🚧 Funzionalità calendario in sviluppo...")
    
    # Vista semplice per ora
    st.subheader("📅 Visite Pianificate")
    visite = db.get_visite_pianificate()
    
    if not visite:
        st.info("Nessuna visita pianificata")
    else:
        for v in visite:
            st.markdown(f"""
                <div class="ordine-row">
                    <strong>{format_date(v['data_pianificata'])}</strong><br>
                    {v.get('cliente_nome', 'N/D')} - {v.get('cliente_citta', '')}
                </div>
            """, unsafe_allow_html=True)


# ============================================
# REPORT
# ============================================

def render_report():
    render_page_header("Report", "Analisi e statistiche")
    
    anno = st.selectbox("Anno", options=[2024, 2025, 2026], index=1)
    
    tab1, tab2, tab3 = st.tabs(["🏭 Per Azienda", "👥 Per Cliente", "📦 Top Prodotti"])
    
    with tab1:
        st.subheader("Fatturato per Azienda")
        dati = db.get_fatturato_per_azienda(anno)
        
        if dati and any(d['fatturato'] for d in dati):
            df = pd.DataFrame(dati)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(df[df['fatturato'] > 0], values='fatturato', names='nome', title='Distribuzione Fatturato')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                df_display = df[['nome', 'num_ordini', 'fatturato']].copy()
                df_display.columns = ['Azienda', 'N. Ordini', 'Fatturato']
                df_display['Fatturato'] = df_display['Fatturato'].apply(format_currency)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            totale = sum(d['fatturato'] or 0 for d in dati)
            st.metric("TOTALE AGENZIA", format_currency(totale))
        else:
            st.info("Nessun dato disponibile")
    
    with tab2:
        st.subheader("Top Clienti")
        dati = db.get_fatturato_per_cliente(anno, limit=20)
        
        if dati:
            df = pd.DataFrame(dati)
            df_display = df[['ragione_sociale', 'citta', 'num_ordini', 'fatturato']].copy()
            df_display.columns = ['Cliente', 'Città', 'N. Ordini', 'Fatturato']
            df_display['Fatturato'] = df_display['Fatturato'].apply(format_currency)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun dato disponibile")
    
    with tab3:
        st.subheader("Top Prodotti")
        dati = db.get_top_prodotti(anno, limit=20)
        
        if dati:
            df = pd.DataFrame(dati)
            df_display = df[['codice', 'nome', 'azienda_nome', 'quantita_venduta', 'fatturato']].copy()
            df_display.columns = ['Codice', 'Prodotto', 'Azienda', 'Qtà Venduta', 'Fatturato']
            df_display['Fatturato'] = df_display['Fatturato'].apply(format_currency)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun dato disponibile")


# ============================================
# IMPOSTAZIONI
# ============================================

def render_impostazioni():
    render_page_header("Impostazioni", "Configurazione agente e sistema")
    
    tab1, tab2 = st.tabs(["👤 Dati Agente", "⚙️ Sistema"])
    
    with tab1:
        st.subheader("Dati Agente")
        agente = db.get_agente() or {}
        
        with st.form("form_agente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome", value=agente.get('nome', ''))
                cognome = st.text_input("Cognome", value=agente.get('cognome', ''))
                ragione_sociale = st.text_input("Ragione Sociale", value=agente.get('ragione_sociale', ''))
                indirizzo = st.text_input("Indirizzo", value=agente.get('indirizzo', ''))
                citta = st.text_input("Città", value=agente.get('citta', ''))
            
            with col2:
                telefono = st.text_input("Telefono", value=agente.get('telefono', ''))
                cellulare = st.text_input("Cellulare", value=agente.get('cellulare', ''))
                email = st.text_input("Email", value=agente.get('email', ''))
                partita_iva = st.text_input("Partita IVA", value=agente.get('partita_iva', ''))
                codice_enasarco = st.text_input("Codice ENASARCO", value=agente.get('codice_enasarco', ''))
            
            if st.form_submit_button("💾 Salva", type="primary"):
                data = {
                    'nome': nome,
                    'cognome': cognome,
                    'ragione_sociale': ragione_sociale,
                    'indirizzo': indirizzo,
                    'citta': citta,
                    'telefono': telefono,
                    'cellulare': cellulare,
                    'email': email,
                    'partita_iva': partita_iva,
                    'codice_enasarco': codice_enasarco
                }
                db.save_agente(data)
                st.success("Dati agente salvati!")
    
    with tab2:
        st.subheader("Informazioni Sistema")
        st.info("Versione: 1.0.0 - Portale Agente Professionale")
        
        stats = db.get_statistiche_dashboard()
        st.markdown(f"""
            - **Aziende:** {stats.get('totale_aziende', 0)}
            - **Clienti:** {stats.get('totale_clienti', 0)}
            - **Prodotti:** {stats.get('totale_prodotti', 0)}
            - **Ordini totali:** {stats.get('ordini_anno', 0)}
        """)


# ============================================
# MAIN
# ============================================

def main():
    # Inizializza database
    db.init_db()
    
    # Login check
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Sidebar
    render_sidebar()
    
    # Routing pagine
    page = st.session_state.current_page
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'ordini':
        render_ordini()
    elif page == 'nuovo_ordine':
        render_nuovo_ordine()
    elif page == 'clienti':
        render_clienti()
    elif page == 'aziende':
        render_aziende()
    elif page == 'prodotti':
        render_prodotti()
    elif page == 'calendario':
        render_calendario()
    elif page == 'promemoria':
        render_promemoria()
    elif page == 'report':
        render_report()
    elif page == 'impostazioni':
        render_impostazioni()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
