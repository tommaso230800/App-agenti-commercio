"""
PORTALE AGENTE DI COMMERCIO
Versione 2.0 - UI Professionale Migliorata
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
import plotly.express as px
import plotly.graph_objects as go
import base64
import calendar
import os

# Import moduli locali
import db
from pdf_ordine import genera_pdf_ordine_download
from email_sender import send_email_with_attachment


# Logo Agenzia (header globale)
AGENCY_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "agency_logo.jpg")


def render_agency_logo(width: int = 90):
    """Mostra il logo dell'agenzia se presente."""
    try:
        if os.path.exists(AGENCY_LOGO_PATH):
            st.image(AGENCY_LOGO_PATH, width=width)
    except Exception:
        pass


def _b64_to_bytes(b64_str: str) -> bytes:
    try:
        return base64.b64decode(b64_str)
    except Exception:
        return b""


def _file_to_b64(uploaded_file) -> tuple[str, str]:
    """(b64, mime)"""
    if not uploaded_file:
        return "", ""
    data = uploaded_file.getvalue()
    mime = getattr(uploaded_file, "type", "application/octet-stream") or "application/octet-stream"
    return base64.b64encode(data).decode("utf-8"), mime


def _initials(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()

# ============================================
# CONFIGURAZIONE PAGINA
# ============================================

st.set_page_config(
    page_title="Portale Agente",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PREMIUM - UI PROFESSIONALE
# ============================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1e3a5f;
        --primary-light: #2d5a87;
        --primary-dark: #152a45;
        --accent: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        --white: #ffffff;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Main container */
    .main .block-container {
        padding: 1rem 1rem 6rem 1rem;
        max-width: 100%;
    }

    /* Inputs & buttons (global polish) */
    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input {
        border-radius: 14px !important;
        border: 1px solid var(--gray-200) !important;
        background: var(--white) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow) !important;
        border: 1px solid var(--gray-200) !important;
        padding: 0.65rem 0.9rem !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        border: none !important;
    }

    /* Section card */
    .section-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--gray-900);
        margin: 0 0 0.75rem 0;
        display:flex;
        align-items:center;
        gap: 0.5rem;
    }

    /* KPI */
    .kpi {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
    }
    .kpi-top { display:flex; align-items:center; justify-content:space-between; }
    .kpi-icon {
        width: 38px; height: 38px; border-radius: 12px;
        display:flex; align-items:center; justify-content:center;
        background: var(--gray-100);
        font-size: 1.1rem;
    }
    .kpi-value { font-size: 1.45rem; font-weight: 800; margin-top: 0.4rem; }
    .kpi-label { color: var(--gray-500); font-weight: 600; font-size: 0.9rem; }

    /* Action tiles */
    .action-tile {
        background: linear-gradient(135deg, #ffffff, #f9fafb);
        border: 1px solid var(--gray-200);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: var(--shadow-md);
        height: 100%;
    }
    .action-title { font-weight: 800; margin: 0.25rem 0; }
    .action-sub { color: var(--gray-500); font-size: 0.9rem; margin: 0; }

    /* Tables */
    .stDataFrame, div[data-testid="stTable"] {
        border-radius: 18px !important;
        overflow: hidden !important;
        border: 1px solid var(--gray-200) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        background: var(--white);
        border-bottom: 1px solid var(--gray-200);
        padding: 0.75rem 1rem;
        margin: -1rem -1rem 1rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .top-nav-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .top-nav-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 0;
    }
    
    .top-nav-subtitle {
        font-size: 0.8rem;
        color: var(--gray-500);
        margin: 0;
    }
    
    /* Back button */
    .btn-back {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.5rem 0.75rem;
        background: var(--gray-100);
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        color: var(--gray-600);
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s ease;
        text-decoration: none;
    }
    
    .btn-back:hover {
        background: var(--gray-200);
        color: var(--gray-800);
    }
    
    /* Cards */
    .card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--gray-100);
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 0;
    }
    
    /* Metric Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    @media (min-width: 768px) {
        .metrics-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    
    .metric-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow-md);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.7rem;
        font-weight: 500;
        color: var(--gray-500);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* List Items */
    .list-item {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    
    .list-item:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow);
    }
    
    .list-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
    }
    
    .list-item-title {
        font-weight: 600;
        color: var(--gray-800);
        font-size: 0.95rem;
        margin: 0;
    }
    
    .list-item-subtitle {
        font-size: 0.8rem;
        color: var(--gray-500);
        margin: 0;
    }
    
    .list-item-meta {
        font-size: 0.75rem;
        color: var(--gray-400);
    }
    
    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .badge-bozza { background: #fef3c7; color: #92400e; }
    .badge-inviato { background: #d1fae5; color: #065f46; }
    .badge-warning { background: #fee2e2; color: #991b1b; }
    .badge-info { background: #dbeafe; color: #1e40af; }
    .badge-success { background: #d1fae5; color: #065f46; }
    
    /* Action Buttons Grid */
    .actions-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    @media (min-width: 768px) {
        .actions-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    
    .action-btn {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .action-btn:hover {
        border-color: var(--primary);
        background: var(--gray-50);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .action-btn-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .action-btn-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--gray-700);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border-color: var(--gray-300) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-light) !important;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Section header */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--gray-800);
        margin: 0;
    }
    
    .section-count {
        font-size: 0.8rem;
        color: var(--gray-500);
    }
    
    /* Floating button */
    .fab {
        position: fixed;
        bottom: 5rem;
        right: 1rem;
        width: 56px;
        height: 56px;
        border-radius: 16px;
        background: var(--primary);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: var(--shadow-lg);
        cursor: pointer;
        z-index: 90;
        transition: all 0.2s ease;
    }
    
    .fab:hover {
        transform: scale(1.05);
        background: var(--primary-light);
    }
    
    /* Bottom Navigation */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--white);
        border-top: 1px solid var(--gray-200);
        padding: 0.5rem 0.25rem;
        display: flex;
        justify-content: space-around;
        z-index: 100;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s ease;
        text-decoration: none;
        min-width: 60px;
    }
    
    .nav-item:hover {
        background: var(--gray-100);
    }
    
    .nav-item.active {
        color: var(--primary);
    }
    
    .nav-item.active .nav-icon {
        color: var(--primary);
    }
    
    .nav-icon {
        font-size: 1.25rem;
        margin-bottom: 0.125rem;
        color: var(--gray-500);
    }
    
    .nav-label {
        font-size: 0.65rem;
        font-weight: 500;
        color: var(--gray-500);
    }
    
    .nav-item.active .nav-label {
        color: var(--primary);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--gray-500);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-state-title {
        font-size: 1rem;
        font-weight: 500;
        color: var(--gray-600);
        margin-bottom: 0.5rem;
    }
    
    .empty-state-text {
        font-size: 0.875rem;
        color: var(--gray-400);
    }
    
    /* Expander fix */
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    /* Product row in order */
    .product-row {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 10px;
        padding: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    .product-row.in-cart {
        border-color: var(--success);
        background: #f0fdf4;
    }
    
    .product-name {
        font-weight: 600;
        color: var(--gray-800);
        font-size: 0.9rem;
    }
    
    .product-info {
        font-size: 0.75rem;
        color: var(--gray-500);
    }
    
    .product-price {
        font-weight: 700;
        color: var(--primary);
    }
    
    /* Step indicator */
    .steps {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 0 1rem;
    }
    
    .step-item {
        display: flex;
        align-items: center;
    }
    
    .step-circle {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .step-circle.active {
        background: var(--primary);
        color: white;
    }
    
    .step-circle.completed {
        background: var(--success);
        color: white;
    }
    
    .step-circle.inactive {
        background: var(--gray-200);
        color: var(--gray-500);
    }
    
    .step-line {
        width: 24px;
        height: 2px;
        margin: 0 0.25rem;
    }
    
    .step-line.active {
        background: var(--primary);
    }
    
    .step-line.inactive {
        background: var(--gray-200);
    }
    
    /* Order summary bar */
    .order-summary-bar {
        position: fixed;
        bottom: 60px;
        left: 0;
        right: 0;
        background: var(--primary);
        color: white;
        padding: 0.75rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 95;
    }
    
    .summary-item {
        text-align: center;
    }
    
    .summary-value {
        font-size: 1rem;
        font-weight: 700;
    }
    
    .summary-label {
        font-size: 0.65rem;
        opacity: 0.8;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE
# ============================================

def init_session_state():
    defaults = {
        'authenticated': False,
        'current_page': 'dashboard',
        'page_history': ['dashboard'],
        # Ordine
        'ordine_step': 1,
        'ordine_azienda_id': None,
        'ordine_cliente_id': None,
        'ordine_righe': [],
        'ordine_dettagli': {},
        # UI
        'show_form': False,
        'editing_id': None,
        'selected_azienda_view': None,  # Per vedere prodotti di un'azienda
        'selected_cliente_view': None,  # Vista dettaglio cliente
        # Calendario
        'cal_year': date.today().year,
        'cal_month': date.today().month,
        'cal_selected_date': date.today().isoformat(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

APP_PASSWORD = "demo123"


# ============================================
# NAVIGATION HELPERS
# ============================================

def navigate_to(page: str, add_to_history: bool = True):
    """Naviga a una pagina"""
    if add_to_history and st.session_state.current_page != page:
        st.session_state.page_history.append(st.session_state.current_page)
    st.session_state.current_page = page
    st.session_state.show_form = False
    st.session_state.editing_id = None

def go_back():
    """Torna alla pagina precedente"""
    if len(st.session_state.page_history) > 1:
        st.session_state.page_history.pop()
        st.session_state.current_page = st.session_state.page_history[-1]
    else:
        st.session_state.current_page = 'dashboard'
    st.session_state.show_form = False


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
    st.session_state.ordine_righe = []
    st.session_state.ordine_dettagli = {}

def calcola_totali_ordine() -> dict:
    totale_pezzi = sum(r.get('quantita_totale', 0) for r in st.session_state.ordine_righe)
    totale_cartoni = sum(r.get('quantita_cartoni', 0) for r in st.session_state.ordine_righe)
    imponibile = sum(r.get('importo_riga', 0) for r in st.session_state.ordine_righe)
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
# UI COMPONENTS
# ============================================

def render_top_nav(title: str, subtitle: str = None, show_back: bool = True):
    """Barra di navigazione superiore compatta"""
    # Menu a tendina globale (richiesta utente)
    pages = [
        ("Home", "dashboard"),
        ("Nuovo ordine", "nuovo_ordine"),
        ("Ordini", "ordini"),
        ("Clienti", "clienti"),
        ("Aziende", "aziende"),
        ("Promemoria", "promemoria"),
        ("Calendario", "calendario"),
    ]

    col1, col2, col3 = st.columns([1.2, 6, 2.2])
    
    with col1:
        if show_back and st.session_state.current_page != 'dashboard':
            if st.button("← Indietro", key="btn_back", use_container_width=True):
                go_back()
                st.rerun()
    
    with col2:
        # Logo agenzia + titolo
        l1, l2 = st.columns([1, 6])
        with l1:
            render_agency_logo(width=56)
        with l2:
            st.markdown(
                f"**{title}**" + (f" · <span style='color:#6b7280;font-size:0.85rem;'>{subtitle}</span>" if subtitle else ""),
                unsafe_allow_html=True,
            )
    
    with col3:
        labels = [p[0] for p in pages]
        values = [p[1] for p in pages]
        try:
            current_idx = values.index(st.session_state.current_page)
        except Exception:
            current_idx = 0
        sel = st.selectbox(
            "Menu",
            options=list(range(len(pages))),
            format_func=lambda i: labels[i],
            index=current_idx,
            label_visibility="collapsed",
        )
        target_page = values[int(sel)]
        if target_page != st.session_state.current_page:
            if target_page == 'nuovo_ordine':
                reset_ordine()
            navigate_to(target_page, add_to_history=True)
            st.rerun()
    
    st.markdown("<hr style='margin:0.5rem 0 1rem 0;border:none;border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)


def render_bottom_nav():
    """Barra di navigazione inferiore"""
    # Disattivata: l'utente vuole il menu a tendina.
    return


def render_metrics_grid(metrics: list):
    """Griglia di metriche"""
    cols = st.columns(len(metrics))
    for col, (value, label) in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)


# ============================================
# LOGIN
# ============================================

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div style="text-align:center;padding:3rem 0 1rem 0;"></div>""", unsafe_allow_html=True)
        # Logo agenzia sopra al login
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            render_agency_logo(width=180)
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0 1.5rem 0;">
                <h1 style="color:#1e3a5f;font-size:1.75rem;margin-bottom:0.25rem;">Portale Agente</h1>
                <p style="color:#6b7280;margin:0;">Gestionale Commerciale</p>
            </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Password", type="password", placeholder="Inserisci password")
        
        if st.button("Accedi", use_container_width=True, type="primary"):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password non corretta")
        
        st.caption("Password: demo123")


# ============================================
# DASHBOARD
# ============================================

def render_dashboard():
    render_top_nav("Dashboard", datetime.now().strftime("%A %d %B %Y").capitalize(), show_back=False)

    stats = db.get_statistiche_dashboard()

    # --- KPI (più professionale) ---
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        (k1, "👥", str(stats.get('totale_clienti', 0)), "Clienti"),
        (k2, "🏭", str(stats.get('totale_aziende', 0)), "Aziende"),
        (k3, "📦", str(stats.get('ordini_mese', 0)), "Ordini mese"),
        (k4, "💶", format_currency(stats.get('fatturato_mese', 0)), "Fatturato mese"),
        (k5, "📈", format_currency(stats.get('fatturato_anno', 0)), "Fatturato anno"),
        (k6, "⏰", str(stats.get('promemoria_oggi', 0)), "Promemoria oggi"),
    ]
    for col, ico, val, lab in [(x[0], x[1], x[2], x[3]) for x in kpis]:
        with col:
            st.markdown(
                f"""
                <div class="kpi">
                    <div class="kpi-top">
                        <div class="kpi-icon">{ico}</div>
                    </div>
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-label">{lab}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Quick actions (tile + bottoni) ---
    st.markdown("<div class='section-title'>⚡ Azioni rapide</div>", unsafe_allow_html=True)
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1:
        st.markdown("<div class='action-tile'><div class='action-title'>➕ Nuovo ordine</div><p class='action-sub'>Crea e invia un ordine</p></div>", unsafe_allow_html=True)
        if st.button("Apri", key="dash_new_order", use_container_width=True, type="primary"):
            reset_ordine(); navigate_to('nuovo_ordine'); st.rerun()
    with a2:
        st.markdown("<div class='action-tile'><div class='action-title'>👥 Clienti</div><p class='action-sub'>Anagrafica e contatti</p></div>", unsafe_allow_html=True)
        if st.button("Apri", key="dash_clienti", use_container_width=True):
            navigate_to('clienti'); st.rerun()
    with a3:
        st.markdown("<div class='action-tile'><div class='action-title'>🏭 Aziende</div><p class='action-sub'>Fornitori e cataloghi</p></div>", unsafe_allow_html=True)
        if st.button("Apri", key="dash_aziende", use_container_width=True):
            navigate_to('aziende'); st.rerun()
    with a4:
        st.markdown("<div class='action-tile'><div class='action-title'>📅 Calendario</div><p class='action-sub'>Visite e appuntamenti</p></div>", unsafe_allow_html=True)
        if st.button("Apri", key="dash_cal", use_container_width=True):
            navigate_to('calendario'); st.rerun()
    with a5:
        st.markdown("<div class='action-tile'><div class='action-title'>⏰ Promemoria</div><p class='action-sub'>Scadenze e note</p></div>", unsafe_allow_html=True)
        if st.button("Apri", key="dash_prom", use_container_width=True):
            navigate_to('promemoria'); st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Analisi (grafici) ---
    left, right = st.columns([2, 1])
    with left:
        st.markdown("<div class='section-card'><div class='section-title'>📈 Andamento fatturato (ultimi 12 mesi)</div>", unsafe_allow_html=True)
        try:
            series = db.get_fatturato_mensile_series(12)
        except Exception:
            series = []
        if series:
            df = pd.DataFrame(series)
            fig = px.line(df, x="mese", y="fatturato", markers=True, template="plotly_white")
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), font=dict(family="Inter"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun dato disponibile")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-card'><div class='section-title'>📌 Stato ordini (mese)</div>", unsafe_allow_html=True)
        try:
            counts = db.get_ordini_stato_counts_current_month()
        except Exception:
            counts = []
        if counts:
            dfc = pd.DataFrame(counts)
            fig2 = px.pie(dfc, names="stato", values="conteggio", hole=0.55, template="plotly_white")
            fig2.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), font=dict(family="Inter"), showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Nessun ordine nel mese")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Pianificazione (appuntamenti + promemoria) ---
    p1, p2 = st.columns(2)
    today = date.today()
    with p1:
        st.markdown("<div class='section-card'><div class='section-title'>📅 Prossimi appuntamenti (7 gg)</div>", unsafe_allow_html=True)
        try:
            apps = db.get_appuntamenti_range(today.isoformat(), (today + timedelta(days=7)).isoformat()) if hasattr(db, "get_appuntamenti_range") else []
        except Exception:
            apps = []
        if not apps:
            st.info("Nessun appuntamento nei prossimi 7 giorni")
        else:
            for a in apps[:8]:
                st.markdown(f"- **{format_date(a.get('data'))} {a.get('ora') or ''}** · {a.get('titolo','')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with p2:
        st.markdown("<div class='section-card'><div class='section-title'>⏰ Promemoria in scadenza (7 gg)</div>", unsafe_allow_html=True)
        try:
            proms = db.get_promemoria(solo_attivi=True)
            proms = [p for p in proms if p.get('data_scadenza') and str(p['data_scadenza']) <= (today + timedelta(days=7)).isoformat()]
        except Exception:
            proms = []
        if not proms:
            st.info("Nessun promemoria in scadenza")
        else:
            for p in proms[:8]:
                st.markdown(f"- **{format_date(p.get('data_scadenza'))}** · {p.get('titolo','')}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Ultimi ordini (card più pulite) ---
    st.markdown("<div class='section-card'><div class='section-title'>📦 Ultimi ordini</div>", unsafe_allow_html=True)
    ordini = db.get_ordini(limit=8)
    if not ordini:
        st.info("Nessun ordine presente")
    else:
        for o in ordini:
            badge_class = "badge-inviato" if o['stato'] == 'inviato' else "badge-bozza"
            stato_label = "INVIATO" if o['stato'] == 'inviato' else "BOZZA"
            st.markdown(f"""
                <div class="list-item" style="margin-bottom:0.75rem;">
                    <div class="list-item-header">
                        <div>
                            <p class="list-item-title">{o['numero']}</p>
                            <p class="list-item-subtitle">{o.get('cliente_ragione_sociale', 'N/D')} · {o.get('azienda_nome','')}</p>
                        </div>
                        <span class="badge {badge_class}">{stato_label}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="list-item-meta">{format_date(o['data_ordine'])}</span>
                        <span class="product-price">{format_currency(o['totale_finale'])}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


# ============================================
# AZIENDE (con gestione prodotti)
# ============================================

def render_aziende():
    render_top_nav("Aziende", "Fornitori e cataloghi")
    
    # Se stiamo visualizzando i prodotti di un'azienda
    if st.session_state.selected_azienda_view:
        render_azienda_prodotti()
        return
    
    # Form nuova azienda
    if st.session_state.show_form:
        render_form_azienda()
        return
    
    # Pulsante nuovo
    if st.button("➕ Nuova Azienda", type="primary"):
        st.session_state.show_form = True
        st.session_state.editing_id = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lista aziende
    aziende = db.get_aziende()
    
    if not aziende:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🏭</div>
                <div class="empty-state-title">Nessuna azienda</div>
                <div class="empty-state-text">Aggiungi la tua prima azienda per iniziare</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(aziende)} aziende**")
        
        for azienda in aziende:
            num_prodotti = len(db.get_prodotti(azienda_id=azienda['id']))

            c_logo, c_info, c_btn = st.columns([1, 6, 1])
            with c_logo:
                if azienda.get('logo_b64'):
                    st.image(_b64_to_bytes(azienda['logo_b64']), width=44)
                else:
                    ini = _initials(azienda.get('nome', '')) or "AZ"
                    st.markdown(
                        f"""
                        <div style='width:44px;height:44px;border-radius:12px;background:#111827;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;'>
                            {ini}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with c_info:
                subtitle = azienda.get('ragione_sociale', '') or azienda.get('citta', '') or 'Nessuna descrizione'
                st.markdown(
                    f"""
                    <div class="list-item" style="margin:0;">
                        <div class="list-item-header">
                            <div>
                                <p class="list-item-title">{azienda['nome']}</p>
                                <p class="list-item-subtitle">{subtitle}</p>
                            </div>
                            <span class="badge badge-info">{num_prodotti} prodotti</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_btn:
                # Un solo bottone per evitare sovrapposizioni su schermi diversi
                if st.button("Apri", key=f"prod_{azienda['id']}", use_container_width=True, type="primary"):
                    st.session_state.selected_azienda_view = azienda['id']
                    st.rerun()
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


def render_azienda_prodotti():
    """Visualizza e gestisce i prodotti di un'azienda specifica"""
    azienda = db.get_azienda(st.session_state.selected_azienda_view)
    
    if not azienda:
        st.session_state.selected_azienda_view = None
        st.rerun()
        return
    
    # Header con pulsante indietro + modifica azienda
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Indietro"):
            st.session_state.selected_azienda_view = None
            st.session_state.show_form = False
            st.rerun()
    with col2:
        st.markdown(f"**{azienda['nome']}** · Catalogo Prodotti")
    with col3:
        if st.button("✏️ Modifica", use_container_width=True):
            # Apri il form azienda (non il form prodotto)
            st.session_state.selected_azienda_view = None
            st.session_state.show_form = True
            st.session_state.editing_id = azienda['id']
            navigate_to('aziende', add_to_history=True)
            st.rerun()
    
    st.markdown("<hr style='margin:0.5rem 0 1rem 0;border:none;border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)
    
    # Form prodotto
    if st.session_state.show_form:
        render_form_prodotto(azienda['id'])
        return
    
    # Pulsante aggiungi prodotto
    if st.button("➕ Aggiungi Prodotto", type="primary"):
        st.session_state.show_form = True
        st.session_state.editing_id = None
        st.rerun()
    
    # Cerca
    search = st.text_input("🔍 Cerca prodotto", placeholder="Nome o codice...")
    
    # Lista prodotti
    prodotti = db.get_prodotti(azienda_id=azienda['id'], search=search if search else None, solo_disponibili=False)
    
    st.markdown(f"**{len(prodotti)} prodotti**")
    
    if not prodotti:
        st.info("Nessun prodotto per questa azienda")
    else:
        for prod in prodotti:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                disp = "✅" if prod.get('disponibile') else "❌"
                st.markdown(f"""
                    <div class="product-row">
                        <div class="product-name">{prod['nome']} {disp}</div>
                        <div class="product-info">Cod: {prod['codice']} · 6 pz/cartone</div>
                        <div class="product-price">{format_currency(prod['prezzo_listino'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key=f"ep_{prod['id']}"):
                    st.session_state.show_form = True
                    st.session_state.editing_id = prod['id']
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"dp_{prod['id']}"):
                    db.delete_prodotto(prod['id'])
                    st.rerun()


def render_form_azienda():
    """Form per nuova/modifica azienda"""
    azienda = None
    if st.session_state.editing_id:
        azienda = db.get_azienda(st.session_state.editing_id)
    
    st.markdown(f"**{'✏️ Modifica' if azienda else '➕ Nuova'} Azienda**")
    
    with st.form("form_azienda"):
        nome = st.text_input("Nome Azienda *", value=azienda.get('nome', '') if azienda else '')
        ragione_sociale = st.text_input("Ragione Sociale", value=azienda.get('ragione_sociale', '') if azienda else '')

        # Logo azienda (salvato nel DB in base64)
        if azienda and azienda.get('logo_b64'):
            st.caption("Logo attuale")
            st.image(_b64_to_bytes(azienda['logo_b64']), width=140)
        uploaded_logo = st.file_uploader("Carica logo (PNG/JPG)", type=["png", "jpg", "jpeg"], help="Sarà mostrato nelle liste e nella selezione ordine")
        
        col1, col2 = st.columns(2)
        with col1:
            indirizzo = st.text_input("Indirizzo", value=azienda.get('indirizzo', '') if azienda else '')
            citta = st.text_input("Città", value=azienda.get('citta', '') if azienda else '')
        with col2:
            telefono = st.text_input("Telefono", value=azienda.get('telefono', '') if azienda else '')
            email = st.text_input("Email", value=azienda.get('email', '') if azienda else '')
        
        partita_iva = st.text_input("Partita IVA", value=azienda.get('partita_iva', '') if azienda else '')
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salva", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annulla", use_container_width=True)
        
        if submitted:
            if not nome:
                st.error("Il nome è obbligatorio")
            else:
                data = {
                    'nome': nome,
                    'ragione_sociale': ragione_sociale,
                    'indirizzo': indirizzo,
                    'citta': citta,
                    'telefono': telefono,
                    'email': email,
                    'partita_iva': partita_iva,
                }

                if uploaded_logo is not None:
                    b64, mime = _file_to_b64(uploaded_logo)
                    if b64:
                        data['logo_b64'] = b64
                        data['logo_mime'] = mime
                if st.session_state.editing_id:
                    data['id'] = st.session_state.editing_id
                db.save_azienda(data)
                st.success("Salvato!")
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()
        
        if cancelled:
            st.session_state.show_form = False
            st.session_state.editing_id = None
            st.rerun()


def render_form_prodotto(azienda_id: str):
    """Form per nuovo/modifica prodotto"""
    prodotto = None
    if st.session_state.editing_id:
        prodotto = db.get_prodotto(st.session_state.editing_id)
    
    st.markdown(f"**{'✏️ Modifica' if prodotto else '➕ Nuovo'} Prodotto**")
    
    with st.form("form_prodotto"):
        col1, col2 = st.columns(2)
        with col1:
            codice = st.text_input("Codice *", value=prodotto.get('codice', '') if prodotto else '')
            nome = st.text_input("Nome *", value=prodotto.get('nome', '') if prodotto else '')
        with col2:
            prezzo = st.number_input("Prezzo €", min_value=0.0, value=float(prodotto.get('prezzo_listino', 0)) if prodotto else 0.0, step=0.01)
            # Regola: 1 cartone = 6 pezzi (fisso)
            pezzi_cartone = 6
            st.number_input(
                "Pezzi/Cartone (fisso)",
                min_value=1,
                value=pezzi_cartone,
                step=1,
                disabled=True,
                help="In questa app il cartone è sempre composto da 6 pezzi."
            )
        
        descrizione = st.text_input("Descrizione", value=prodotto.get('descrizione', '') if prodotto else '')
        disponibile = st.checkbox("Disponibile", value=prodotto.get('disponibile', True) if prodotto else True)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salva", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annulla", use_container_width=True)
        
        if submitted:
            if not codice or not nome:
                st.error("Codice e nome obbligatori")
            else:
                data = {
                    'azienda_id': azienda_id,
                    'codice': codice,
                    'nome': nome,
                    'descrizione': descrizione,
                    'prezzo_listino': prezzo,
                    'pezzi_per_cartone': 6,
                    'disponibile': 1 if disponibile else 0
                }
                if st.session_state.editing_id:
                    data['id'] = st.session_state.editing_id
                db.save_prodotto(data)
                st.success("Salvato!")
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()
        
        if cancelled:
            st.session_state.show_form = False
            st.session_state.editing_id = None
            st.rerun()


# ============================================
# CLIENTI
# ============================================

def render_clienti():
    render_top_nav("Clienti", "Anagrafica")

    # Vista dettaglio cliente (per evitare sovrapposizioni/expander)
    if st.session_state.selected_cliente_view:
        cliente = db.get_cliente(st.session_state.selected_cliente_view)
        if not cliente:
            st.session_state.selected_cliente_view = None
            st.rerun()
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Indietro"):
                st.session_state.selected_cliente_view = None
                st.rerun()
        with col2:
            st.markdown(f"**{cliente['ragione_sociale']}**")

        st.markdown("<hr style='margin:0.5rem 0 1rem 0;border:none;border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                **Codice:** {cliente.get('codice','-')}  
                **Indirizzo:** {cliente.get('indirizzo','-')}  
                **CAP/Città:** {cliente.get('cap','')} {cliente.get('citta','')} ({cliente.get('provincia','')})
                """
            )
        with c2:
            st.markdown(
                f"""
                **Telefono:** {cliente.get('telefono','-')}  
                **Email:** {cliente.get('email','-')}  
                **P.IVA:** {cliente.get('partita_iva','-')}
                """
            )

        b1, b2, _ = st.columns([1, 1, 2])
        with b1:
            if st.button("✏️ Modifica", type="primary", use_container_width=True):
                st.session_state.show_form = True
                st.session_state.editing_id = cliente['id']
                st.rerun()
        with b2:
            if cliente.get('indirizzo'):
                st.link_button("🗺️ Maps", f"https://maps.google.com/?q={cliente['indirizzo']}, {cliente.get('citta','')}", use_container_width=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        render_bottom_nav()
        return
    
    if st.session_state.show_form:
        render_form_cliente()
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Cerca", placeholder="Ragione sociale, città...", label_visibility="collapsed")
    with col2:
        if st.button("➕ Nuovo", type="primary", use_container_width=True):
            st.session_state.show_form = True
            st.session_state.editing_id = None
            st.rerun()
    
    clienti = db.get_clienti(search=search if search else None)
    
    st.markdown(f"**{len(clienti)} clienti**")
    
    if not clienti:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <div class="empty-state-title">Nessun cliente</div>
                <div class="empty-state-text">Aggiungi il tuo primo cliente</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for cliente in clienti:
            c1, c2 = st.columns([6, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="list-item" style="margin:0;">
                        <div class="list-item-header">
                            <div>
                                <p class="list-item-title">{cliente['ragione_sociale']}</p>
                                <p class="list-item-subtitle">{cliente.get('citta','')} ({cliente.get('provincia','')}) · {cliente.get('indirizzo','') or ''}</p>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("→", key=f"open_cli_{cliente['id']}", use_container_width=True):
                    st.session_state.selected_cliente_view = cliente['id']
                    st.rerun()
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


def render_form_cliente():
    """Form per nuovo/modifica cliente"""
    cliente = None
    if st.session_state.editing_id:
        cliente = db.get_cliente(st.session_state.editing_id)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.show_form = False
            st.session_state.editing_id = None
            st.rerun()
    with col2:
        st.markdown(f"**{'✏️ Modifica' if cliente else '➕ Nuovo'} Cliente**")
    
    st.markdown("<hr style='margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    
    with st.form("form_cliente"):
        codice = st.text_input("Codice", value=cliente.get('codice', '') if cliente else '')
        ragione_sociale = st.text_input("Ragione Sociale *", value=cliente.get('ragione_sociale', '') if cliente else '')
        
        indirizzo = st.text_input("Indirizzo", value=cliente.get('indirizzo', '') if cliente else '')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            citta = st.text_input("Città", value=cliente.get('citta', '') if cliente else '')
        with col2:
            provincia = st.text_input("Prov.", value=cliente.get('provincia', '') if cliente else '', max_chars=2)
        with col3:
            cap = st.text_input("CAP", value=cliente.get('cap', '') if cliente else '', max_chars=5)
        
        col1, col2 = st.columns(2)
        with col1:
            telefono = st.text_input("Telefono", value=cliente.get('telefono', '') if cliente else '')
        with col2:
            email = st.text_input("Email", value=cliente.get('email', '') if cliente else '')
        
        partita_iva = st.text_input("Partita IVA", value=cliente.get('partita_iva', '') if cliente else '')
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salva", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annulla", use_container_width=True)
        
        if submitted:
            if not ragione_sociale:
                st.error("Ragione sociale obbligatoria")
            else:
                data = {
                    'codice': codice,
                    'ragione_sociale': ragione_sociale,
                    'indirizzo': indirizzo,
                    'citta': citta,
                    'provincia': provincia.upper() if provincia else '',
                    'cap': cap,
                    'telefono': telefono,
                    'email': email,
                    'partita_iva': partita_iva,
                }
                if st.session_state.editing_id:
                    data['id'] = st.session_state.editing_id
                db.save_cliente(data)
                st.success("Cliente salvato!")
                st.session_state.show_form = False
                st.session_state.editing_id = None
                st.rerun()
        
        if cancelled:
            st.session_state.show_form = False
            st.session_state.editing_id = None
            st.rerun()


# ============================================
# ORDINI
# ============================================

def render_ordini():
    render_top_nav("Ordini", "Storico ordini")
    
    # Filtri
    col1, col2 = st.columns(2)
    with col1:
        stato = st.selectbox("Stato", ["Tutti", "Bozza", "Inviato"], label_visibility="collapsed")
    with col2:
        if st.button("➕ Nuovo Ordine", type="primary", use_container_width=True):
            reset_ordine()
            navigate_to('nuovo_ordine')
            st.rerun()
    
    stato_filter = None if stato == "Tutti" else stato.lower()
    ordini = db.get_ordini(stato=stato_filter)
    
    st.markdown(f"**{len(ordini)} ordini**")
    
    if not ordini:
        st.info("Nessun ordine trovato")
    else:
        for o in ordini:
            badge_class = "badge-inviato" if o['stato'] == 'inviato' else "badge-bozza"
            
            with st.expander(f"{o['numero']} · {o.get('cliente_ragione_sociale', 'N/D')} · {format_currency(o['totale_finale'])}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        **Azienda:** {o.get('azienda_nome', 'N/D')}<br>
                        **Data:** {format_date(o['data_ordine'])}<br>
                        **Stato:** {o['stato'].upper()}
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        **Pezzi:** {o.get('totale_pezzi', 0)}<br>
                        **Imponibile:** {format_currency(o.get('imponibile', 0))}<br>
                        **Totale:** {format_currency(o['totale_finale'])}
                    """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📄 PDF", key=f"pdf_{o['id']}"):
                        pdf_bytes, filename = genera_pdf_ordine_download(o['id'])
                        if pdf_bytes:
                            st.download_button("⬇️ Scarica", pdf_bytes, filename, "application/pdf", key=f"dl_{o['id']}")
                with col2:
                    if o['stato'] == 'bozza':
                        if st.button("✅ Invia", key=f"inv_{o['id']}"):
                            db.update_stato_ordine(o['id'], 'inviato')
                            st.success("Inviato!")
                            st.rerun()
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


# ============================================
# NUOVO ORDINE
# ============================================

def render_nuovo_ordine():
    render_top_nav("Nuovo Ordine", f"Step {st.session_state.ordine_step}/6")
    
    # Step indicator
    steps = ["Fornitore", "Cliente", "Sede", "Articoli", "Dettagli", "Conferma"]
    render_steps(st.session_state.ordine_step, steps)
    
    # Render step corrente
    if st.session_state.ordine_step == 1:
        render_step_fornitore()
    elif st.session_state.ordine_step == 2:
        render_step_cliente()
    elif st.session_state.ordine_step == 3:
        render_step_sede()
    elif st.session_state.ordine_step == 4:
        render_step_articoli()
    elif st.session_state.ordine_step == 5:
        render_step_dettagli()
    elif st.session_state.ordine_step == 6:
        render_step_conferma()
    
    # Barra totali (da step 4)
    if st.session_state.ordine_step >= 4 and st.session_state.ordine_righe:
        totali = calcola_totali_ordine()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background:#1e3a5f;color:white;padding:0.75rem 1rem;border-radius:10px;display:flex;justify-content:space-around;text-align:center;">
                <div><div style="font-size:1rem;font-weight:700;">{totali['totale_pezzi']}</div><div style="font-size:0.65rem;opacity:0.8;">PEZZI</div></div>
                <div><div style="font-size:1rem;font-weight:700;">{totali['totale_cartoni']:.0f}</div><div style="font-size:0.65rem;opacity:0.8;">CARTONI</div></div>
                <div><div style="font-size:1rem;font-weight:700;">{format_currency(totali['imponibile'])}</div><div style="font-size:0.65rem;opacity:0.8;">IMPONIBILE</div></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


def render_steps(current: int, steps: list):
    """Indicatore steps compatto"""
    cols = st.columns(len(steps) * 2 - 1)
    col_idx = 0
    
    for i, step in enumerate(steps, 1):
        with cols[col_idx]:
            if i < current:
                st.markdown(f"<div style='text-align:center;'><div style='width:28px;height:28px;border-radius:50%;background:#10b981;color:white;display:inline-flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;'>✓</div></div>", unsafe_allow_html=True)
            elif i == current:
                st.markdown(f"<div style='text-align:center;'><div style='width:28px;height:28px;border-radius:50%;background:#1e3a5f;color:white;display:inline-flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;'>{i}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center;'><div style='width:28px;height:28px;border-radius:50%;background:#e5e7eb;color:#9ca3af;display:inline-flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;'>{i}</div></div>", unsafe_allow_html=True)
        col_idx += 1
        
        if i < len(steps):
            with cols[col_idx]:
                color = "#1e3a5f" if i < current else "#e5e7eb"
                st.markdown(f"<div style='height:2px;background:{color};margin-top:13px;'></div>", unsafe_allow_html=True)
            col_idx += 1
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_step_fornitore():
    """Step 1: Selezione azienda"""
    st.markdown("**Seleziona Azienda**")
    
    aziende = db.get_aziende()
    
    if not aziende:
        st.warning("Nessuna azienda disponibile. Creane una prima.")
        if st.button("➕ Crea Azienda"):
            navigate_to('aziende')
            st.rerun()
        return
    
    for azienda in aziende:
        num_prod = len(db.get_prodotti(azienda_id=azienda['id']))
        selected = st.session_state.ordine_azienda_id == azienda['id']

        c1, c2, c3 = st.columns([1, 5, 1])
        with c1:
            # Logo azienda (se presente)
            if azienda.get('logo_b64'):
                st.image(_b64_to_bytes(azienda['logo_b64']), width=48)
            else:
                ini = _initials(azienda.get('nome', '')) or "AZ"
                st.markdown(
                    f"""
                    <div style='width:48px;height:48px;border-radius:12px;background:#111827;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;'>
                        {ini}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with c2:
            st.markdown(
                f"""<div class='list-item' style="margin:0;{'border-color:#3b82f6;background:#eff6ff;' if selected else ''}">
                        <p class='list-item-title' style='margin-bottom:0.125rem'>{azienda['nome']}</p>
                        <p class='list-item-subtitle' style='margin:0'>{num_prod} prodotti</p>
                    </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            if st.button("✓" if selected else "Seleziona", key=f"sel_az_{azienda['id']}", type="primary" if selected else "secondary", use_container_width=True):
                st.session_state.ordine_azienda_id = azienda['id']
                st.session_state.ordine_step = 2
                st.rerun()


def render_step_cliente():
    """Step 2: Selezione cliente"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.ordine_step = 1
            st.rerun()
    with col2:
        st.markdown("**Seleziona Cliente**")
    
    search = st.text_input("🔍 Cerca cliente", placeholder="Ragione sociale, città...")
    
    clienti = db.get_clienti(search=search if search else None)
    
    for cliente in clienti[:15]:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
                <div class="list-item">
                    <p class="list-item-title">{cliente['ragione_sociale']}</p>
                    <p class="list-item-subtitle">{cliente.get('indirizzo', '')} · {cliente.get('citta', '')} ({cliente.get('provincia', '')})</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("→", key=f"sel_cl_{cliente['id']}"):
                st.session_state.ordine_cliente_id = cliente['id']
                st.session_state.ordine_step = 3
                st.rerun()


def render_step_sede():
    """Step 3: Conferma sede"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.ordine_step = 2
            st.rerun()
    with col2:
        st.markdown("**Sede di Consegna**")
    
    cliente = db.get_cliente(st.session_state.ordine_cliente_id)
    
    st.markdown(f"""
        <div class="card">
            <p style="font-weight:600;margin-bottom:0.5rem;">{cliente['ragione_sociale']}</p>
            <p style="color:#6b7280;margin:0;">{cliente.get('indirizzo', 'N/D')}</p>
            <p style="color:#6b7280;margin:0;">{cliente.get('cap', '')} {cliente.get('citta', '')} ({cliente.get('provincia', '')})</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Avanti →", type="primary", use_container_width=True):
        st.session_state.ordine_step = 4
        st.rerun()


def render_step_articoli():
    """Step 4: Selezione articoli"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.ordine_step = 3
            st.rerun()
    with col2:
        st.markdown("**Seleziona Articoli**")
    
    # Cerca
    search = st.text_input("🔍 Cerca prodotto", placeholder="Nome o codice...")
    
    # Prodotti azienda
    prodotti = db.get_prodotti(azienda_id=st.session_state.ordine_azienda_id, search=search if search else None)

    # Prefill: ultimo prezzo/quantità usati da questo cliente per prodotto
    prefs = {}
    if st.session_state.ordine_cliente_id and st.session_state.ordine_azienda_id:
        try:
            prefs = db.get_cliente_prodotti_pref(st.session_state.ordine_cliente_id, st.session_state.ordine_azienda_id)
        except Exception:
            prefs = {}
    
    st.markdown(f"**{len(prodotti)} prodotti** · {len(st.session_state.ordine_righe)} nel carrello")
    
    for prod in prodotti:
        in_cart = next((r for r in st.session_state.ordine_righe if r['prodotto_id'] == prod['id']), None)
        pref = prefs.get(prod['id']) if not in_cart else None
        
        st.markdown(f"""
            <div class="product-row {'in-cart' if in_cart else ''}">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                    <div>
                        <span class="product-name">{prod['nome']}</span>
                        <div class="product-info">Cod: {prod['codice']} · 6 pz/cart</div>
                    </div>
                    <span class="product-price">{format_currency(prod['prezzo_listino'])}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        with col1:
            cartoni = st.number_input(
                "Cartoni",
                min_value=0,
                step=1,
                value=int(in_cart['quantita_cartoni']) if in_cart else int((pref or {}).get('quantita_cartoni', 0) or 0),
                key=f"cart_{prod['id']}",
                label_visibility="visible",
            )
        with col2:
            pezzi = st.number_input(
                "Pezzi",
                min_value=0,
                step=1,
                value=int(in_cart['quantita_pezzi']) if in_cart else int((pref or {}).get('quantita_pezzi', 0) or 0),
                key=f"pz_{prod['id']}",
                label_visibility="visible",
            )
        with col3:
            # Prezzo modificabile nell'ordine (override rispetto al listino)
            prezzo_unitario = st.number_input(
                "Prezzo €/pz",
                min_value=0.0,
                step=0.01,
                value=float(in_cart['prezzo_unitario']) if in_cart else float((pref or {}).get('prezzo_unitario') or prod['prezzo_listino']),
                key=f"pr_{prod['id']}",
                label_visibility="visible",
            )
        with col4:
            sconto = st.number_input(
                "Sconto %",
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                value=float(in_cart['sconto_riga']) if in_cart else float((pref or {}).get('sconto_riga', 0) or 0.0),
                key=f"sc_{prod['id']}",
                label_visibility="visible",
            )

        # Calcolo live: totale pezzi = cartoni*6 + pezzi (regola fissa)
        qta_tot_live = (int(cartoni) * 6) + int(pezzi)
        if pref and not in_cart:
            st.caption(f"Prefill ultimo ordine: cartoni {pref.get('quantita_cartoni',0)} · pezzi {pref.get('quantita_pezzi',0)} · prezzo {format_currency(pref.get('prezzo_unitario',0))}")
        st.caption(f"Totale pezzi: **{qta_tot_live}** (cartone = 6 pz)")

        with col5:
            if st.button("+" if not in_cart else "↻", key=f"add_{prod['id']}"):
                if cartoni > 0 or pezzi > 0:
                    qta_tot = (int(cartoni) * 6) + int(pezzi)
                    prezzo_finale = float(prezzo_unitario) * (1 - float(sconto)/100)
                    importo = qta_tot * prezzo_finale
                    
                    nuova_riga = {
                        'prodotto_id': prod['id'],
                        'prodotto_codice': prod['codice'],
                        'prodotto_nome': prod['nome'],
                        'pezzi_per_cartone': 6,
                        'quantita_cartoni': int(cartoni),
                        'quantita_pezzi': int(pezzi),
                        'quantita_totale': int(qta_tot),
                        'prezzo_unitario': float(prezzo_unitario),
                        'sconto_riga': sconto,
                        'prezzo_finale': float(prezzo_finale),
                        'importo_riga': importo
                    }
                    
                    # Aggiorna o aggiungi
                    st.session_state.ordine_righe = [r for r in st.session_state.ordine_righe if r['prodotto_id'] != prod['id']]
                    st.session_state.ordine_righe.append(nuova_riga)
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.ordine_righe:
        if st.button("Avanti →", type="primary", use_container_width=True):
            st.session_state.ordine_step = 5
            st.rerun()


def render_step_dettagli():
    """Step 5: Dettagli ordine"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.ordine_step = 4
            st.rerun()
    with col2:
        st.markdown("**Dettagli Ordine**")
    
    pagamento = st.selectbox("Pagamento", ["Bonifico 30gg", "Bonifico 60gg", "Rimessa diretta", "Contanti"],
                            index=0)
    consegna = st.selectbox("Consegna", ["Franco destino", "Franco partenza", "Ritiro"],
                           index=0)
    sconto_chiusura = st.number_input(
        "Sconto Chiusura %",
        min_value=0.0,
        max_value=50.0,
        value=float(st.session_state.ordine_dettagli.get('sconto_chiusura', 0) or 0.0)
    )
    note = st.text_area("Note ordine", value=st.session_state.ordine_dettagli.get('note', '') or '')

    # Email invio PDF (opzionale)
    default_email = st.session_state.ordine_dettagli.get('email_destinatario')
    if not default_email and st.session_state.ordine_cliente_id:
        try:
            default_email = (db.get_cliente(st.session_state.ordine_cliente_id) or {}).get('email', '')
        except Exception:
            default_email = ''
    email_destinatario = st.text_input(
        "📧 Invia conferma/proforma PDF a (opzionale)",
        value=default_email or '',
        placeholder="es. acquisti@cliente.it"
    )
    
    st.session_state.ordine_dettagli = {
        'pagamento': pagamento,
        'consegna_tipo': consegna,
        'sconto_chiusura': sconto_chiusura,
        'note': note,
        'email_destinatario': email_destinatario
    }
    
    if st.button("Avanti →", type="primary", use_container_width=True):
        st.session_state.ordine_step = 6
        st.rerun()


def render_step_conferma():
    """Step 6: Riepilogo e conferma"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.ordine_step = 5
            st.rerun()
    with col2:
        st.markdown("**Riepilogo Ordine**")
    
    azienda = db.get_azienda(st.session_state.ordine_azienda_id) if st.session_state.ordine_azienda_id else None
    cliente = db.get_cliente(st.session_state.ordine_cliente_id) if st.session_state.ordine_cliente_id else None
    totali = calcola_totali_ordine()
    
    # Riepilogo testata (no HTML fragile su mobile)
    st.markdown("#### Riepilogo")
    st.write(f"Fornitore: {azienda['nome'] if azienda else '—'}")
    st.write(f"Cliente: {cliente['ragione_sociale'] if cliente else '—'}")
    st.write(f"Articoli: {len(st.session_state.ordine_righe)}")
    
    # Articoli
    for riga in st.session_state.ordine_righe:
        st.markdown(f"- {riga['prodotto_nome']}: {riga['quantita_cartoni']} cart. + {riga['quantita_pezzi']} pz = **{format_currency(riga['importo_riga'])}**")
    
    # Totali (render stabile su iOS)
    with st.container():
        st.success(
            f"Totale pezzi: {totali['totale_pezzi']}\n\n"
            f"Imponibile: {format_currency(totali['imponibile'])}\n\n"
            + (f"Sconto chiusura: {totali['sconto_chiusura']}%\n\n" if totali['sconto_chiusura'] > 0 else "")
            + f"TOTALE: {format_currency(totali['totale_finale'])}"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salva Bozza", use_container_width=True):
            salva_ordine('bozza')
    with col2:
        if st.button("📤 INVIA ORDINE", type="primary", use_container_width=True):
            salva_ordine('inviato')


def salva_ordine(stato: str):
    """Salva l'ordine.

    - Salva sempre su DB
    - Se stato=inviato: genera PDF e, se inserita email, invia allegato
    - Aggiorna anche la tabella prefill (ultimo prezzo/quantità per cliente/prodotto) tramite db.save_ordine
    """
    # Validazioni base + fallback (se per qualche motivo l'azienda non è in sessione)
    if not st.session_state.ordine_azienda_id:
        # Prova a inferire l'azienda dal primo prodotto in carrello
        try:
            if st.session_state.ordine_righe:
                pid = st.session_state.ordine_righe[0].get('prodotto_id')
                if pid:
                    prod = db.get_prodotto(pid)
                    if prod and prod.get('azienda_id'):
                        st.session_state.ordine_azienda_id = prod['azienda_id']
        except Exception:
            pass
    if not st.session_state.ordine_azienda_id:
        st.error("Seleziona un fornitore (azienda) prima di salvare.")
        return
    if not st.session_state.ordine_cliente_id:
        st.error("Seleziona un cliente prima di salvare.")
        return
    if not st.session_state.ordine_righe:
        st.error("Aggiungi almeno un articolo all'ordine.")
        return

    # verifica che l'azienda esista davvero
    if not db.get_azienda(st.session_state.ordine_azienda_id):
        st.error("Fornitore non valido. Torna indietro e seleziona l'azienda.")
        return

    totali = calcola_totali_ordine()
    det = st.session_state.ordine_dettagli

    testata = {
        'numero': db.get_prossimo_numero_ordine(),
        'data_ordine': date.today().isoformat(),
        'azienda_id': st.session_state.ordine_azienda_id,
        'cliente_id': st.session_state.ordine_cliente_id,
        'pagamento': det.get('pagamento'),
        'consegna_tipo': det.get('consegna_tipo'),
        'totale_pezzi': totali['totale_pezzi'],
        'totale_cartoni': totali['totale_cartoni'],
        'imponibile': totali['imponibile'],
        'sconto_chiusura': totali['sconto_chiusura'],
        'totale_finale': totali['totale_finale'],
        'stato': stato,
        'note': det.get('note'),
    }

    try:
        ordine_id = db.save_ordine(testata, st.session_state.ordine_righe)
    except Exception as e:
        st.error(f"Errore nel salvataggio ordine: {e}")
        return

    # Bozza
    if stato != 'inviato':
        st.success("💾 Bozza salvata")
        reset_ordine()
        navigate_to('ordini')
        st.rerun()

    # INVIATO: PDF + email
    st.success("✅ Ordine INVIATO e salvato nel database!")

    pdf_bytes, filename = None, None
    try:
        pdf_bytes, filename = genera_pdf_ordine_download(ordine_id)
    except Exception as e:
        st.error(f"Errore generazione PDF: {e}")

    if pdf_bytes and filename:
        st.download_button(
            "⬇️ Scarica Conferma/Proforma (PDF)",
            pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )

    email_dest = (det or {}).get('email_destinatario')
    if email_dest:
        if not pdf_bytes:
            st.warning("PDF non disponibile: impossibile inviare email con allegato.")
        else:
            try:
                cliente = db.get_cliente(testata['cliente_id']) or {}
                send_email_with_attachment(
                    to_email=email_dest,
                    subject=f"Conferma Ordine {testata['numero']} - {cliente.get('ragione_sociale','Cliente')}",
                    body=(
                        f"Buongiorno,\n\n"
                        f"in allegato la conferma/proforma dell'ordine {testata['numero']} del {testata['data_ordine']}.\n\n"
                        f"Cordiali saluti"
                    ),
                    attachment_bytes=pdf_bytes,
                    attachment_filename=filename or "ordine.pdf",
                    mime_type="application/pdf",
                )
                st.success(f"📧 Email inviata a: {email_dest}")
            except Exception as e:
                st.error(f"⚠️ Ordine salvato, ma invio email fallito: {e}")
    else:
        st.info("📧 Email non inserita: puoi inviare il PDF più tardi dalla pagina Ordini")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Vai a Ordini", type="primary", use_container_width=True):
            reset_ordine()
            navigate_to('ordini')
            st.rerun()
    with col2:
        if st.button("➕ Nuovo Ordine", use_container_width=True):
            reset_ordine()
            navigate_to('nuovo_ordine')
            st.rerun()
    return


# ============================================
# PROMEMORIA
# ============================================

def render_promemoria():
    render_top_nav("Promemoria", "Scadenze")
    
    if st.session_state.show_form:
        render_form_promemoria()
        return
    
    if st.button("➕ Nuovo Promemoria", type="primary"):
        st.session_state.show_form = True
        st.rerun()
    
    promemoria = db.get_promemoria(solo_attivi=True)
    oggi = date.today()
    
    if not promemoria:
        st.success("✨ Nessun promemoria attivo!")
    else:
        for p in promemoria:
            try:
                data_scad = datetime.strptime(p['data_scadenza'].split('T')[0], '%Y-%m-%d').date()
            except:
                data_scad = oggi
            
            if data_scad < oggi:
                badge = "🔴 SCADUTO"
                bg = "#fee2e2"
            elif data_scad == oggi:
                badge = "🟠 OGGI"
                bg = "#fef3c7"
            else:
                badge = f"📅 {format_date(p['data_scadenza'])}"
                bg = "#f3f4f6"
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                    <div class="list-item" style="background:{bg};">
                        <p class="list-item-title">{p['titolo']}</p>
                        <p class="list-item-subtitle">{p.get('cliente_nome', '')} · {badge}</p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=f"cp_{p['id']}"):
                    db.completa_promemoria(p['id'])
                    st.rerun()
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


def render_form_promemoria():
    """Form nuovo promemoria"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Indietro"):
            st.session_state.show_form = False
            st.rerun()
    with col2:
        st.markdown("**Nuovo Promemoria**")
    
    with st.form("form_prom"):
        titolo = st.text_input("Titolo *")
        data_scadenza = st.date_input("Scadenza", value=date.today() + timedelta(days=1))
        priorita = st.selectbox("Priorità", ["alta", "media", "bassa"], index=1)
        descrizione = st.text_area("Note")
        
        if st.form_submit_button("💾 Salva", type="primary", use_container_width=True):
            if titolo:
                db.save_promemoria({
                    'titolo': titolo,
                    'data_scadenza': data_scadenza.isoformat(),
                    'priorita': priorita,
                    'descrizione': descrizione,
                    'completato': 0
                })
                st.success("Salvato!")
                st.session_state.show_form = False
                st.rerun()


def render_calendario():
    """Calendario stile "app calendario" (mese con eventi visibili), più viste Giorno/Settimana/Elenco."""
    render_top_nav("Calendario", "Appuntamenti")

    # --- controlli mese/anno + today ---
    year = st.session_state.cal_year
    month = st.session_state.cal_month
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        y = st.selectbox(
            "Anno",
            options=list(range(date.today().year - 2, date.today().year + 3)),
            index=list(range(date.today().year - 2, date.today().year + 3)).index(year),
        )
    with c2:
        mese_labels = [calendar.month_name[m] for m in range(1, 13)]
        m = st.selectbox(
            "Mese",
            options=list(range(1, 13)),
            format_func=lambda mm: mese_labels[mm - 1],
            index=month - 1,
        )
    with c3:
        if st.button("Oggi", use_container_width=True):
            st.session_state.cal_year = date.today().year
            st.session_state.cal_month = date.today().month
            st.session_state.cal_selected_date = date.today().isoformat()
            st.rerun()

    if y != year or m != month:
        st.session_state.cal_year = y
        st.session_state.cal_month = m
        # se il giorno selezionato è fuori mese, resetta al primo
        try:
            dsel = date.fromisoformat(st.session_state.cal_selected_date)
            if dsel.year != y or dsel.month != m:
                st.session_state.cal_selected_date = date(y, m, 1).isoformat()
        except Exception:
            st.session_state.cal_selected_date = date(y, m, 1).isoformat()
        st.rerun()

    # --- carica appuntamenti del mese (con fallback) ---
    first_day = date(y, m, 1)
    last_day = date(y, m, calendar.monthrange(y, m)[1])
    if hasattr(db, "get_appuntamenti_range"):
        month_apps = db.get_appuntamenti_range(first_day.isoformat(), last_day.isoformat())
    else:
        conn = db.get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM appuntamenti WHERE data >= ? AND data <= ? ORDER BY data, ora",
                (first_day.isoformat(), last_day.isoformat()),
            ).fetchall()
            month_apps = [dict(r) for r in rows]
        finally:
            conn.close()

    # indicizza per giorno
    apps_by_day: Dict[str, List[Dict]] = {}
    for a in month_apps:
        dd = str(a.get("data") or "")
        if dd:
            apps_by_day.setdefault(dd, []).append(a)

    # CSS (griglia 7 colonne sempre, anche su iPhone) + tema light/dark
    st.markdown(
        """
        <style>
        .cal-wrap{width:100%;}
        .cal-head{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:0.25rem;}
        .cal-head div{font-weight:800;text-align:center;opacity:.9;font-size:0.85rem;}
        .cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;}
        .cal-cell{border-radius:14px;padding:8px;min-height:92px;}
        .cal-cell.out{opacity:.45;}
        .cal-day{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
        .cal-daynum{font-weight:900;font-size:0.95rem;}
        .cal-badge{font-size:0.75rem;opacity:.70;}
        .cal-event{display:block;font-size:0.74rem;line-height:1.15rem;padding:2px 6px;border-radius:8px;margin:3px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
        .cal-today{outline:2px solid rgba(0,140,255,0.55);}
        .cal-selected{outline:2px solid rgba(0,200,120,0.55);}

        /* Light */
        @media (prefers-color-scheme: light){
          .cal-cell{border:1px solid rgba(0,0,0,0.10);background:rgba(255,255,255,0.98);}
          .cal-blue{background:rgba(70,130,255,0.18);border:1px solid rgba(70,130,255,0.35);} 
          .cal-orange{background:rgba(255,165,0,0.18);border:1px solid rgba(255,165,0,0.35);} 
          .cal-green{background:rgba(0,200,120,0.16);border:1px solid rgba(0,200,120,0.30);} 
        }

        /* Dark */
        @media (prefers-color-scheme: dark){
          .cal-cell{border:1px solid rgba(255,255,255,0.12);background:rgba(255,255,255,0.04);} 
          .cal-blue{background:rgba(70,130,255,0.35);border:1px solid rgba(70,130,255,0.55);} 
          .cal-orange{background:rgba(255,165,0,0.28);border:1px solid rgba(255,165,0,0.50);} 
          .cal-green{background:rgba(0,200,120,0.25);border:1px solid rgba(0,200,120,0.45);} 
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Barra vista stile calendario (come l'app iPhone)
    view = st.radio(
        "",
        options=["Elenco", "Giorno", "Sett.", "Mese", "Planner"],
        index=3,
        horizontal=True,
        label_visibility="collapsed",
    )

    # --- MESE (stile calendario) ---
    if view == "Mese":
        mesi_it = [
            "gennaio","febbraio","marzo","aprile","maggio","giugno",
            "luglio","agosto","settembre","ottobre","novembre","dicembre"
        ]
        st.markdown(f"## {mesi_it[m-1]} {y}")

        # costruisci 6 settimane con date (Monday-first)
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(y, m)
        week_days = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
        st.markdown("<div class='cal-wrap'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='cal-head'>" + "".join([f"<div>{w}</div>" for w in week_days]) + "</div>",
            unsafe_allow_html=True,
        )

        def _pick_class(title: str) -> str:
            t = (title or "").lower()
            if any(k in t for k in ["sold", "pag", "incasso", "fatt"]) :
                return "cal-orange"
            if any(k in t for k in ["visita", "giro", "cliente", "appunt"]) :
                return "cal-blue"
            return "cal-green"

        today_iso = date.today().isoformat()
        selected_iso = str(st.session_state.get('cal_selected_date') or "")
        html = ["<div class='cal-grid'>"]
        for w in weeks:
            for d in w:
                day_iso = d.isoformat()
                out = (d.month != m)
                day_apps = apps_by_day.get(day_iso, [])
                badge = f"{len(day_apps)}" if day_apps else ""
                extra = ""
                if day_iso == today_iso:
                    extra += " cal-today"
                if day_iso == selected_iso:
                    extra += " cal-selected"
                cell_cls = ("cal-cell out" if out else "cal-cell") + extra
                html.append(f"<div class='{cell_cls}'>")
                html.append("<div class='cal-day'>")
                html.append(f"<div class='cal-daynum'>{d.day}</div>")
                html.append(f"<div class='cal-badge'>{badge}</div>")
                html.append("</div>")
                for a in day_apps[:4]:
                    titolo = a.get("titolo") or ""
                    ora = a.get("ora") or ""
                    label = (f"{ora} " if ora else "") + titolo
                    cls = _pick_class(titolo)
                    html.append(f"<span class='cal-event {cls}'>{label}</span>")
                html.append("</div>")
        html.append("</div>")
        st.markdown("\n".join(html), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Dettaglio giorno**")
        try:
            selected_date = date.fromisoformat(st.session_state.cal_selected_date)
        except Exception:
            selected_date = date.today()
            st.session_state.cal_selected_date = selected_date.isoformat()

        # selettore giorno (comodo su mobile)
        picked = st.date_input("Seleziona giorno", value=selected_date)
        if picked.isoformat() != st.session_state.cal_selected_date:
            st.session_state.cal_selected_date = picked.isoformat()
            st.rerun()

        # carica appuntamenti giorno
        if hasattr(db, "get_appuntamenti_by_date"):
            day_apps = db.get_appuntamenti_by_date(picked.isoformat())
        else:
            conn = db.get_connection()
            try:
                rows = conn.execute(
                    "SELECT * FROM appuntamenti WHERE data = ? ORDER BY ora",
                    (picked.isoformat(),),
                ).fetchall()
                day_apps = [dict(r) for r in rows]
            finally:
                conn.close()

        if not day_apps:
            st.info("Nessun appuntamento in questa data")
        else:
            for a in day_apps:
                titolo = a.get('titolo', '')
                ora = a.get('ora') or ""
                cliente_nome = a.get('cliente_nome') or ""
                luogo = a.get('luogo') or ""
                st.markdown(
                    f"""
                    <div class='list-item' style='margin:0.25rem 0;'>
                        <p class='list-item-title' style='margin-bottom:0.15rem;'>{ora} {titolo}</p>
                        <p class='list-item-subtitle' style='margin:0;'>{cliente_nome}{' · ' if cliente_nome and luogo else ''}{luogo}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("🗑️ Elimina", key=f"del_app_{a['id']}"):
                    db.delete_appuntamento(a['id'])
                    st.rerun()

        st.markdown("---")
        st.markdown("**➕ Nuovo appuntamento**")
        clienti = db.get_clienti()
        cli_opts = [("", "— Nessun cliente —")] + [(c['id'], c['ragione_sociale']) for c in clienti]
        with st.form("form_app"):
            titolo = st.text_input("Titolo *", placeholder="Es. Giro visite / consegna / degustazione")
            senza_ora = st.checkbox("Senza ora (tutto il giorno)", value=False)
            ora_t = None
            if not senza_ora:
                ora_t = st.time_input("Ora", value=datetime.now().replace(second=0, microsecond=0).time())
            cliente_id = st.selectbox("Cliente", options=[x[0] for x in cli_opts], format_func=lambda _id: dict(cli_opts).get(_id, ""))
            luogo = st.text_input("Luogo", placeholder="Indirizzo / città")
            note = st.text_area("Note")
            saved = st.form_submit_button("Salva", type="primary", use_container_width=True)
            if saved:
                if not titolo:
                    st.error("Inserisci il titolo")
                else:
                    ora_str = None
                    try:
                        if ora_t:
                            ora_str = ora_t.strftime("%H:%M")
                    except Exception:
                        ora_str = None
                    db.save_appuntamento({
                        'titolo': titolo,
                        'data': picked.isoformat(),
                        'ora': ora_str,
                        'cliente_id': cliente_id or None,
                        'luogo': luogo,
                        'note': note,
                    })
                    st.success("Appuntamento salvato")
                    st.rerun()

    # --- ELENCO ---
    if view == "Elenco":
        st.markdown("**Appuntamenti del mese**")
        if not month_apps:
            st.info("Nessun appuntamento nel mese")
        else:
            for a in month_apps:
                st.write(f"{a.get('data','')}  {a.get('ora') or ''}  —  {a.get('titolo','')}")

    # --- GIORNO ---
    if view == "Giorno":
        st.markdown("Seleziona un giorno nella vista **Mese** (oppure col selettore) per vedere il dettaglio.")

    # --- SETTIMANA ---
    if view == "Sett.":
        st.markdown("Vista settimana (in arrivo). Per ora usa **Mese** o **Elenco**.")

    # --- PLANNER ---
    if view == "Planner":
        st.markdown("Planner (in arrivo): lista attività con priorità e scadenze.")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()


# ============================================
# MAIN
# ============================================

def main():
    db.init_db()
    
    if not st.session_state.authenticated:
        render_login()
        return
    
    page = st.session_state.current_page
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'aziende':
        render_aziende()
    elif page == 'clienti':
        render_clienti()
    elif page == 'ordini':
        render_ordini()
    elif page == 'nuovo_ordine':
        render_nuovo_ordine()
    elif page == 'calendario':
        render_calendario()
    elif page == 'promemoria':
        render_promemoria()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
