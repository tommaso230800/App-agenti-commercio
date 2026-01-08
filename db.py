from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional, Tuple


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT_DIR / "data" / "app.db"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def uid() -> str:
    return str(uuid.uuid4())


def get_conn(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = Path(db_path or os.getenv("DB_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema_path = ROOT_DIR / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


# --------------------- Aziende ---------------------

def list_aziende(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM aziende ORDER BY nome ASC;")
    return [dict(r) for r in cur.fetchall()]


def get_azienda(conn: sqlite3.Connection, azienda_id: str) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM aziende WHERE id=?;", (azienda_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def upsert_azienda(conn: sqlite3.Connection, data: Dict[str, Any]) -> str:
    azienda_id = data.get("id") or uid()
    payload = {
        "id": azienda_id,
        "nome": data.get("nome", "").strip(),
        "ragione_sociale": data.get("ragione_sociale", "").strip(),
        "indirizzo": data.get("indirizzo", "").strip(),
        "citta": data.get("citta", "").strip(),
        "provincia": data.get("provincia", "").strip(),
        "cap": data.get("cap", "").strip(),
        "partita_iva": data.get("partita_iva", "").strip(),
        "email": data.get("email", "").strip(),
        "telefono": data.get("telefono", "").strip(),
        "created_at": data.get("created_at") or now_iso(),
    }
    conn.execute("""
        INSERT INTO aziende (id, nome, ragione_sociale, indirizzo, citta, provincia, cap, partita_iva, email, telefono, created_at)
        VALUES (:id,:nome,:ragione_sociale,:indirizzo,:citta,:provincia,:cap,:partita_iva,:email,:telefono,:created_at)
        ON CONFLICT(id) DO UPDATE SET
            nome=excluded.nome,
            ragione_sociale=excluded.ragione_sociale,
            indirizzo=excluded.indirizzo,
            citta=excluded.citta,
            provincia=excluded.provincia,
            cap=excluded.cap,
            partita_iva=excluded.partita_iva,
            email=excluded.email,
            telefono=excluded.telefono;
    """, payload)
    conn.commit()
    return azienda_id


def delete_azienda(conn: sqlite3.Connection, azienda_id: str) -> None:
    conn.execute("DELETE FROM aziende WHERE id=?;", (azienda_id,))
    conn.commit()


# --------------------- Clienti ---------------------

def list_clienti(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM clienti ORDER BY nome_azienda ASC;")
    return [dict(r) for r in cur.fetchall()]


def get_cliente(conn: sqlite3.Connection, cliente_id: str) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM clienti WHERE id=?;", (cliente_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def upsert_cliente(conn: sqlite3.Connection, data: Dict[str, Any]) -> str:
    cliente_id = data.get("id") or uid()
    payload = {
        "id": cliente_id,
        "nome_azienda": data.get("nome_azienda", "").strip(),
        "tipo": data.get("tipo", "distributore"),
        "indirizzo": data.get("indirizzo", "").strip(),
        "citta": data.get("citta", "").strip(),
        "provincia": data.get("provincia", "").strip(),
        "cap": data.get("cap", "").strip(),
        "telefono": data.get("telefono", "").strip(),
        "email": data.get("email", "").strip(),
        "referente_nome": data.get("referente_nome", "").strip(),
        "referente_ruolo": data.get("referente_ruolo", "").strip(),
        "partita_iva": data.get("partita_iva", "").strip(),
        "categoria": data.get("categoria", "C"),
        "note": data.get("note", "").strip(),
        "created_at": data.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }
    conn.execute("""
        INSERT INTO clienti (id,nome_azienda,tipo,indirizzo,citta,provincia,cap,telefono,email,referente_nome,referente_ruolo,partita_iva,categoria,note,created_at,updated_at)
        VALUES (:id,:nome_azienda,:tipo,:indirizzo,:citta,:provincia,:cap,:telefono,:email,:referente_nome,:referente_ruolo,:partita_iva,:categoria,:note,:created_at,:updated_at)
        ON CONFLICT(id) DO UPDATE SET
            nome_azienda=excluded.nome_azienda,
            tipo=excluded.tipo,
            indirizzo=excluded.indirizzo,
            citta=excluded.citta,
            provincia=excluded.provincia,
            cap=excluded.cap,
            telefono=excluded.telefono,
            email=excluded.email,
            referente_nome=excluded.referente_nome,
            referente_ruolo=excluded.referente_ruolo,
            partita_iva=excluded.partita_iva,
            categoria=excluded.categoria,
            note=excluded.note,
            updated_at=excluded.updated_at;
    """, payload)
    conn.commit()
    return cliente_id


def delete_cliente(conn: sqlite3.Connection, cliente_id: str) -> None:
    conn.execute("DELETE FROM clienti WHERE id=?;", (cliente_id,))
    conn.commit()


# --------------------- Prodotti ---------------------

def list_prodotti(conn: sqlite3.Connection, azienda_id: Optional[str] = None, only_active: bool = True) -> List[Dict[str, Any]]:
    q = "SELECT * FROM prodotti"
    params: List[Any] = []
    conds = []
    if azienda_id:
        conds.append("azienda_id=?")
        params.append(azienda_id)
    if only_active:
        conds.append("attivo=1")
    if conds:
        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY nome ASC;"
    cur = conn.execute(q, params)
    return [dict(r) for r in cur.fetchall()]


def upsert_prodotto(conn: sqlite3.Connection, data: Dict[str, Any]) -> str:
    prodotto_id = data.get("id") or uid()
    payload = {
        "id": prodotto_id,
        "azienda_id": data["azienda_id"],
        "codice": data.get("codice", "").strip(),
        "nome": data.get("nome", "").strip(),
        "prezzo_unitario": float(data.get("prezzo_unitario") or 0),
        "pezzi_per_cartone": int(data.get("pezzi_per_cartone") or 1),
        "unita_minima": data.get("unita_minima", "cartone/bottiglia"),
        "attivo": 1 if data.get("attivo", True) else 0,
        "created_at": data.get("created_at") or now_iso(),
    }
    conn.execute("""
        INSERT INTO prodotti (id,azienda_id,codice,nome,prezzo_unitario,pezzi_per_cartone,unita_minima,attivo,created_at)
        VALUES (:id,:azienda_id,:codice,:nome,:prezzo_unitario,:pezzi_per_cartone,:unita_minima,:attivo,:created_at)
        ON CONFLICT(id) DO UPDATE SET
            azienda_id=excluded.azienda_id,
            codice=excluded.codice,
            nome=excluded.nome,
            prezzo_unitario=excluded.prezzo_unitario,
            pezzi_per_cartone=excluded.pezzi_per_cartone,
            unita_minima=excluded.unita_minima,
            attivo=excluded.attivo;
    """, payload)
    conn.commit()
    return prodotto_id


def delete_prodotto(conn: sqlite3.Connection, prodotto_id: str) -> None:
    conn.execute("DELETE FROM prodotti WHERE id=?;", (prodotto_id,))
    conn.commit()


def list_prodotti_gia_acquistati(conn: sqlite3.Connection, azienda_id: str, cliente_id: str) -> List[str]:
    """
    Ritorna la lista di prodotto_id già acquistati in passato dal cliente per quella azienda.
    """
    cur = conn.execute("""
        SELECT DISTINCT r.prodotto_id
        FROM ordini o
        JOIN ordine_righe r ON r.ordine_id=o.id
        WHERE o.azienda_id=? AND o.cliente_id=? AND o.stato IN ('confermato','aperto');
    """, (azienda_id, cliente_id))
    return [row["prodotto_id"] for row in cur.fetchall()]


# --------------------- Ordini + Proforma ---------------------

def _next_progressivo(conn: sqlite3.Connection, prefix: str, year: int) -> int:
    like = f"{prefix}-{year}-%"
    cur = conn.execute("SELECT numero FROM ordini WHERE numero LIKE ? ORDER BY numero DESC LIMIT 1;", (like,))
    row = cur.fetchone()
    if not row:
        return 1
    m = row["numero"].split("-")
    try:
        return int(m[-1]) + 1
    except Exception:
        return 1


def create_ordine(conn: sqlite3.Connection, azienda_id: str, cliente_id: str, righe: List[Dict[str, Any]], note: str = "") -> Dict[str, Any]:
    azienda = get_azienda(conn, azienda_id)
    if not azienda:
        raise ValueError("Azienda non trovata")
    cliente = get_cliente(conn, cliente_id)
    if not cliente:
        raise ValueError("Cliente non trovato")

    year = datetime.now().year
    prefix = (azienda.get("nome") or "AZ").strip().upper()
    prefix = "".join([c for c in prefix if c.isalnum()])[:3] or "AZ"
    prog = _next_progressivo(conn, prefix, year)
    numero = f"{prefix}-{year}-{prog:04d}"

    ordine_id = uid()
    data_ordine = now_iso()
    created_at = now_iso()

    # calcoli righe
    imponibile = 0.0
    righe_to_insert = []
    for r in righe:
        prodotto = r["prodotto"]
        cartoni = int(r.get("cartoni") or 0)
        bottiglie = int(r.get("bottiglie") or 0)
        ppc = int(prodotto["pezzi_per_cartone"] or 1)
        pezzi = cartoni * ppc + bottiglie
        prezzo = float(prodotto["prezzo_unitario"] or 0)
        totale = pezzi * prezzo
        imponibile += totale
        righe_to_insert.append({
            "id": uid(),
            "ordine_id": ordine_id,
            "prodotto_id": prodotto["id"],
            "codice_prodotto": prodotto["codice"],
            "nome_prodotto": prodotto["nome"],
            "cartoni": cartoni,
            "bottiglie": bottiglie,
            "pezzi_totali": pezzi,
            "prezzo_unitario": prezzo,
            "totale_riga": totale,
        })

    conn.execute("""
        INSERT INTO ordini (id,numero,azienda_id,cliente_id,data_ordine,note,imponibile,stato,created_at)
        VALUES (?,?,?,?,?,?,?,?,?);
    """, (ordine_id, numero, azienda_id, cliente_id, data_ordine, note, imponibile, "confermato", created_at))

    conn.executemany("""
        INSERT INTO ordine_righe (id,ordine_id,prodotto_id,codice_prodotto,nome_prodotto,cartoni,bottiglie,pezzi_totali,prezzo_unitario,totale_riga)
        VALUES (:id,:ordine_id,:prodotto_id,:codice_prodotto,:nome_prodotto,:cartoni,:bottiglie,:pezzi_totali,:prezzo_unitario,:totale_riga);
    """, righe_to_insert)

    conn.commit()

    return {
        "id": ordine_id,
        "numero": numero,
        "azienda": azienda,
        "cliente": cliente,
        "data_ordine": data_ordine,
        "note": note,
        "imponibile": imponibile,
        "righe": righe_to_insert,
    }


def list_ordini(conn: sqlite3.Connection, azienda_id: Optional[str] = None) -> List[Dict[str, Any]]:
    q = """
        SELECT o.*,
               a.nome as azienda_nome,
               c.nome_azienda as cliente_nome
        FROM ordini o
        JOIN aziende a ON a.id=o.azienda_id
        JOIN clienti c ON c.id=o.cliente_id
    """
    params: List[Any] = []
    if azienda_id:
        q += " WHERE o.azienda_id=?"
        params.append(azienda_id)
    q += " ORDER BY o.data_ordine DESC;"
    cur = conn.execute(q, params)
    return [dict(r) for r in cur.fetchall()]


def get_ordine(conn: sqlite3.Connection, ordine_id: str) -> Optional[Dict[str, Any]]:
    cur = conn.execute("""
        SELECT o.*,
               a.nome as azienda_nome,
               c.nome_azienda as cliente_nome
        FROM ordini o
        JOIN aziende a ON a.id=o.azienda_id
        JOIN clienti c ON c.id=o.cliente_id
        WHERE o.id=?;
    """, (ordine_id,))
    o = cur.fetchone()
    if not o:
        return None
    righe = conn.execute("SELECT * FROM ordine_righe WHERE ordine_id=? ORDER BY nome_prodotto ASC;", (ordine_id,)).fetchall()
    pro = conn.execute("SELECT * FROM proforme WHERE ordine_id=?;", (ordine_id,)).fetchone()
    return {**dict(o), "righe": [dict(r) for r in righe], "proforma": dict(pro) if pro else None}


def _next_proforma_progressivo(conn: sqlite3.Connection, azienda_prefix: str, year: int) -> int:
    like = f"{azienda_prefix}-{year}-%"
    cur = conn.execute("SELECT numero FROM proforme WHERE numero LIKE ? ORDER BY numero DESC LIMIT 1;", (like,))
    row = cur.fetchone()
    if not row:
        return 1
    try:
        return int(row["numero"].split("-")[-1]) + 1
    except Exception:
        return 1


def create_proforma_record(conn: sqlite3.Connection, ordine_id: str, pdf_path: str) -> Dict[str, Any]:
    ordine = get_ordine(conn, ordine_id)
    if not ordine:
        raise ValueError("Ordine non trovato")
    azienda = get_azienda(conn, ordine["azienda_id"])
    if not azienda:
        raise ValueError("Azienda non trovata")

    year = datetime.now().year
    prefix = (azienda.get("nome") or "AZ").strip().upper()
    prefix = "".join([c for c in prefix if c.isalnum()])[:3] or "AZ"
    prog = _next_proforma_progressivo(conn, prefix, year)
    numero = f"{prefix}-{year}-{prog:04d}"

    pro_id = uid()
    data_proforma = now_iso()
    created_at = now_iso()

    conn.execute("""
        INSERT INTO proforme (id, ordine_id, numero, data_proforma, imponibile, pdf_path, created_at)
        VALUES (?,?,?,?,?,?,?);
    """, (pro_id, ordine_id, numero, data_proforma, float(ordine["imponibile"]), pdf_path, created_at))
    conn.commit()

    return {
        "id": pro_id,
        "ordine_id": ordine_id,
        "numero": numero,
        "data_proforma": data_proforma,
        "imponibile": float(ordine["imponibile"]),
        "pdf_path": pdf_path,
        "created_at": created_at,
    }
