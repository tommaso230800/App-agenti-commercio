from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader


def _fmt_eur(x: float) -> str:
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def genera_proforma_pdf(
    *,
    file_path: str,
    logo_path: Optional[str],
    proforma_numero: str,
    data_proforma: str,
    azienda: Dict[str, Any],
    cliente: Dict[str, Any],
    righe: List[Dict[str, Any]],
    imponibile: float,
    agenzia_nome: str = "AMG Ho.Re.Ca Business & Strategy",
) -> None:
    """
    Genera un PDF PROFORMA (solo imponibile, no IVA).
    """
    out = Path(file_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    width, height = A4

    margin_x = 18 * mm
    y = height - 18 * mm

    # Logo
    if logo_path:
        lp = Path(logo_path)
        if lp.exists():
            try:
                img = ImageReader(str(lp))
                iw, ih = img.getSize()
                target_h = 18 * mm
                scale = target_h / ih
                target_w = iw * scale
                c.drawImage(img, margin_x, y - target_h, width=target_w, height=target_h, mask='auto')
            except Exception:
                pass

    # Titolo
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(width - margin_x, y, "PROFORMA")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    c.drawRightString(width - margin_x, y, f"N° {proforma_numero}")
    y -= 5 * mm
    c.drawRightString(width - margin_x, y, f"Data: {data_proforma}")
    y -= 10 * mm

    # Box azienda + cliente
    box_top = y
    box_h = 38 * mm
    box_w = (width - 2 * margin_x - 8 * mm) / 2

    # Azienda (fornitore)
    ax = margin_x
    ay = box_top
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.8)
    c.rect(ax, ay - box_h, box_w, box_h, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(ax + 4*mm, ay - 6*mm, "Azienda (Fornitore)")
    c.setFont("Helvetica", 9)

    az_lines = [
        (azienda.get("ragione_sociale") or azienda.get("nome") or "").strip(),
        (azienda.get("indirizzo") or "").strip(),
        " ".join([x for x in [(azienda.get("cap") or "").strip(), (azienda.get("citta") or "").strip(), (azienda.get("provincia") or "").strip()] if x]),
        ("P.IVA: " + (azienda.get("partita_iva") or "").strip()) if (azienda.get("partita_iva") or "").strip() else "",
        ("Email: " + (azienda.get("email") or "").strip()) if (azienda.get("email") or "").strip() else "",
        ("Tel: " + (azienda.get("telefono") or "").strip()) if (azienda.get("telefono") or "").strip() else "",
    ]
    az_lines = [l for l in az_lines if l]
    ly = ay - 12*mm
    for l in az_lines[:6]:
        c.drawString(ax + 4*mm, ly, l)
        ly -= 4.2*mm

    # Cliente (acquirente)
    cx = margin_x + box_w + 8 * mm
    cy = box_top
    c.rect(cx, cy - box_h, box_w, box_h, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(cx + 4*mm, cy - 6*mm, "Cliente (Acquirente)")
    c.setFont("Helvetica", 9)

    cl_lines = [
        (cliente.get("nome_azienda") or "").strip(),
        (cliente.get("indirizzo") or "").strip(),
        " ".join([x for x in [(cliente.get("cap") or "").strip(), (cliente.get("citta") or "").strip(), (cliente.get("provincia") or "").strip()] if x]),
        ("P.IVA: " + (cliente.get("partita_iva") or "").strip()) if (cliente.get("partita_iva") or "").strip() else "",
        ("Referente: " + (cliente.get("referente_nome") or "").strip()) if (cliente.get("referente_nome") or "").strip() else "",
        ("Tel: " + (cliente.get("telefono") or "").strip()) if (cliente.get("telefono") or "").strip() else "",
    ]
    cl_lines = [l for l in cl_lines if l]
    ly = cy - 12*mm
    for l in cl_lines[:6]:
        c.drawString(cx + 4*mm, ly, l)
        ly -= 4.2*mm

    y = box_top - box_h - 10 * mm

    # Tabella righe ordine
    table_data = [["Codice", "Prodotto", "Cartoni", "Bottiglie", "Pezzi", "Prezzo", "Totale"]]
    for r in righe:
        table_data.append([
            r.get("codice_prodotto") or "",
            r.get("nome_prodotto") or "",
            str(r.get("cartoni") or 0),
            str(r.get("bottiglie") or 0),
            str(r.get("pezzi_totali") or 0),
            _fmt_eur(float(r.get("prezzo_unitario") or 0)),
            _fmt_eur(float(r.get("totale_riga") or 0)),
        ])

    col_widths = [20*mm, 62*mm, 16*mm, 18*mm, 14*mm, 24*mm, 24*mm]
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 9),
        ("FONT", (0,1), (-1,-1), "Helvetica", 9),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F2F2F2")),
        ("GRID", (0,0), (-1,-1), 0.4, colors.black),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FBFBFB")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    tw, th = tbl.wrapOn(c, width - 2*margin_x, height)
    tbl.drawOn(c, margin_x, y - th)

    y = y - th - 10*mm

    # Totale imponibile
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - margin_x, y, f"TOTALE IMPONIBILE: {_fmt_eur(float(imponibile))}")

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(margin_x, 12*mm, "Documento non valido ai fini fiscali. Solo imponibile (IVA esclusa).")
    c.setFillColor(colors.black)

    c.save()
