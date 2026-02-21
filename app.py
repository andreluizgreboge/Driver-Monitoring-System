from flask import Flask, render_template, redirect, url_for
import sqlite3
import os
import threading
from auditor import process_pending_events, DB_PATH

# =============================
# APP CONFIG
# =============================
app = Flask(__name__)

# Lock para garantir que o Qwen não abra mil vezes na RAM de 16GB
audit_lock = threading.Lock()

# =============================
# DATABASE FUNCTION
# =============================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =============================
# ROUTES
# =============================
@app.route("/")
def dashboard():
    # 1. Tenta disparar a auditoria em background (Non-blocking)
    if audit_lock.acquire(blocking=False):
        def run_async_audit():
            try:
                # Chama a função que você arrumou no auditor.py
                process_pending_events()
            finally:
                audit_lock.release()
        
        threading.Thread(target=run_async_audit, daemon=True).start()

    # 2. Busca os dados do banco para renderizar o HTML
    conn = get_db_connection()
    # Ordenação: PENDING no topo, depois o resto por ID decrescente
    query = """
        SELECT * FROM events 
        ORDER BY 
            CASE WHEN status = 'PENDING' THEN 1 ELSE 2 END ASC, 
            id DESC
    """
    events = conn.execute(query).fetchall()
    conn.close()

    return render_template("dashboard.html", events=events)

from collections import Counter
from datetime import datetime

@app.route("/analytics")
def analytics():
    conn = get_db_connection()
    # Buscamos o tipo, timestamp e a decisão humana para cruzar os dados
    events = conn.execute("""
        SELECT event_type, timestamp, human_decision 
        FROM events 
        WHERE status = 'AI_REVIEWED'
    """).fetchall()
    conn.close()

    # 1. Distribution by Type (YOLO Detections)
    types = [e['event_type'] for e in events]
    type_counts = dict(Counter(types))

    # 2. Hourly Analysis (Peak Risk Hours)
    # Using a try/except block to handle potential format mismatches safely
    hour_counts = {h: 0 for h in range(24)}
    for e in events:
        try:
            # Matches the format: 2026-02-20 19-53-01
            dt = datetime.strptime(e['timestamp'], "%Y-%m-%d %H-%M-%S")
            hour_counts[dt.hour] += 1
        except ValueError:
            try:
                # Fallback for standard format: 2026-02-20 19:53:01
                dt = datetime.strptime(e['timestamp'], "%Y-%m-%d %H:%M:%S")
                hour_counts[dt.hour] += 1
            except:
                continue

    # 3. Human vs AI Comparison (The Accuracy Chart)
    # We count how many times you clicked 'Confirmed' vs 'Discarded'
    comparison = {"Confirmed": 0, "Discarded": 0, "Pending": 0}
    for e in events:
        decision = e['human_decision']
        if decision == 'Confirmed':
            comparison["Confirmed"] += 1
        elif decision == 'Discarded':
            comparison["Discarded"] += 1
        else:
            comparison["Pending"] += 1

    return render_template("analytics.html", 
                           type_counts=type_counts, 
                           hour_counts=hour_counts,
                           comparison=comparison)

@app.route("/update_decision/<int:event_id>/<decision>")
def update_decision(event_id, decision):
    conn = get_db_connection()
    # decision será 'confirmado' ou 'descartado'
    conn.execute("UPDATE events SET human_decision = ? WHERE id = ?", (decision, event_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    # Debug=True é bom, mas o reloader do Flask pode disparar a thread duas vezes.
    # Para PoC local, funciona bem.
    app.run(host="127.0.0.1", port=5000, debug=True)