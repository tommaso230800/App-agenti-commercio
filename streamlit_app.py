import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import pandas as pd

# Carica variabili d'ambiente
load_dotenv()

# Configurazione pagina
st.set_page_config(
    page_title="Agente di Commercio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato per mobile
st.markdown("""
<style>
    /* Mobile-friendly */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            padding: 15px;
            font-size: 18px;
        }
        .stTextInput > div > div > input {
            font-size: 16px;
            padding: 12px;
        }
        .stSelectbox > div > div > select {
            font-size: 16px;
        }
    }
    
    /* Card style */
    .client-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Priority badges */
    .priority-alta { color: #ff4b4b; font-weight: bold; }
    .priority-media { color: #ffa500; font-weight: bold; }
    .priority-bassa { color: #00cc00; font-weight: bold; }
    
    /* Category badges */
    .cat-a { background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 4px; }
    .cat-b { background-color: #ffa500; color: white; padding: 2px 8px; border-radius: 4px; }
    .cat-c { background-color: #00cc00; color: white; padding: 2px 8px; border-radius: 4px; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Inizializza session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# Database mock (per demo senza Supabase)
if 'clienti' not in st.session_state:
    st.session_state.clienti = []
if 'visite' not in st.session_state:
    st.session_state.visite = []
if 'promemoria' not in st.session_state:
    st.session_state.promemoria = []
if 'visite_pianificate' not in st.session_state:
    st.session_state.visite_pianificate = []

# Password dal file .env o default
APP_PASSWORD = os.getenv('APP_PASSWORD', 'demo123')

# ==================== FUNZIONI HELPER ====================

def get_province_italiane():
    """Lista delle province italiane"""
    return [
        "Agrigento", "Alessandria", "Ancona", "Aosta", "Arezzo", "Ascoli Piceno",
        "Asti", "Avellino", "Bari", "Barletta-Andria-Trani", "Belluno", "Benevento",
        "Bergamo", "Biella", "Bologna", "Bolzano", "Brescia", "Brindisi", "Cagliari",
        "Caltanissetta", "Campobasso", "Caserta", "Catania", "Catanzaro", "Chieti",
        "Como", "Cosenza", "Cremona", "Crotone", "Cuneo", "Enna", "Fermo", "Ferrara",
        "Firenze", "Foggia", "Forlì-Cesena", "Frosinone", "Genova", "Gorizia",
        "Grosseto", "Imperia", "Isernia", "L'Aquila", "La Spezia", "Latina", "Lecce",
        "Lecco", "Livorno", "Lodi", "Lucca", "Macerata", "Mantova", "Massa-Carrara",
        "Matera", "Messina", "Milano", "Modena", "Monza e Brianza", "Napoli", "Novara",
        "Nuoro", "Oristano", "Padova", "Palermo", "Parma", "Pavia", "Perugia",
        "Pesaro e Urbino", "Pescara", "Piacenza", "Pisa", "Pistoia", "Pordenone",
        "Potenza", "Prato", "Ragusa", "Ravenna", "Reggio Calabria", "Reggio Emilia",
        "Rieti", "Rimini", "Roma", "Rovigo", "Salerno", "Sassari", "Savona", "Siena",
        "Siracusa", "Sondrio", "Sud Sardegna", "Taranto", "Teramo", "Terni", "Torino",
        "Trapani", "Trento", "Treviso", "Trieste", "Udine", "Varese", "Venezia",
        "Verbano-Cusio-Ossola", "Vercelli", "Verona", "Vibo Valentia", "Vicenza", "Viterbo"
    ]

def generate_id():
    """Genera un ID unico"""
    import uuid
    return str(uuid.uuid4())

def get_cliente_by_id(cliente_id):
    """Trova un cliente per ID"""
    for c in st.session_state.clienti:
        if c['id'] == cliente_id:
            return c
    return None

def format_currency(value):
    """Formatta un valore come valuta"""
    if value:
        return f"€ {value:,.2f}"
    return "-"

# ==================== PAGINA LOGIN ====================

def show_login():
    st.markdown("# 💼 Agente di Commercio")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Accesso")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Accedi", use_container_width=True, type="primary"):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password non corretta")

# ==================== SIDEBAR NAVIGAZIONE ====================

def show_sidebar():
    with st.sidebar:
        st.markdown("## 💼 Menu")
        st.markdown("---")
        
        # Conta promemoria in scadenza oggi
        oggi = date.today()
        promemoria_oggi = len([p for p in st.session_state.promemoria 
                               if not p['completato'] and 
                               datetime.fromisoformat(p['data_scadenza']).date() <= oggi])
        
        # Conta visite pianificate oggi
        visite_oggi = len([v for v in st.session_state.visite_pianificate 
                          if not v['completata'] and 
                          datetime.fromisoformat(v['data_pianificata']).date() == oggi])
        
        pages = {
            'dashboard': '📊 Dashboard',
            'clienti': '👥 Clienti',
            'calendario': '📅 Calendario',
            'giro': f'🚗 Giro Giornaliero ({visite_oggi})',
            'visite': '✅ Registra Visita',
            'promemoria': f'🔔 Promemoria ({promemoria_oggi})',
            'report': '📈 Report'
        }
        
        for key, label in pages.items():
            if st.button(label, use_container_width=True, 
                        type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()
        
        st.markdown("---")
        
        # Info rapide
        st.markdown("### 📌 Riepilogo")
        st.metric("Clienti", len(st.session_state.clienti))
        st.metric("Visite questo mese", len([v for v in st.session_state.visite 
                                             if datetime.fromisoformat(v['data_visita']).month == oggi.month]))
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# ==================== PAGINA DASHBOARD ====================

def get_saluto():
    """Restituisce un saluto basato sull'ora del giorno"""
    ora = datetime.now().hour
    if ora < 12:
        return "Buongiorno"
    elif ora < 18:
        return "Buon pomeriggio"
    else:
        return "Buonasera"

def get_meteo_emoji(mese):
    """Emoji stagionale"""
    if mese in [12, 1, 2]:
        return "❄️"
    elif mese in [3, 4, 5]:
        return "🌸"
    elif mese in [6, 7, 8]:
        return "☀️"
    else:
        return "🍂"

def calcola_statistiche_mese(visite, oggi):
    """Calcola tutte le statistiche del mese corrente"""
    visite_mese = [v for v in visite if datetime.fromisoformat(v['data_visita']).month == oggi.month 
                   and datetime.fromisoformat(v['data_visita']).year == oggi.year]
    
    # Mese precedente per confronto
    mese_prec = oggi.month - 1 if oggi.month > 1 else 12
    anno_prec = oggi.year if oggi.month > 1 else oggi.year - 1
    visite_mese_prec = [v for v in visite if datetime.fromisoformat(v['data_visita']).month == mese_prec 
                        and datetime.fromisoformat(v['data_visita']).year == anno_prec]
    
    stats = {
        'visite_mese': len(visite_mese),
        'visite_mese_prec': len(visite_mese_prec),
        'visite_positive': len([v for v in visite_mese if v['esito'] == 'positivo']),
        'visite_negative': len([v for v in visite_mese if v['esito'] == 'negativo']),
        'ordini_mese': len([v for v in visite_mese if v.get('ordine_effettuato')]),
        'ordini_mese_prec': len([v for v in visite_mese_prec if v.get('ordine_effettuato')]),
        'totale_ordini': sum([v.get('importo_ordine', 0) or 0 for v in visite_mese if v.get('ordine_effettuato')]),
        'totale_ordini_prec': sum([v.get('importo_ordine', 0) or 0 for v in visite_mese_prec if v.get('ordine_effettuato')]),
    }
    
    # Calcola percentuali e delta
    stats['tasso_conversione'] = (stats['visite_positive'] / stats['visite_mese'] * 100) if stats['visite_mese'] > 0 else 0
    stats['media_ordine'] = (stats['totale_ordini'] / stats['ordini_mese']) if stats['ordini_mese'] > 0 else 0
    
    # Delta rispetto mese precedente
    stats['delta_visite'] = stats['visite_mese'] - stats['visite_mese_prec']
    stats['delta_ordini'] = stats['ordini_mese'] - stats['ordini_mese_prec']
    stats['delta_totale'] = stats['totale_ordini'] - stats['totale_ordini_prec']
    
    return stats

def show_dashboard():
    oggi = date.today()
    ora_corrente = datetime.now()
    
    # Header con saluto personalizzato
    meteo = get_meteo_emoji(oggi.month)
    st.markdown(f"# {meteo} {get_saluto()}!")
    st.markdown(f"**{oggi.strftime('%A %d %B %Y')}** • {ora_corrente.strftime('%H:%M')}")
    st.markdown("---")
    
    # ==================== ALERT SECTION ====================
    # Mostra alert importanti in cima
    
    promemoria_scaduti = [p for p in st.session_state.promemoria 
                         if not p['completato'] 
                         and datetime.fromisoformat(p['data_scadenza']).date() < oggi]
    
    clienti_non_visitati_30gg = []
    for cliente in st.session_state.clienti:
        ultime_visite = [v for v in st.session_state.visite if v['cliente_id'] == cliente['id']]
        if ultime_visite:
            ultima = max(ultime_visite, key=lambda x: x['data_visita'])
            giorni = (oggi - datetime.fromisoformat(ultima['data_visita']).date()).days
            if giorni > 30:
                clienti_non_visitati_30gg.append({'cliente': cliente, 'giorni': giorni})
        else:
            # Mai visitato
            clienti_non_visitati_30gg.append({'cliente': cliente, 'giorni': 999})
    
    if promemoria_scaduti or len(clienti_non_visitati_30gg) > 0:
        with st.container():
            if promemoria_scaduti:
                st.error(f"⚠️ **{len(promemoria_scaduti)} promemoria scaduti!** Controlla la sezione Promemoria.")
            if len(clienti_non_visitati_30gg) >= 3:
                st.warning(f"📍 **{len(clienti_non_visitati_30gg)} clienti** non visitati da oltre 30 giorni")
        st.markdown("")
    
    # ==================== QUICK ACTIONS ====================
    st.markdown("### ⚡ Azioni Rapide")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Nuovo Cliente", use_container_width=True, type="primary"):
            st.session_state.page = 'clienti'
            st.rerun()
    
    with col2:
        if st.button("✅ Registra Visita", use_container_width=True, type="primary"):
            st.session_state.page = 'visite'
            st.rerun()
    
    with col3:
        if st.button("🔔 Nuovo Promemoria", use_container_width=True, type="primary"):
            st.session_state.page = 'promemoria'
            st.rerun()
    
    with col4:
        if st.button("🚗 Giro di Oggi", use_container_width=True, type="primary"):
            st.session_state.page = 'giro'
            st.rerun()
    
    st.markdown("---")
    
    # ==================== METRICHE PRINCIPALI ====================
    st.markdown("### 📊 Performance Mese Corrente")
    
    stats = calcola_statistiche_mese(st.session_state.visite, oggi)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "👥 Clienti", 
            len(st.session_state.clienti),
            help="Totale clienti in anagrafica"
        )
    
    with col2:
        delta_visite = f"{stats['delta_visite']:+d}" if stats['delta_visite'] != 0 else None
        st.metric(
            "✅ Visite", 
            stats['visite_mese'],
            delta=delta_visite,
            help="Visite effettuate questo mese vs mese precedente"
        )
    
    with col3:
        st.metric(
            "🎯 Conversione", 
            f"{stats['tasso_conversione']:.0f}%",
            help="Percentuale visite positive"
        )
    
    with col4:
        delta_ordini = f"{stats['delta_ordini']:+d}" if stats['delta_ordini'] != 0 else None
        st.metric(
            "📦 Ordini", 
            stats['ordini_mese'],
            delta=delta_ordini,
            help="Ordini questo mese vs mese precedente"
        )
    
    with col5:
        delta_totale = f"€{stats['delta_totale']:+,.0f}" if stats['delta_totale'] != 0 else None
        st.metric(
            "💰 Fatturato", 
            format_currency(stats['totale_ordini']),
            delta=delta_totale,
            help="Totale ordini questo mese"
        )
    
    # Riga secondaria metriche
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        visite_oggi_count = len([v for v in st.session_state.visite_pianificate 
                                if datetime.fromisoformat(v['data_pianificata']).date() == oggi 
                                and not v['completata']])
        st.metric("🚗 Da visitare oggi", visite_oggi_count)
    
    with col2:
        promemoria_attivi = len([p for p in st.session_state.promemoria if not p['completato']])
        promemoria_oggi = len([p for p in st.session_state.promemoria 
                              if not p['completato'] 
                              and datetime.fromisoformat(p['data_scadenza']).date() == oggi])
        st.metric("🔔 Promemoria", promemoria_attivi, delta=f"{promemoria_oggi} oggi" if promemoria_oggi else None)
    
    with col3:
        st.metric("📈 Media Ordine", format_currency(stats['media_ordine']))
    
    with col4:
        visite_positive = stats['visite_positive']
        visite_negative = stats['visite_negative']
        st.metric("✅ Positive", visite_positive, help=f"❌ Negative: {visite_negative}")
    
    with col5:
        # Clienti visitati questo mese
        clienti_visitati_mese = set()
        for v in st.session_state.visite:
            if datetime.fromisoformat(v['data_visita']).month == oggi.month:
                clienti_visitati_mese.add(v['cliente_id'])
        clienti_da_visitare = len(st.session_state.clienti) - len(clienti_visitati_mese)
        st.metric("📍 Da visitare", clienti_da_visitare, help="Clienti non ancora visitati questo mese")
    
    st.markdown("---")
    
    # ==================== GRAFICI ====================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Andamento Ultimi 7 Giorni")
        
        # Prepara dati ultimi 7 giorni
        dati_7gg = []
        for i in range(6, -1, -1):
            giorno = oggi - timedelta(days=i)
            visite_giorno = len([v for v in st.session_state.visite 
                                if datetime.fromisoformat(v['data_visita']).date() == giorno])
            ordini_giorno = sum([v.get('importo_ordine', 0) or 0 for v in st.session_state.visite 
                                if datetime.fromisoformat(v['data_visita']).date() == giorno 
                                and v.get('ordine_effettuato')])
            dati_7gg.append({
                'Giorno': giorno.strftime('%a %d'),
                'Visite': visite_giorno,
                'Ordini (€)': ordini_giorno
            })
        
        if any(d['Visite'] > 0 for d in dati_7gg):
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(x=[d['Giorno'] for d in dati_7gg], 
                      y=[d['Visite'] for d in dati_7gg],
                      name="Visite",
                      marker_color='#636EFA'),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(x=[d['Giorno'] for d in dati_7gg], 
                          y=[d['Ordini (€)'] for d in dati_7gg],
                          name="Ordini €",
                          line=dict(color='#00CC96', width=3)),
                secondary_y=True
            )
            
            fig.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                hovermode="x unified"
            )
            fig.update_yaxes(title_text="Visite", secondary_y=False)
            fig.update_yaxes(title_text="€", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessun dato disponibile per i grafici. Inizia a registrare visite!")
    
    with col2:
        st.markdown("### 🗺️ Performance per Provincia")
        
        # Raggruppa visite per provincia
        visite_per_provincia = {}
        for v in st.session_state.visite:
            if datetime.fromisoformat(v['data_visita']).month == oggi.month:
                cliente = get_cliente_by_id(v['cliente_id'])
                if cliente:
                    prov = cliente.get('provincia', 'N/D')
                    if prov not in visite_per_provincia:
                        visite_per_provincia[prov] = {'visite': 0, 'ordini': 0, 'totale': 0}
                    visite_per_provincia[prov]['visite'] += 1
                    if v.get('ordine_effettuato'):
                        visite_per_provincia[prov]['ordini'] += 1
                        visite_per_provincia[prov]['totale'] += v.get('importo_ordine', 0) or 0
        
        if visite_per_provincia:
            import plotly.express as px
            
            df_prov = pd.DataFrame([
                {'Provincia': k, 'Visite': v['visite'], 'Ordini': v['ordini'], 'Totale': v['totale']}
                for k, v in visite_per_provincia.items()
            ]).sort_values('Visite', ascending=True).tail(8)
            
            fig = px.bar(df_prov, y='Provincia', x='Visite', orientation='h',
                        color='Totale', color_continuous_scale='Greens',
                        hover_data=['Ordini', 'Totale'])
            fig.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nessuna visita registrata questo mese")
    
    st.markdown("---")
    
    # ==================== SEZIONI INFORMATIVE ====================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🚗 Visite Oggi")
        
        visite_oggi = [v for v in st.session_state.visite_pianificate 
                      if datetime.fromisoformat(v['data_pianificata']).date() == oggi]
        
        if visite_oggi:
            completate = len([v for v in visite_oggi if v['completata']])
            totali = len(visite_oggi)
            
            # Progress bar
            progress = completate / totali if totali > 0 else 0
            st.progress(progress, text=f"{completate}/{totali} completate")
            
            for v in sorted(visite_oggi, key=lambda x: x.get('ora_inizio') or '23:59'):
                cliente = get_cliente_by_id(v['cliente_id'])
                if cliente:
                    status = "✅" if v['completata'] else "⏳"
                    ora = ""
                    if v.get('ora_inizio'):
                        ora = datetime.fromisoformat(f"2000-01-01T{v['ora_inizio']}").strftime("%H:%M") + " - "
                    st.markdown(f"{status} {ora}**{cliente['nome_azienda']}**")
        else:
            st.info("Nessuna visita pianificata")
            if st.button("📅 Pianifica", key="plan_today"):
                st.session_state.page = 'calendario'
                st.rerun()
    
    with col2:
        st.markdown("### 🔔 Promemoria Urgenti")
        
        promemoria_urgenti = [p for p in st.session_state.promemoria 
                             if not p['completato'] 
                             and datetime.fromisoformat(p['data_scadenza']).date() <= oggi + timedelta(days=3)]
        promemoria_urgenti.sort(key=lambda x: x['data_scadenza'])
        
        if promemoria_urgenti:
            for p in promemoria_urgenti[:5]:
                data_scad = datetime.fromisoformat(p['data_scadenza']).date()
                
                if data_scad < oggi:
                    badge = "🔴"
                elif data_scad == oggi:
                    badge = "🟠"
                else:
                    badge = "🟡"
                
                priorita_icon = {"alta": "‼️", "media": "❗", "bassa": ""}[p['priorita']]
                
                st.markdown(f"{badge} {priorita_icon} **{p['titolo']}**")
                st.caption(f"Scade: {data_scad.strftime('%d/%m')}")
        else:
            st.success("✨ Nessun promemoria urgente!")
    
    with col3:
        st.markdown("### 💰 Ultimi Ordini")
        
        ordini_recenti = [v for v in st.session_state.visite if v.get('ordine_effettuato')]
        ordini_recenti.sort(key=lambda x: x['data_visita'], reverse=True)
        
        if ordini_recenti:
            for v in ordini_recenti[:5]:
                cliente = get_cliente_by_id(v['cliente_id'])
                if cliente:
                    data = datetime.fromisoformat(v['data_visita']).strftime("%d/%m")
                    importo = format_currency(v.get('importo_ordine', 0))
                    st.markdown(f"💵 **{importo}**")
                    st.caption(f"{cliente['nome_azienda']} • {data}")
        else:
            st.info("Nessun ordine registrato")
    
    st.markdown("---")
    
    # ==================== CLIENTI DA RICONTATTARE ====================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Clienti da Ricontattare")
        st.caption("Non visitati da oltre 30 giorni")
        
        if clienti_non_visitati_30gg:
            clienti_non_visitati_30gg.sort(key=lambda x: x['giorni'], reverse=True)
            
            for item in clienti_non_visitati_30gg[:5]:
                cliente = item['cliente']
                giorni = item['giorni']
                
                if giorni == 999:
                    badge = "🆕 Mai visitato"
                elif giorni > 60:
                    badge = f"🔴 {giorni}gg"
                else:
                    badge = f"🟡 {giorni}gg"
                
                cat_badge = f"[{cliente.get('categoria', 'C')}]"
                st.markdown(f"{badge} **{cliente['nome_azienda']}** {cat_badge}")
                st.caption(f"{cliente.get('provincia', 'N/D')} • {cliente.get('telefono', '-')}")
        else:
            st.success("✨ Tutti i clienti visitati di recente!")
    
    with col2:
        st.markdown("### 🏆 Top Clienti del Mese")
        st.caption("Per valore ordini")
        
        # Calcola totale ordini per cliente
        ordini_per_cliente = {}
        for v in st.session_state.visite:
            if (datetime.fromisoformat(v['data_visita']).month == oggi.month 
                and v.get('ordine_effettuato')):
                cid = v['cliente_id']
                ordini_per_cliente[cid] = ordini_per_cliente.get(cid, 0) + (v.get('importo_ordine', 0) or 0)
        
        if ordini_per_cliente:
            top_clienti = sorted(ordini_per_cliente.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for i, (cliente_id, totale) in enumerate(top_clienti, 1):
                cliente = get_cliente_by_id(cliente_id)
                if cliente:
                    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1]
                    st.markdown(f"{medal} **{cliente['nome_azienda']}**")
                    st.caption(f"{format_currency(totale)}")
        else:
            st.info("Nessun ordine questo mese")
    
    st.markdown("---")
    
    # ==================== FOOTER INFO ====================
    st.markdown("### 📅 Prossimi Appuntamenti")
    
    prossime_visite = [v for v in st.session_state.visite_pianificate 
                      if datetime.fromisoformat(v['data_pianificata']).date() > oggi
                      and not v['completata']]
    prossime_visite.sort(key=lambda x: x['data_pianificata'])
    
    if prossime_visite:
        cols = st.columns(min(len(prossime_visite[:4]), 4))
        for i, v in enumerate(prossime_visite[:4]):
            with cols[i]:
                cliente = get_cliente_by_id(v['cliente_id'])
                if cliente:
                    data = datetime.fromisoformat(v['data_pianificata']).strftime("%a %d/%m")
                    st.markdown(f"📍 **{data}**")
                    st.markdown(f"{cliente['nome_azienda']}")
                    st.caption(cliente.get('provincia', ''))
    else:
        st.info("Nessuna visita pianificata. Vai al Calendario per pianificare!")
    
    # Motivational quote
    st.markdown("---")
    quotes = [
        "💪 *\"Il successo è la somma di piccoli sforzi ripetuti giorno dopo giorno.\"*",
        "🎯 *\"Non contare i giorni, fai che i giorni contino.\"*",
        "🚀 *\"Ogni cliente è un'opportunità di crescita.\"*",
        "⭐ *\"La qualità del servizio crea clienti fedeli.\"*",
        "🔥 *\"L'unico modo per fare un ottimo lavoro è amare quello che fai.\"*"
    ]
    import random
    st.markdown(random.choice(quotes))

# ==================== PAGINA CLIENTI ====================

def show_clienti():
    st.markdown("# 👥 Clienti")
    st.markdown("---")
    
    # Tabs per gestione
    tab1, tab2 = st.tabs(["📋 Lista Clienti", "➕ Nuovo Cliente"])
    
    with tab1:
        # Filtri
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_provincia = st.selectbox("Filtra per Provincia", 
                                           ["Tutte"] + get_province_italiane())
        with col2:
            filtro_categoria = st.selectbox("Filtra per Categoria", 
                                           ["Tutte", "A", "B", "C"])
        with col3:
            ricerca = st.text_input("🔍 Cerca", placeholder="Nome azienda...")
        
        # Applica filtri
        clienti_filtrati = st.session_state.clienti.copy()
        
        if filtro_provincia != "Tutte":
            clienti_filtrati = [c for c in clienti_filtrati if c.get('provincia') == filtro_provincia]
        
        if filtro_categoria != "Tutte":
            clienti_filtrati = [c for c in clienti_filtrati if c.get('categoria') == filtro_categoria]
        
        if ricerca:
            clienti_filtrati = [c for c in clienti_filtrati 
                               if ricerca.lower() in c['nome_azienda'].lower()]
        
        st.markdown(f"**{len(clienti_filtrati)} clienti trovati**")
        
        # Lista clienti
        for cliente in clienti_filtrati:
            with st.expander(f"🏢 {cliente['nome_azienda']} - {cliente.get('provincia', 'N/D')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Tipo:** {cliente.get('tipo', '-')}")
                    st.markdown(f"**Categoria:** {cliente.get('categoria', '-')}")
                    st.markdown(f"**Telefono:** {cliente.get('telefono', '-')}")
                    st.markdown(f"**Email:** {cliente.get('email', '-')}")
                
                with col2:
                    st.markdown(f"**Indirizzo:** {cliente.get('indirizzo', '-')}")
                    st.markdown(f"**Città:** {cliente.get('citta', '-')} ({cliente.get('cap', '')})")
                    st.markdown(f"**Referente:** {cliente.get('referente_nome', '-')} ({cliente.get('referente_ruolo', '')})")
                    st.markdown(f"**P.IVA:** {cliente.get('partita_iva', '-')}")
                
                if cliente.get('note'):
                    st.markdown(f"**Note:** {cliente['note']}")
                
                # Azioni
                col1, col2, col3 = st.columns(3)
                with col1:
                    if cliente.get('indirizzo') and cliente.get('citta'):
                        indirizzo_completo = f"{cliente['indirizzo']}, {cliente['citta']}"
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={indirizzo_completo.replace(' ', '+')}"
                        st.link_button("🗺️ Apri Maps", maps_url)
                
                with col2:
                    if st.button("✏️ Modifica", key=f"edit_{cliente['id']}"):
                        st.session_state.cliente_edit = cliente['id']
                        st.session_state.page = 'modifica_cliente'
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Elimina", key=f"del_{cliente['id']}"):
                        st.session_state.clienti = [c for c in st.session_state.clienti 
                                                   if c['id'] != cliente['id']]
                        st.success("Cliente eliminato")
                        st.rerun()
    
    with tab2:
        show_form_nuovo_cliente()

def show_form_nuovo_cliente():
    st.markdown("### ➕ Nuovo Cliente")
    
    with st.form("nuovo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_azienda = st.text_input("Nome Azienda *", placeholder="Es: Distribuzione Rossi")
            tipo = st.selectbox("Tipo", ["distributore", "grossista"])
            telefono = st.text_input("Telefono", placeholder="Es: 0123 456789")
            email = st.text_input("Email", placeholder="Es: info@azienda.it")
            partita_iva = st.text_input("Partita IVA", placeholder="Es: 01234567890")
        
        with col2:
            indirizzo = st.text_input("Indirizzo", placeholder="Es: Via Roma 123")
            citta = st.text_input("Città", placeholder="Es: Milano")
            provincia = st.selectbox("Provincia *", get_province_italiane())
            cap = st.text_input("CAP", placeholder="Es: 20100")
            categoria = st.selectbox("Categoria", ["A", "B", "C"], index=2)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            referente_nome = st.text_input("Nome Referente", placeholder="Es: Mario Rossi")
        with col2:
            referente_ruolo = st.text_input("Ruolo Referente", placeholder="Es: Responsabile Acquisti")
        
        note = st.text_area("Note", placeholder="Eventuali note sul cliente...")
        
        submitted = st.form_submit_button("💾 Salva Cliente", use_container_width=True, type="primary")
        
        if submitted:
            if not nome_azienda:
                st.error("Il nome azienda è obbligatorio")
            else:
                nuovo_cliente = {
                    'id': generate_id(),
                    'nome_azienda': nome_azienda,
                    'tipo': tipo,
                    'indirizzo': indirizzo,
                    'citta': citta,
                    'provincia': provincia,
                    'cap': cap,
                    'telefono': telefono,
                    'email': email,
                    'referente_nome': referente_nome,
                    'referente_ruolo': referente_ruolo,
                    'partita_iva': partita_iva,
                    'categoria': categoria,
                    'note': note,
                    'created_at': datetime.now().isoformat()
                }
                st.session_state.clienti.append(nuovo_cliente)
                st.success(f"✅ Cliente '{nome_azienda}' aggiunto con successo!")
                st.rerun()

# ==================== PAGINA CALENDARIO ====================

def show_calendario():
    st.markdown("# 📅 Calendario")
    st.markdown("---")
    
    # Selettore data
    col1, col2 = st.columns([2, 1])
    
    with col1:
        data_selezionata = st.date_input("Seleziona data", value=date.today())
    
    with col2:
        if st.button("➕ Pianifica Visita", type="primary"):
            st.session_state.show_pianifica = True
    
    # Form pianificazione visita
    if st.session_state.get('show_pianifica', False):
        with st.form("pianifica_visita"):
            st.markdown("### Pianifica Nuova Visita")
            
            cliente_options = {c['id']: c['nome_azienda'] for c in st.session_state.clienti}
            
            if not cliente_options:
                st.warning("Nessun cliente disponibile. Crea prima un cliente.")
            else:
                cliente_sel = st.selectbox("Cliente", options=list(cliente_options.keys()),
                                          format_func=lambda x: cliente_options[x])
                
                col1, col2 = st.columns(2)
                with col1:
                    data_visita = st.date_input("Data", value=data_selezionata)
                with col2:
                    ora_visita = st.time_input("Ora", value=None)
                
                note = st.text_area("Note", placeholder="Eventuali note...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salva", type="primary"):
                        nuova_visita = {
                            'id': generate_id(),
                            'cliente_id': cliente_sel,
                            'data_pianificata': data_visita.isoformat(),
                            'ora_inizio': ora_visita.isoformat() if ora_visita else None,
                            'note': note,
                            'completata': False,
                            'created_at': datetime.now().isoformat()
                        }
                        st.session_state.visite_pianificate.append(nuova_visita)
                        st.session_state.show_pianifica = False
                        st.success("Visita pianificata!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ Annulla"):
                        st.session_state.show_pianifica = False
                        st.rerun()
    
    st.markdown("---")
    
    # Vista settimanale
    st.markdown("### 📆 Questa Settimana")
    
    inizio_settimana = data_selezionata - timedelta(days=data_selezionata.weekday())
    
    for i in range(7):
        giorno = inizio_settimana + timedelta(days=i)
        visite_giorno = [v for v in st.session_state.visite_pianificate 
                        if datetime.fromisoformat(v['data_pianificata']).date() == giorno]
        
        giorno_nome = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"][i]
        
        with st.expander(f"**{giorno_nome} {giorno.strftime('%d/%m')}** - {len(visite_giorno)} visite", 
                        expanded=(giorno == date.today())):
            if visite_giorno:
                for v in visite_giorno:
                    cliente = get_cliente_by_id(v['cliente_id'])
                    if cliente:
                        status = "✅" if v['completata'] else "⏳"
                        ora = v.get('ora_inizio', '')
                        if ora:
                            ora = datetime.fromisoformat(f"2000-01-01T{ora}").strftime("%H:%M")
                        st.markdown(f"{status} **{ora or '--:--'}** - {cliente['nome_azienda']} ({cliente.get('provincia', '')})")
            else:
                st.markdown("*Nessuna visita pianificata*")

# ==================== PAGINA GIRO GIORNALIERO ====================

def show_giro():
    st.markdown("# 🚗 Giro Giornaliero")
    st.markdown("---")
    
    data_giro = st.date_input("Data", value=date.today())
    
    visite_giorno = [v for v in st.session_state.visite_pianificate 
                    if datetime.fromisoformat(v['data_pianificata']).date() == data_giro]
    
    # Ordina per ora
    visite_giorno.sort(key=lambda x: x.get('ora_inizio') or '23:59')
    
    if not visite_giorno:
        st.info("Nessuna visita pianificata per questa data. Vai al Calendario per pianificare visite.")
        return
    
    st.markdown(f"### {len(visite_giorno)} visite pianificate")
    
    # Lista visite
    for i, visita in enumerate(visite_giorno, 1):
        cliente = get_cliente_by_id(visita['cliente_id'])
        if not cliente:
            continue
        
        status_icon = "✅" if visita['completata'] else f"**{i}.**"
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                ora = visita.get('ora_inizio', '')
                if ora:
                    ora = datetime.fromisoformat(f"2000-01-01T{ora}").strftime("%H:%M")
                st.markdown(f"{status_icon} **{cliente['nome_azienda']}**")
                st.markdown(f"📍 {cliente.get('indirizzo', 'N/D')}, {cliente.get('citta', 'N/D')} ({cliente.get('provincia', '')})")
                if cliente.get('telefono'):
                    st.markdown(f"📞 {cliente['telefono']}")
            
            with col2:
                if cliente.get('indirizzo') and cliente.get('citta'):
                    indirizzo = f"{cliente['indirizzo']}, {cliente['citta']}"
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={indirizzo.replace(' ', '+')}"
                    st.link_button("🗺️ Maps", maps_url)
            
            with col3:
                if not visita['completata']:
                    if st.button("✅ Fatto", key=f"done_{visita['id']}"):
                        for v in st.session_state.visite_pianificate:
                            if v['id'] == visita['id']:
                                v['completata'] = True
                        st.rerun()
            
            st.markdown("---")
    
    # Link per ottimizzare percorso
    if len(visite_giorno) > 1:
        st.markdown("### 🗺️ Ottimizza Percorso")
        
        indirizzi = []
        for v in visite_giorno:
            cliente = get_cliente_by_id(v['cliente_id'])
            if cliente and cliente.get('indirizzo') and cliente.get('citta'):
                indirizzi.append(f"{cliente['indirizzo']}, {cliente['citta']}")
        
        if len(indirizzi) >= 2:
            # Crea URL Google Maps con waypoints
            origin = indirizzi[0].replace(' ', '+')
            destination = indirizzi[-1].replace(' ', '+')
            waypoints = '|'.join([i.replace(' ', '+') for i in indirizzi[1:-1]])
            
            if waypoints:
                maps_route = f"https://www.google.com/maps/dir/{origin}/{waypoints}/{destination}"
            else:
                maps_route = f"https://www.google.com/maps/dir/{origin}/{destination}"
            
            st.link_button("🚗 Apri Percorso in Google Maps", maps_route, type="primary")

# ==================== PAGINA REGISTRA VISITA ====================

def show_registra_visita():
    st.markdown("# ✅ Registra Visita")
    st.markdown("---")
    
    cliente_options = {c['id']: f"{c['nome_azienda']} ({c.get('provincia', '')})" 
                      for c in st.session_state.clienti}
    
    if not cliente_options:
        st.warning("Nessun cliente disponibile. Crea prima un cliente.")
        return
    
    with st.form("registra_visita"):
        cliente_sel = st.selectbox("Cliente *", options=list(cliente_options.keys()),
                                  format_func=lambda x: cliente_options[x])
        
        col1, col2 = st.columns(2)
        with col1:
            data_visita = st.date_input("Data Visita", value=date.today())
        with col2:
            ora_visita = st.time_input("Ora", value=datetime.now().time())
        
        esito = st.selectbox("Esito", ["positivo", "negativo", "da_ricontattare"])
        
        col1, col2 = st.columns(2)
        with col1:
            ordine = st.checkbox("Ordine Effettuato")
        with col2:
            importo = st.number_input("Importo Ordine (€)", min_value=0.0, step=10.0, 
                                     disabled=not ordine)
        
        note = st.text_area("Note", placeholder="Dettagli della visita...")
        prossima_azione = st.text_input("Prossima Azione", placeholder="Es: Inviare preventivo")
        
        if st.form_submit_button("💾 Salva Visita", type="primary", use_container_width=True):
            nuova_visita = {
                'id': generate_id(),
                'cliente_id': cliente_sel,
                'data_visita': datetime.combine(data_visita, ora_visita).isoformat(),
                'esito': esito,
                'ordine_effettuato': ordine,
                'importo_ordine': importo if ordine else None,
                'note': note,
                'prossima_azione': prossima_azione,
                'created_at': datetime.now().isoformat()
            }
            st.session_state.visite.append(nuova_visita)
            st.success("✅ Visita registrata con successo!")
            
            # Crea promemoria automatico se c'è prossima azione
            if prossima_azione:
                st.info("💡 Vuoi creare un promemoria per la prossima azione?")
    
    # Storico visite recenti
    st.markdown("---")
    st.markdown("### 📋 Ultime Visite")
    
    visite_recenti = sorted(st.session_state.visite, 
                           key=lambda x: x['data_visita'], reverse=True)[:10]
    
    for visita in visite_recenti:
        cliente = get_cliente_by_id(visita['cliente_id'])
        if cliente:
            data = datetime.fromisoformat(visita['data_visita']).strftime("%d/%m/%Y %H:%M")
            esito_icon = {"positivo": "✅", "negativo": "❌", "da_ricontattare": "🔄"}[visita['esito']]
            ordine_txt = format_currency(visita.get('importo_ordine')) if visita.get('ordine_effettuato') else ""
            
            st.markdown(f"{esito_icon} **{data}** - {cliente['nome_azienda']} {ordine_txt}")

# ==================== PAGINA PROMEMORIA ====================

def show_promemoria():
    st.markdown("# 🔔 Promemoria")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 Attivi", "✅ Completati", "➕ Nuovo"])
    
    with tab1:
        promemoria_attivi = [p for p in st.session_state.promemoria if not p['completato']]
        promemoria_attivi.sort(key=lambda x: x['data_scadenza'])
        
        if not promemoria_attivi:
            st.success("🎉 Nessun promemoria attivo!")
        else:
            oggi = date.today()
            
            for p in promemoria_attivi:
                data_scad = datetime.fromisoformat(p['data_scadenza']).date()
                
                # Colore in base alla scadenza
                if data_scad < oggi:
                    status = "🔴 SCADUTO"
                elif data_scad == oggi:
                    status = "🟠 OGGI"
                elif data_scad <= oggi + timedelta(days=3):
                    status = "🟡 Prossimo"
                else:
                    status = "🟢"
                
                with st.expander(f"{status} {p['titolo']} - {data_scad.strftime('%d/%m/%Y')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Tipo:** {p.get('tipo', '-')}")
                        st.markdown(f"**Priorità:** {p['priorita']}")
                        
                        cliente = get_cliente_by_id(p.get('cliente_id'))
                        if cliente:
                            st.markdown(f"**Cliente:** {cliente['nome_azienda']}")
                    
                    with col2:
                        if p.get('descrizione'):
                            st.markdown(f"**Note:** {p['descrizione']}")
                    
                    if st.button("✅ Completa", key=f"complete_{p['id']}"):
                        for prom in st.session_state.promemoria:
                            if prom['id'] == p['id']:
                                prom['completato'] = True
                                prom['completato_at'] = datetime.now().isoformat()
                        st.rerun()
    
    with tab2:
        promemoria_completati = [p for p in st.session_state.promemoria if p['completato']]
        promemoria_completati.sort(key=lambda x: x.get('completato_at', ''), reverse=True)
        
        if not promemoria_completati:
            st.info("Nessun promemoria completato")
        else:
            for p in promemoria_completati[:20]:
                data_comp = datetime.fromisoformat(p['completato_at']).strftime("%d/%m/%Y") if p.get('completato_at') else '-'
                st.markdown(f"✅ ~~{p['titolo']}~~ - completato il {data_comp}")
    
    with tab3:
        with st.form("nuovo_promemoria"):
            st.markdown("### ➕ Nuovo Promemoria")
            
            titolo = st.text_input("Titolo *", placeholder="Es: Chiamare cliente Rossi")
            
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["chiamata", "preventivo", "sollecito", "ricontatto", "altro"])
                data_scadenza = st.date_input("Scadenza", value=date.today() + timedelta(days=1))
            
            with col2:
                priorita = st.selectbox("Priorità", ["alta", "media", "bassa"], index=1)
                ora_scadenza = st.time_input("Ora", value=None)
            
            # Cliente opzionale
            cliente_options = {"": "Nessun cliente"} | {c['id']: c['nome_azienda'] 
                                                        for c in st.session_state.clienti}
            cliente_sel = st.selectbox("Cliente (opzionale)", options=list(cliente_options.keys()),
                                      format_func=lambda x: cliente_options[x])
            
            descrizione = st.text_area("Descrizione", placeholder="Dettagli...")
            
            if st.form_submit_button("💾 Salva Promemoria", type="primary", use_container_width=True):
                if not titolo:
                    st.error("Il titolo è obbligatorio")
                else:
                    if ora_scadenza:
                        data_scad_completa = datetime.combine(data_scadenza, ora_scadenza)
                    else:
                        data_scad_completa = datetime.combine(data_scadenza, datetime.min.time())
                    
                    nuovo_promemoria = {
                        'id': generate_id(),
                        'titolo': titolo,
                        'descrizione': descrizione,
                        'cliente_id': cliente_sel if cliente_sel else None,
                        'tipo': tipo,
                        'data_scadenza': data_scad_completa.isoformat(),
                        'priorita': priorita,
                        'completato': False,
                        'created_at': datetime.now().isoformat()
                    }
                    st.session_state.promemoria.append(nuovo_promemoria)
                    st.success("✅ Promemoria creato!")
                    st.rerun()

# ==================== PAGINA REPORT ====================

def show_report():
    st.markdown("# 📈 Report")
    st.markdown("---")
    
    # Selettore periodo
    col1, col2 = st.columns(2)
    with col1:
        data_inizio = st.date_input("Da", value=date.today().replace(day=1))
    with col2:
        data_fine = st.date_input("A", value=date.today())
    
    st.markdown("---")
    
    # Filtra visite nel periodo
    visite_periodo = [v for v in st.session_state.visite 
                     if data_inizio <= datetime.fromisoformat(v['data_visita']).date() <= data_fine]
    
    # Metriche
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Visite Totali", len(visite_periodo))
    
    with col2:
        visite_positive = len([v for v in visite_periodo if v['esito'] == 'positivo'])
        perc = (visite_positive / len(visite_periodo) * 100) if visite_periodo else 0
        st.metric("Visite Positive", f"{visite_positive} ({perc:.0f}%)")
    
    with col3:
        ordini = len([v for v in visite_periodo if v.get('ordine_effettuato')])
        st.metric("Ordini", ordini)
    
    with col4:
        totale = sum([v.get('importo_ordine', 0) or 0 for v in visite_periodo if v.get('ordine_effettuato')])
        st.metric("Totale Ordini", format_currency(totale))
    
    st.markdown("---")
    
    # Grafici
    if visite_periodo:
        import plotly.express as px
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Esiti Visite")
            esiti = {"positivo": 0, "negativo": 0, "da_ricontattare": 0}
            for v in visite_periodo:
                esiti[v['esito']] += 1
            
            fig = px.pie(values=list(esiti.values()), names=list(esiti.keys()),
                        color_discrete_sequence=['#00cc00', '#ff4b4b', '#ffa500'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Visite per Giorno")
            visite_per_giorno = {}
            for v in visite_periodo:
                giorno = datetime.fromisoformat(v['data_visita']).strftime("%d/%m")
                visite_per_giorno[giorno] = visite_per_giorno.get(giorno, 0) + 1
            
            if visite_per_giorno:
                df = pd.DataFrame(list(visite_per_giorno.items()), columns=['Giorno', 'Visite'])
                fig = px.bar(df, x='Giorno', y='Visite')
                st.plotly_chart(fig, use_container_width=True)
    
    # Clienti più visitati
    st.markdown("### 🏆 Clienti Più Visitati")
    
    visite_per_cliente = {}
    for v in visite_periodo:
        cliente_id = v['cliente_id']
        visite_per_cliente[cliente_id] = visite_per_cliente.get(cliente_id, 0) + 1
    
    top_clienti = sorted(visite_per_cliente.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for cliente_id, num_visite in top_clienti:
        cliente = get_cliente_by_id(cliente_id)
        if cliente:
            st.markdown(f"- **{cliente['nome_azienda']}**: {num_visite} visite")

# ==================== MAIN ====================

def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        show_sidebar()
        
        page = st.session_state.page
        
        if page == 'dashboard':
            show_dashboard()
        elif page == 'clienti':
            show_clienti()
        elif page == 'calendario':
            show_calendario()
        elif page == 'giro':
            show_giro()
        elif page == 'visite':
            show_registra_visita()
        elif page == 'promemoria':
            show_promemoria()
        elif page == 'report':
            show_report()

if __name__ == "__main__":
    main()
