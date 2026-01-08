"""
PORTALE AGENTE DI COMMERCIO
Database Manager - Gestione completa SQLite
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
import uuid
import json

# Path del database
DB_PATH = os.path.join(os.path.dirname(__file__), 'portale_agente.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_connection() -> sqlite3.Connection:
    """Ottiene una connessione al database con row_factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Inizializza il database con lo schema"""
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema = f.read()
        conn.executescript(schema)

        # --- MIGRAZIONI/REGOLA COMMERCIALE ---
        # Cartone fisso: 6 pezzi per tutti i prodotti.
        # (Serve anche per database già esistenti creati con default=1)
        try:
            conn.execute("UPDATE prodotti SET pezzi_per_cartone = 6 WHERE pezzi_per_cartone IS NULL OR pezzi_per_cartone != 6")
        except Exception:
            pass

        conn.commit()
    finally:
        conn.close()


def generate_id() -> str:
    """Genera un ID univoco"""
    return str(uuid.uuid4())


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Converte una riga SQLite in dizionario"""
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Converte una lista di righe in lista di dizionari"""
    return [row_to_dict(row) for row in rows]


# ============================================
# AZIENDE
# ============================================

def get_aziende(solo_attive: bool = True) -> List[Dict]:
    """Ottiene tutte le aziende"""
    conn = get_connection()
    try:
        query = "SELECT * FROM aziende"
        if solo_attive:
            query += " WHERE attivo = 1"
        query += " ORDER BY nome"
        rows = conn.execute(query).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def get_azienda(azienda_id: str) -> Optional[Dict]:
    """Ottiene un'azienda per ID"""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM aziende WHERE id = ?", (azienda_id,)).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def save_azienda(data: Dict) -> str:
    """Salva o aggiorna un'azienda"""
    conn = get_connection()
    try:
        if 'id' in data and data['id']:
            # Update
            azienda_id = data['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at':
                    fields.append(f"{key} = ?")
                    values.append(value)
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(azienda_id)
            
            query = f"UPDATE aziende SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            # Insert
            azienda_id = generate_id()
            data['id'] = azienda_id
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            fields = list(data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO aziende ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(data.values()))
        
        conn.commit()
        return azienda_id
    finally:
        conn.close()


def delete_azienda(azienda_id: str) -> bool:
    """Elimina un'azienda (soft delete)"""
    conn = get_connection()
    try:
        conn.execute("UPDATE aziende SET attivo = 0, updated_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), azienda_id))
        conn.commit()
        return True
    finally:
        conn.close()


# ============================================
# CLIENTI
# ============================================

def get_clienti(solo_attivi: bool = True, search: str = None) -> List[Dict]:
    """Ottiene tutti i clienti"""
    conn = get_connection()
    try:
        query = "SELECT * FROM clienti WHERE 1=1"
        params = []
        
        if solo_attivi:
            query += " AND attivo = 1"
        
        if search:
            query += " AND (ragione_sociale LIKE ? OR codice LIKE ? OR citta LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY ragione_sociale"
        rows = conn.execute(query, params).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def get_cliente(cliente_id: str) -> Optional[Dict]:
    """Ottiene un cliente per ID"""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM clienti WHERE id = ?", (cliente_id,)).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def save_cliente(data: Dict) -> str:
    """Salva o aggiorna un cliente"""
    conn = get_connection()
    try:
        if 'id' in data and data['id']:
            # Update
            cliente_id = data['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at':
                    fields.append(f"{key} = ?")
                    values.append(value)
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(cliente_id)
            
            query = f"UPDATE clienti SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            # Insert
            cliente_id = generate_id()
            data['id'] = cliente_id
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            fields = list(data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO clienti ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(data.values()))
        
        conn.commit()
        return cliente_id
    finally:
        conn.close()


def delete_cliente(cliente_id: str) -> bool:
    """Elimina un cliente (soft delete)"""
    conn = get_connection()
    try:
        conn.execute("UPDATE clienti SET attivo = 0, updated_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), cliente_id))
        conn.commit()
        return True
    finally:
        conn.close()


# ============================================
# PRODOTTI
# ============================================

def get_prodotti(azienda_id: str = None, search: str = None, solo_disponibili: bool = True) -> List[Dict]:
    """Ottiene i prodotti, opzionalmente filtrati per azienda"""
    conn = get_connection()
    try:
        query = """
            SELECT p.*, a.nome AS azienda_nome 
            FROM prodotti p
            LEFT JOIN aziende a ON p.azienda_id = a.id
            WHERE 1=1
        """
        params = []
        
        if azienda_id:
            query += " AND p.azienda_id = ?"
            params.append(azienda_id)
        
        if solo_disponibili:
            query += " AND p.disponibile = 1"
        
        if search:
            query += " AND (p.nome LIKE ? OR p.codice LIKE ? OR p.descrizione LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY p.nome"
        rows = conn.execute(query, params).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def get_prodotto(prodotto_id: str) -> Optional[Dict]:
    """Ottiene un prodotto per ID"""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT p.*, a.nome AS azienda_nome 
            FROM prodotti p
            LEFT JOIN aziende a ON p.azienda_id = a.id
            WHERE p.id = ?
        """, (prodotto_id,)).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_prodotti_acquistati_cliente(cliente_id: str, azienda_id: str = None) -> List[str]:
    """Ottiene gli ID dei prodotti già acquistati da un cliente"""
    conn = get_connection()
    try:
        query = """
            SELECT DISTINCT r.prodotto_id
            FROM ordini_righe r
            JOIN ordini o ON r.ordine_id = o.id
            WHERE o.cliente_id = ? AND o.stato IN ('inviato', 'confermato', 'evaso')
        """
        params = [cliente_id]
        
        if azienda_id:
            query += " AND o.azienda_id = ?"
            params.append(azienda_id)
        
        rows = conn.execute(query, params).fetchall()
        return [row['prodotto_id'] for row in rows]
    finally:
        conn.close()


def save_prodotto(data: Dict) -> str:
    """Salva o aggiorna un prodotto"""
    # Regola fissa: 1 cartone = 6 pezzi
    if data is not None:
        data['pezzi_per_cartone'] = 6
    conn = get_connection()
    try:
        if 'id' in data and data['id']:
            # Update
            prodotto_id = data['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at':
                    fields.append(f"{key} = ?")
                    values.append(value)
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(prodotto_id)
            
            query = f"UPDATE prodotti SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            # Insert
            prodotto_id = generate_id()
            data['id'] = prodotto_id
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            fields = list(data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO prodotti ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(data.values()))
        
        conn.commit()
        return prodotto_id
    finally:
        conn.close()


def delete_prodotto(prodotto_id: str) -> bool:
    """Elimina un prodotto"""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM prodotti WHERE id = ?", (prodotto_id,))
        conn.commit()
        return True
    finally:
        conn.close()


# ============================================
# ORDINI
# ============================================

def get_prossimo_numero_ordine() -> str:
    """Genera il prossimo numero ordine"""
    conn = get_connection()
    try:
        # Ottieni impostazioni
        row = conn.execute("SELECT valore FROM impostazioni WHERE chiave = 'numero_ordine_progressivo'").fetchone()
        progressivo = int(row['valore']) if row else 1
        
        row = conn.execute("SELECT valore FROM impostazioni WHERE chiave = 'numero_ordine_prefisso'").fetchone()
        prefisso = row['valore'] if row else 'ORD'
        
        row = conn.execute("SELECT valore FROM impostazioni WHERE chiave = 'numero_ordine_anno'").fetchone()
        include_anno = row['valore'] == '1' if row else True
        
        # Genera numero
        anno = datetime.now().year
        if include_anno:
            numero = f"{prefisso}-{anno}-{progressivo:05d}"
        else:
            numero = f"{prefisso}-{progressivo:05d}"
        
        # Incrementa progressivo
        conn.execute("UPDATE impostazioni SET valore = ?, updated_at = ? WHERE chiave = 'numero_ordine_progressivo'",
                    (str(progressivo + 1), datetime.now().isoformat()))
        conn.commit()
        
        return numero
    finally:
        conn.close()


def get_ordini(stato: str = None, azienda_id: str = None, cliente_id: str = None, 
               data_da: str = None, data_a: str = None, limit: int = None) -> List[Dict]:
    """Ottiene gli ordini con filtri"""
    conn = get_connection()
    try:
        query = """
            SELECT o.*, 
                   a.nome AS azienda_nome,
                   c.ragione_sociale AS cliente_ragione_sociale,
                   c.citta AS cliente_citta,
                   c.provincia AS cliente_provincia
            FROM ordini o
            LEFT JOIN aziende a ON o.azienda_id = a.id
            LEFT JOIN clienti c ON o.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if stato:
            query += " AND o.stato = ?"
            params.append(stato)
        
        if azienda_id:
            query += " AND o.azienda_id = ?"
            params.append(azienda_id)
        
        if cliente_id:
            query += " AND o.cliente_id = ?"
            params.append(cliente_id)
        
        if data_da:
            query += " AND o.data_ordine >= ?"
            params.append(data_da)
        
        if data_a:
            query += " AND o.data_ordine <= ?"
            params.append(data_a)
        
        query += " ORDER BY o.data_ordine DESC, o.numero DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = conn.execute(query, params).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def get_ordine(ordine_id: str) -> Optional[Dict]:
    """Ottiene un ordine con tutti i dettagli"""
    conn = get_connection()
    try:
        # Testata
        row = conn.execute("""
            SELECT o.*, 
                   a.nome AS azienda_nome,
                   a.ragione_sociale AS azienda_ragione_sociale,
                   a.indirizzo AS azienda_indirizzo,
                   a.citta AS azienda_citta,
                   a.provincia AS azienda_provincia,
                   a.cap AS azienda_cap,
                   a.telefono AS azienda_telefono,
                   a.email AS azienda_email,
                   a.partita_iva AS azienda_piva,
                   c.ragione_sociale AS cliente_ragione_sociale,
                   c.indirizzo AS cliente_indirizzo,
                   c.citta AS cliente_citta,
                   c.provincia AS cliente_provincia,
                   c.cap AS cliente_cap,
                   c.telefono AS cliente_telefono,
                   c.email AS cliente_email,
                   c.partita_iva AS cliente_piva,
                   c.codice_fiscale AS cliente_cf
            FROM ordini o
            LEFT JOIN aziende a ON o.azienda_id = a.id
            LEFT JOIN clienti c ON o.cliente_id = c.id
            WHERE o.id = ?
        """, (ordine_id,)).fetchone()
        
        if not row:
            return None
        
        ordine = row_to_dict(row)
        
        # Righe
        righe = conn.execute("""
            SELECT r.*, p.codice AS prodotto_codice, p.nome AS prodotto_nome,
                   p.unita_misura, p.pezzi_per_cartone
            FROM ordini_righe r
            LEFT JOIN prodotti p ON r.prodotto_id = p.id
            WHERE r.ordine_id = ?
            ORDER BY r.posizione
        """, (ordine_id,)).fetchall()
        
        ordine['righe'] = rows_to_list(righe)
        
        return ordine
    finally:
        conn.close()


def save_ordine(testata: Dict, righe: List[Dict]) -> str:
    """Salva un ordine completo (testata + righe).

    Fix importanti:
    - calcola automaticamente prezzo_finale/importo_riga se mancanti
    - filtra solo le colonne effettive della tabella (evita errori con campi UI)
    - aggiorna una tabella di prefill (cliente_prodotto_pref) per ricordare prezzo/quantità dell'ultimo ordine
    """
    conn = get_connection()
    try:
        conn.execute("BEGIN")

        # colonne ammesse per evitare mismatch
        allowed_testata = {
            'id','numero','data_ordine','azienda_id','cliente_id','pagamento','consegna_tipo',
            'totale_pezzi','totale_cartoni','imponibile','sconto_chiusura','totale_finale',
            'stato','note','data_invio','data_conferma','data_evasione','created_at','updated_at'
        }
        allowed_riga = {
            'id','ordine_id','prodotto_id','quantita_cartoni','quantita_pezzi','quantita_totale',
            'prezzo_unitario','sconto_riga','prezzo_finale','importo_riga','posizione','note','created_at'
        }

        if 'id' in testata and testata['id']:
            ordine_id = testata['id']
            # Update testata
            fields = []
            values = []
            for key, value in testata.items():
                if key in allowed_testata and key not in ('id','created_at','updated_at'):
                    fields.append(f"{key} = ?")
                    values.append(value)
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(ordine_id)
            query = f"UPDATE ordini SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)

            # Elimina vecchie righe
            conn.execute("DELETE FROM ordini_righe WHERE ordine_id = ?", (ordine_id,))
        else:
            # Insert testata
            ordine_id = generate_id()
            now = datetime.now().isoformat()
            testata = dict(testata)
            testata['id'] = ordine_id
            testata['created_at'] = now
            testata['updated_at'] = now

            insert_data = {k: v for k, v in testata.items() if k in allowed_testata}
            fields = list(insert_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO ordini ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(insert_data.values()))

        # Insert righe
        for i, riga in enumerate(righe):
            r = dict(riga)
            r['id'] = generate_id()
            r['ordine_id'] = ordine_id
            r['posizione'] = i + 1
            r['created_at'] = datetime.now().isoformat()

            # normalizza quantità
            r['quantita_cartoni'] = int(r.get('quantita_cartoni') or 0)
            r['quantita_pezzi'] = int(r.get('quantita_pezzi') or 0)
            r['quantita_totale'] = int(r.get('quantita_totale') or 0)

            prezzo_unitario = float(r.get('prezzo_unitario') or 0)
            sconto = float(r.get('sconto_riga') or 0)
            if r.get('prezzo_finale') is None:
                r['prezzo_finale'] = prezzo_unitario * (1 - sconto / 100)
            if r.get('importo_riga') is None:
                r['importo_riga'] = float(r['prezzo_finale']) * float(r['quantita_totale'])

            insert_riga = {k: v for k, v in r.items() if k in allowed_riga}
            fields = list(insert_riga.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO ordini_righe ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(insert_riga.values()))

        # Aggiorna prefill per ordine successivo
        try:
            cliente_id = testata.get('cliente_id')
            azienda_id = testata.get('azienda_id')
            if cliente_id and azienda_id:
                _upsert_cliente_prodotto_pref(conn, cliente_id, azienda_id, righe)
        except Exception:
            # non blocchiamo il salvataggio ordine se fallisce il prefill
            pass

        conn.commit()
        return ordine_id
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def _upsert_cliente_prodotto_pref(conn: sqlite3.Connection, cliente_id: str, azienda_id: str, righe: List[Dict]) -> None:
    """Upsert delle preferenze (ultimo prezzo/quantità) per ogni prodotto del cliente."""
    now = datetime.now().isoformat()
    for r in righe:
        prodotto_id = r.get('prodotto_id')
        if not prodotto_id:
            continue
        prezzo_unitario = float(r.get('prezzo_unitario') or 0)
        sconto = float(r.get('sconto_riga') or 0)
        qc = int(r.get('quantita_cartoni') or 0)
        qp = int(r.get('quantita_pezzi') or 0)

        conn.execute(
            """
            INSERT INTO cliente_prodotto_pref (cliente_id, azienda_id, prodotto_id, prezzo_unitario, sconto_riga, quantita_cartoni, quantita_pezzi, updated_at)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(cliente_id, azienda_id, prodotto_id)
            DO UPDATE SET
                prezzo_unitario=excluded.prezzo_unitario,
                sconto_riga=excluded.sconto_riga,
                quantita_cartoni=excluded.quantita_cartoni,
                quantita_pezzi=excluded.quantita_pezzi,
                updated_at=excluded.updated_at
            """,
            (cliente_id, azienda_id, prodotto_id, prezzo_unitario, sconto, qc, qp, now)
        )


def get_cliente_prodotti_pref(cliente_id: str, azienda_id: str) -> Dict[str, Dict]:
    """Ritorna dict {prodotto_id: pref} per precompilare l'ordine successivo."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT prodotto_id, prezzo_unitario, sconto_riga, quantita_cartoni, quantita_pezzi, updated_at
            FROM cliente_prodotto_pref
            WHERE cliente_id = ? AND azienda_id = ?
            """,
            (cliente_id, azienda_id)
        ).fetchall()
        out: Dict[str, Dict] = {}
        for r in rows:
            out[r['prodotto_id']] = dict(r)
        return out
    finally:
        conn.close()


def update_stato_ordine(ordine_id: str, nuovo_stato: str) -> bool:
    """Aggiorna lo stato di un ordine"""
    conn = get_connection()
    try:
        now = datetime.now().isoformat()
        
        update_fields = ["stato = ?", "updated_at = ?"]
        params = [nuovo_stato, now]
        
        if nuovo_stato == 'inviato':
            update_fields.append("data_invio = ?")
            params.append(now)
        elif nuovo_stato == 'confermato':
            update_fields.append("data_conferma = ?")
            params.append(now)
        elif nuovo_stato == 'evaso':
            update_fields.append("data_evasione = ?")
            params.append(now)
        
        params.append(ordine_id)
        
        query = f"UPDATE ordini SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, params)
        conn.commit()
        return True
    finally:
        conn.close()


def delete_ordine(ordine_id: str) -> bool:
    """Elimina un ordine"""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM ordini_righe WHERE ordine_id = ?", (ordine_id,))
        conn.execute("DELETE FROM ordini WHERE id = ?", (ordine_id,))
        conn.commit()
        return True
    finally:
        conn.close()


# ============================================
# PROMEMORIA
# ============================================

def get_promemoria(solo_attivi: bool = True, cliente_id: str = None) -> List[Dict]:
    """Ottiene i promemoria"""
    conn = get_connection()
    try:
        query = """
            SELECT p.*, c.ragione_sociale AS cliente_nome
            FROM promemoria p
            LEFT JOIN clienti c ON p.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if solo_attivi:
            query += " AND p.completato = 0"
        
        if cliente_id:
            query += " AND p.cliente_id = ?"
            params.append(cliente_id)
        
        query += " ORDER BY p.data_scadenza ASC"
        
        rows = conn.execute(query, params).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def save_promemoria(data: Dict) -> str:
    """Salva o aggiorna un promemoria"""
    conn = get_connection()
    try:
        if 'id' in data and data['id']:
            promemoria_id = data['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at' and key != 'cliente_nome':
                    fields.append(f"{key} = ?")
                    values.append(value)
            values.append(promemoria_id)
            
            query = f"UPDATE promemoria SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            promemoria_id = generate_id()
            data['id'] = promemoria_id
            data['created_at'] = datetime.now().isoformat()
            
            insert_data = {k: v for k, v in data.items() if k != 'cliente_nome'}
            
            fields = list(insert_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO promemoria ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(insert_data.values()))
        
        conn.commit()
        return promemoria_id
    finally:
        conn.close()


def completa_promemoria(promemoria_id: str) -> bool:
    """Segna un promemoria come completato"""
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE promemoria 
            SET completato = 1, data_completamento = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), promemoria_id))
        conn.commit()
        return True
    finally:
        conn.close()


def delete_promemoria(promemoria_id: str) -> bool:
    """Elimina un promemoria"""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM promemoria WHERE id = ?", (promemoria_id,))
        conn.commit()
        return True
    finally:
        conn.close()


# ============================================
# VISITE
# ============================================

def get_visite_pianificate(data_da: str = None, data_a: str = None, solo_non_completate: bool = True) -> List[Dict]:
    """Ottiene le visite pianificate"""
    conn = get_connection()
    try:
        query = """
            SELECT vp.*, c.ragione_sociale AS cliente_nome, c.indirizzo AS cliente_indirizzo,
                   c.citta AS cliente_citta, c.provincia AS cliente_provincia, c.telefono AS cliente_telefono
            FROM visite_pianificate vp
            LEFT JOIN clienti c ON vp.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if solo_non_completate:
            query += " AND vp.completata = 0"
        
        if data_da:
            query += " AND vp.data_pianificata >= ?"
            params.append(data_da)
        
        if data_a:
            query += " AND vp.data_pianificata <= ?"
            params.append(data_a)
        
        query += " ORDER BY vp.data_pianificata ASC, vp.ora_inizio ASC"
        
        rows = conn.execute(query, params).fetchall()
        return rows_to_list(rows)
    finally:
        conn.close()


def save_visita_pianificata(data: Dict) -> str:
    """Salva una visita pianificata"""
    conn = get_connection()
    try:
        if 'id' in data and data['id']:
            visita_id = data['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at' and not key.startswith('cliente_'):
                    fields.append(f"{key} = ?")
                    values.append(value)
            values.append(visita_id)
            
            query = f"UPDATE visite_pianificate SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            visita_id = generate_id()
            data['id'] = visita_id
            data['created_at'] = datetime.now().isoformat()
            
            insert_data = {k: v for k, v in data.items() if not k.startswith('cliente_')}
            
            fields = list(insert_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO visite_pianificate ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(insert_data.values()))
        
        conn.commit()
        return visita_id
    finally:
        conn.close()


# ============================================
# AGENTE
# ============================================

def get_agente() -> Optional[Dict]:
    """Ottiene i dati dell'agente"""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM agente LIMIT 1").fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def save_agente(data: Dict) -> str:
    """Salva i dati dell'agente"""
    conn = get_connection()
    try:
        # Verifica se esiste già
        existing = conn.execute("SELECT id FROM agente LIMIT 1").fetchone()
        
        if existing:
            agente_id = existing['id']
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id' and key != 'created_at':
                    fields.append(f"{key} = ?")
                    values.append(value)
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(agente_id)
            
            query = f"UPDATE agente SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
        else:
            agente_id = generate_id()
            data['id'] = agente_id
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            fields = list(data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            query = f"INSERT INTO agente ({', '.join(fields)}) VALUES ({placeholders})"
            conn.execute(query, list(data.values()))
        
        conn.commit()
        return agente_id
    finally:
        conn.close()


# ============================================
# STATISTICHE E REPORT
# ============================================

def get_statistiche_dashboard() -> Dict:
    """Ottiene le statistiche per la dashboard"""
    conn = get_connection()
    try:
        stats = {}
        
        # Totale clienti attivi
        row = conn.execute("SELECT COUNT(*) as cnt FROM clienti WHERE attivo = 1").fetchone()
        stats['totale_clienti'] = row['cnt']
        
        # Totale aziende attive
        row = conn.execute("SELECT COUNT(*) as cnt FROM aziende WHERE attivo = 1").fetchone()
        stats['totale_aziende'] = row['cnt']
        
        # Totale prodotti
        row = conn.execute("SELECT COUNT(*) as cnt FROM prodotti WHERE disponibile = 1").fetchone()
        stats['totale_prodotti'] = row['cnt']
        
        # Ordini mese corrente
        primo_mese = date.today().replace(day=1).isoformat()
        row = conn.execute("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(totale_finale), 0) as totale
            FROM ordini 
            WHERE data_ordine >= ? AND stato != 'annullato'
        """, (primo_mese,)).fetchone()
        stats['ordini_mese'] = row['cnt']
        stats['fatturato_mese'] = row['totale']
        
        # Ordini anno corrente
        primo_anno = date.today().replace(month=1, day=1).isoformat()
        row = conn.execute("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(totale_finale), 0) as totale
            FROM ordini 
            WHERE data_ordine >= ? AND stato != 'annullato'
        """, (primo_anno,)).fetchone()
        stats['ordini_anno'] = row['cnt']
        stats['fatturato_anno'] = row['totale']
        
        # Promemoria scaduti
        oggi = date.today().isoformat()
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM promemoria 
            WHERE completato = 0 AND data_scadenza < ?
        """, (oggi,)).fetchone()
        stats['promemoria_scaduti'] = row['cnt']
        
        # Promemoria oggi
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM promemoria 
            WHERE completato = 0 AND data_scadenza = ?
        """, (oggi,)).fetchone()
        stats['promemoria_oggi'] = row['cnt']
        
        # Visite oggi
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM visite_pianificate 
            WHERE completata = 0 AND data_pianificata = ?
        """, (oggi,)).fetchone()
        stats['visite_oggi'] = row['cnt']
        
        return stats
    finally:
        conn.close()


def get_fatturato_per_azienda(anno: int = None) -> List[Dict]:
    """Ottiene il fatturato raggruppato per azienda"""
    conn = get_connection()
    try:
        if anno is None:
            anno = date.today().year
        
        primo_anno = f"{anno}-01-01"
        ultimo_anno = f"{anno}-12-31"
        
        rows = conn.execute("""
            SELECT a.id, a.nome,
                   COUNT(DISTINCT o.id) as num_ordini,
                   COALESCE(SUM(o.totale_finale), 0) as fatturato
            FROM aziende a
            LEFT JOIN ordini o ON a.id = o.azienda_id 
                AND o.data_ordine BETWEEN ? AND ?
                AND o.stato IN ('inviato', 'confermato', 'evaso')
            WHERE a.attivo = 1
            GROUP BY a.id, a.nome
            ORDER BY fatturato DESC
        """, (primo_anno, ultimo_anno)).fetchall()
        
        return rows_to_list(rows)
    finally:
        conn.close()


def get_fatturato_per_cliente(anno: int = None, limit: int = 20) -> List[Dict]:
    """Ottiene il fatturato raggruppato per cliente"""
    conn = get_connection()
    try:
        if anno is None:
            anno = date.today().year
        
        primo_anno = f"{anno}-01-01"
        ultimo_anno = f"{anno}-12-31"
        
        rows = conn.execute(f"""
            SELECT c.id, c.ragione_sociale, c.citta, c.provincia,
                   COUNT(DISTINCT o.id) as num_ordini,
                   COALESCE(SUM(o.totale_finale), 0) as fatturato,
                   MAX(o.data_ordine) as ultimo_ordine
            FROM clienti c
            LEFT JOIN ordini o ON c.id = o.cliente_id 
                AND o.data_ordine BETWEEN ? AND ?
                AND o.stato IN ('inviato', 'confermato', 'evaso')
            WHERE c.attivo = 1
            GROUP BY c.id, c.ragione_sociale, c.citta, c.provincia
            HAVING fatturato > 0
            ORDER BY fatturato DESC
            LIMIT {limit}
        """, (primo_anno, ultimo_anno)).fetchall()
        
        return rows_to_list(rows)
    finally:
        conn.close()


def get_fatturato_per_mese(anno: int = None) -> List[Dict]:
    """Ottiene il fatturato mensile"""
    conn = get_connection()
    try:
        if anno is None:
            anno = date.today().year
        
        rows = conn.execute("""
            SELECT strftime('%m', data_ordine) as mese,
                   COUNT(*) as num_ordini,
                   SUM(totale_finale) as fatturato
            FROM ordini
            WHERE strftime('%Y', data_ordine) = ?
                AND stato IN ('inviato', 'confermato', 'evaso')
            GROUP BY strftime('%m', data_ordine)
            ORDER BY mese
        """, (str(anno),)).fetchall()
        
        return rows_to_list(rows)
    finally:
        conn.close()


def get_top_prodotti(anno: int = None, limit: int = 10) -> List[Dict]:
    """Ottiene i prodotti più venduti"""
    conn = get_connection()
    try:
        if anno is None:
            anno = date.today().year
        
        primo_anno = f"{anno}-01-01"
        ultimo_anno = f"{anno}-12-31"
        
        rows = conn.execute(f"""
            SELECT p.id, p.codice, p.nome, a.nome as azienda_nome,
                   SUM(r.quantita_totale) as quantita_venduta,
                   SUM(r.importo_riga) as fatturato
            FROM ordini_righe r
            JOIN ordini o ON r.ordine_id = o.id
            JOIN prodotti p ON r.prodotto_id = p.id
            JOIN aziende a ON p.azienda_id = a.id
            WHERE o.data_ordine BETWEEN ? AND ?
                AND o.stato IN ('inviato', 'confermato', 'evaso')
            GROUP BY p.id, p.codice, p.nome, a.nome
            ORDER BY fatturato DESC
            LIMIT {limit}
        """, (primo_anno, ultimo_anno)).fetchall()
        
        return rows_to_list(rows)
    finally:
        conn.close()


# ============================================
# INIZIALIZZAZIONE
# ============================================

# Inizializza il database all'import del modulo
if not os.path.exists(DB_PATH):
    init_db()
