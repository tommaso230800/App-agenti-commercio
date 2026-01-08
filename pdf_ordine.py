"""
PORTALE AGENTE DI COMMERCIO
Generatore PDF Ordine Professionale
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional
import os


# Colori aziendali
COLORE_PRIMARY = colors.HexColor('#1e3a5f')  # Blu scuro
COLORE_SECONDARY = colors.HexColor('#3b82f6')  # Blu
COLORE_GRIGIO = colors.HexColor('#6b7280')
COLORE_GRIGIO_CHIARO = colors.HexColor('#f3f4f6')
COLORE_BORDER = colors.HexColor('#d1d5db')


def genera_pdf_ordine(ordine: Dict, agente: Dict = None) -> bytes:
    """
    Genera un PDF professionale per l'ordine.
    
    Args:
        ordine: Dizionario con tutti i dati dell'ordine (testata + righe)
        agente: Dizionario con i dati dell'agente (opzionale)
    
    Returns:
        bytes: Contenuto del PDF
    """
    buffer = BytesIO()
    
    # Crea il documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    
    # Stili
    styles = getSampleStyleSheet()
    
    # Stili personalizzati
    style_titolo = ParagraphStyle(
        'Titolo',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=COLORE_PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    style_sottotitolo = ParagraphStyle(
        'Sottotitolo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLORE_GRIGIO,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    style_sezione = ParagraphStyle(
        'Sezione',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=COLORE_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        borderPadding=3,
        leftIndent=0
    )
    
    style_label = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORE_GRIGIO
    )
    
    style_valore = ParagraphStyle(
        'Valore',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black
    )
    
    style_valore_bold = ParagraphStyle(
        'ValoreBold',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    style_piccolo = ParagraphStyle(
        'Piccolo',
        parent=styles['Normal'],
        fontSize=7,
        textColor=COLORE_GRIGIO,
        alignment=TA_CENTER
    )
    
    # Elementi del documento
    elements = []
    
    # ==================== HEADER ====================
    
    # Logo e info documento
    header_data = [
        [
            # Colonna sinistra: Logo/Nome azienda
            Paragraph(f"<b>{ordine.get('azienda_nome', 'AZIENDA')}</b>", 
                     ParagraphStyle('AziendaNome', fontSize=14, textColor=COLORE_PRIMARY)),
            # Colonna destra: Info documento
            Paragraph(f"<b>ORDINE N. {ordine.get('numero', '')}</b>", 
                     ParagraphStyle('NumOrdine', fontSize=14, textColor=COLORE_PRIMARY, alignment=TA_RIGHT))
        ],
        [
            Paragraph(ordine.get('azienda_ragione_sociale', '') or '', style_valore),
            Paragraph(f"Data: {format_data(ordine.get('data_ordine'))}", 
                     ParagraphStyle('Data', fontSize=10, alignment=TA_RIGHT))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[100*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5*mm))
    
    # Linea separatrice
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORE_PRIMARY, spaceAfter=5*mm))
    
    # ==================== DATI AZIENDA E CLIENTE ====================
    
    # Box Fornitore e Cliente
    box_data = [
        [
            Paragraph("<b>FORNITORE</b>", style_sezione),
            Paragraph("<b>CLIENTE</b>", style_sezione)
        ],
        [
            # Dati fornitore
            Paragraph(f"""
                <b>{ordine.get('azienda_ragione_sociale', ordine.get('azienda_nome', ''))}</b><br/>
                {ordine.get('azienda_indirizzo', '')}<br/>
                {ordine.get('azienda_cap', '')} {ordine.get('azienda_citta', '')} ({ordine.get('azienda_provincia', '')})<br/>
                Tel: {ordine.get('azienda_telefono', '')}<br/>
                Email: {ordine.get('azienda_email', '')}<br/>
                P.IVA: {ordine.get('azienda_piva', '')}
            """, style_valore),
            # Dati cliente
            Paragraph(f"""
                <b>{ordine.get('cliente_ragione_sociale', '')}</b><br/>
                {ordine.get('cliente_indirizzo', '')}<br/>
                {ordine.get('cliente_cap', '')} {ordine.get('cliente_citta', '')} ({ordine.get('cliente_provincia', '')})<br/>
                Tel: {ordine.get('cliente_telefono', '')}<br/>
                Email: {ordine.get('cliente_email', '')}<br/>
                P.IVA: {ordine.get('cliente_piva', '')} - C.F.: {ordine.get('cliente_cf', '')}
            """, style_valore)
        ]
    ]
    
    box_table = Table(box_data, colWidths=[90*mm, 90*mm])
    box_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (0, 1), 0.5, COLORE_BORDER),
        ('BOX', (1, 0), (1, 1), 0.5, COLORE_BORDER),
        ('BACKGROUND', (0, 0), (0, 0), COLORE_GRIGIO_CHIARO),
        ('BACKGROUND', (1, 0), (1, 0), COLORE_GRIGIO_CHIARO),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(box_table)
    elements.append(Spacer(1, 5*mm))
    
    # ==================== SEDE DI CONSEGNA (se diversa) ====================
    
    if ordine.get('consegna_indirizzo') and ordine.get('consegna_indirizzo') != ordine.get('cliente_indirizzo'):
        elements.append(Paragraph("<b>SEDE DI CONSEGNA</b>", style_sezione))
        consegna_text = f"""
            {ordine.get('consegna_indirizzo', '')}<br/>
            {ordine.get('consegna_cap', '')} {ordine.get('consegna_citta', '')} ({ordine.get('consegna_provincia', '')})<br/>
            {ordine.get('consegna_note', '')}
        """
        elements.append(Paragraph(consegna_text, style_valore))
        elements.append(Spacer(1, 3*mm))
    
    # ==================== TABELLA ARTICOLI ====================
    
    elements.append(Paragraph("<b>DETTAGLIO ARTICOLI</b>", style_sezione))
    
    # Header tabella
    articoli_header = [
        Paragraph("<b>ARTICOLO</b>", style_label),
        Paragraph("<b>DESCRIZIONE</b>", style_label),
        Paragraph("<b>U.M.</b>", style_label),
        Paragraph("<b>Q.TÀ</b>", style_label),
        Paragraph("<b>PR. UN.</b>", style_label),
        Paragraph("<b>SC.%</b>", style_label),
        Paragraph("<b>IMPORTO</b>", style_label),
    ]
    
    articoli_data = [articoli_header]
    
    # Righe articoli
    righe = ordine.get('righe', [])
    for riga in righe:
        # Formatta quantità
        qta_cartoni = riga.get('quantita_cartoni', 0) or 0
        qta_pezzi = riga.get('quantita_pezzi', 0) or 0
        qta_totale = riga.get('quantita_totale', 0) or 0
        
        if qta_cartoni > 0 and qta_pezzi > 0:
            qta_str = f"{qta_cartoni} ct + {qta_pezzi} pz"
        elif qta_cartoni > 0:
            qta_str = f"{qta_cartoni} ct"
        else:
            qta_str = f"{qta_totale} pz"
        
        row = [
            Paragraph(str(riga.get('prodotto_codice', '')), style_valore),
            Paragraph(str(riga.get('prodotto_nome', '')), style_valore),
            Paragraph(str(riga.get('unita_misura', 'PZ')), style_valore),
            Paragraph(qta_str, style_valore),
            Paragraph(format_euro(riga.get('prezzo_unitario', 0)), style_valore),
            Paragraph(f"{riga.get('sconto_riga', 0):.1f}%" if riga.get('sconto_riga') else "", style_valore),
            Paragraph(format_euro(riga.get('importo_riga', 0)), style_valore_bold),
        ]
        articoli_data.append(row)
    
    # Crea tabella
    col_widths = [25*mm, 55*mm, 12*mm, 22*mm, 20*mm, 15*mm, 25*mm]
    articoli_table = Table(articoli_data, colWidths=col_widths, repeatRows=1)
    
    articoli_style = TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), COLORE_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        
        # Righe
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # U.M.
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Q.TÀ
        ('ALIGN', (4, 1), (5, -1), 'RIGHT'),   # Prezzo, Sconto
        ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Importo
        
        # Bordi
        ('BOX', (0, 0), (-1, -1), 0.5, COLORE_BORDER),
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLORE_PRIMARY),
        ('LINEBELOW', (0, 1), (-1, -2), 0.25, COLORE_BORDER),
        
        # Righe alternate
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORE_GRIGIO_CHIARO]),
    ])
    
    articoli_table.setStyle(articoli_style)
    elements.append(articoli_table)
    elements.append(Spacer(1, 5*mm))
    
    # ==================== TOTALI ====================
    
    totale_pezzi = ordine.get('totale_pezzi', 0) or 0
    totale_cartoni = ordine.get('totale_cartoni', 0) or 0
    imponibile = ordine.get('imponibile', 0) or 0
    sconto_chiusura = ordine.get('sconto_chiusura', 0) or 0
    totale_finale = ordine.get('totale_finale', 0) or 0
    
    # Calcola sconto in euro se percentuale
    if sconto_chiusura > 0:
        sconto_euro = imponibile * (sconto_chiusura / 100)
    else:
        sconto_euro = 0
    
    totali_data = [
        ['', '', 'TOTALE PEZZI:', f"{totale_pezzi}"],
        ['', '', 'TOTALE CARTONI:', f"{totale_cartoni:.1f}"],
        ['', '', 'IMPONIBILE:', format_euro(imponibile)],
    ]
    
    if sconto_chiusura > 0:
        totali_data.append(['', '', f'SCONTO CHIUSURA ({sconto_chiusura:.1f}%):', f"- {format_euro(sconto_euro)}"])
    
    totali_data.append(['', '', 'TOTALE ORDINE:', format_euro(totale_finale)])
    
    totali_table = Table(totali_data, colWidths=[60*mm, 50*mm, 40*mm, 30*mm])
    totali_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTSIZE', (2, -1), (3, -1), 11),
        ('TEXTCOLOR', (2, -1), (3, -1), COLORE_PRIMARY),
        ('LINEABOVE', (2, -1), (3, -1), 1, COLORE_PRIMARY),
        ('TOPPADDING', (2, -1), (3, -1), 5),
    ]))
    elements.append(totali_table)
    elements.append(Spacer(1, 8*mm))
    
    # ==================== CONDIZIONI DI VENDITA ====================
    
    elements.append(HRFlowable(width="100%", thickness=0.5, color=COLORE_BORDER, spaceBefore=3*mm, spaceAfter=3*mm))
    
    elements.append(Paragraph("<b>CONDIZIONI DI VENDITA</b>", style_sezione))
    
    condizioni_data = [
        [
            Paragraph(f"<b>Pagamento:</b> {ordine.get('pagamento', '-')}", style_valore),
            Paragraph(f"<b>Consegna:</b> {ordine.get('consegna_tipo', '-')}", style_valore),
        ],
        [
            Paragraph(f"<b>Resa:</b> {ordine.get('resa', '-')}", style_valore),
            Paragraph(f"<b>Spedizione:</b> {ordine.get('spedizione', '-')}", style_valore),
        ],
        [
            Paragraph(f"<b>Banca:</b> {ordine.get('banca', '-')}", style_valore),
            Paragraph("", style_valore),
        ],
    ]
    
    condizioni_table = Table(condizioni_data, colWidths=[90*mm, 90*mm])
    condizioni_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(condizioni_table)
    
    # ==================== NOTE ====================
    
    if ordine.get('note'):
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("<b>NOTE:</b>", style_sezione))
        elements.append(Paragraph(ordine.get('note', ''), style_valore))
    
    elements.append(Spacer(1, 10*mm))
    
    # ==================== FIRME ====================
    
    elements.append(HRFlowable(width="100%", thickness=0.5, color=COLORE_BORDER, spaceBefore=3*mm, spaceAfter=5*mm))
    
    firme_data = [
        [
            Paragraph("<b>FIRMA CLIENTE</b>", ParagraphStyle('FirmaLabel', fontSize=8, textColor=COLORE_GRIGIO, alignment=TA_CENTER)),
            Paragraph("<b>FIRMA AGENTE</b>", ParagraphStyle('FirmaLabel', fontSize=8, textColor=COLORE_GRIGIO, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<br/><br/><br/>_______________________________", ParagraphStyle('FirmaLinea', fontSize=9, alignment=TA_CENTER)),
            Paragraph("<br/><br/><br/>_______________________________", ParagraphStyle('FirmaLinea', fontSize=9, alignment=TA_CENTER)),
        ],
    ]
    
    firme_table = Table(firme_data, colWidths=[90*mm, 90*mm])
    firme_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(firme_table)
    
    # ==================== FOOTER ====================
    
    elements.append(Spacer(1, 10*mm))
    
    if agente:
        agente_info = f"Agente: {agente.get('nome', '')} {agente.get('cognome', '')} - Tel: {agente.get('cellulare', agente.get('telefono', ''))} - Email: {agente.get('email', '')}"
        elements.append(Paragraph(agente_info, style_piccolo))
    
    footer_text = f"Documento generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} - Portale Agente"
    elements.append(Paragraph(footer_text, style_piccolo))
    
    # Genera PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def format_euro(value) -> str:
    """Formatta un valore come euro"""
    try:
        value = float(value) if value else 0
        return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "€ 0,00"


def format_data(data_str) -> str:
    """Formatta una data"""
    if not data_str:
        return "-"
    try:
        if isinstance(data_str, str):
            if 'T' in data_str:
                data = datetime.fromisoformat(data_str.split('T')[0])
            else:
                data = datetime.strptime(data_str, '%Y-%m-%d')
        else:
            data = data_str
        return data.strftime('%d/%m/%Y')
    except:
        return str(data_str)


# ============================================
# FUNZIONE PER GENERARE PDF DA STREAMLIT
# ============================================

def genera_pdf_ordine_download(ordine_id: str) -> tuple:
    """
    Genera il PDF di un ordine pronto per il download.
    
    Returns:
        tuple: (bytes del PDF, nome file)
    """
    # Import db qui per evitare import circolari
    import db
    
    # Carica ordine completo
    ordine = db.get_ordine(ordine_id)
    if not ordine:
        return None, None
    
    # Carica dati agente
    agente = db.get_agente()
    
    # Genera PDF
    pdf_bytes = genera_pdf_ordine(ordine, agente)
    
    # Nome file
    numero_ordine = ordine.get('numero', 'ordine').replace('/', '-')
    cliente = ordine.get('cliente_ragione_sociale', 'cliente').replace(' ', '_')[:20]
    filename = f"Ordine_{numero_ordine}_{cliente}.pdf"
    
    return pdf_bytes, filename
