import sqlite3
import os

# =============================
# PATH CONFIG
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_database():
    # Conecta ao arquivo (cria se não existir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ATENÇÃO: Se quiser resetar o banco totalmente, descomente a linha abaixo:
    # cursor.execute("DROP TABLE IF EXISTS events")

    # ==================================
    # SCHEMA COMPLETO (IA + HUMANO)
    # ==================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        truck_id TEXT,
        timestamp TEXT,
        event_type TEXT,
        status TEXT DEFAULT 'PENDING',
        image_path TEXT,
        ai_analysis TEXT,
        ai_confidence TEXT,
        human_decision TEXT DEFAULT 'PENDING'  -- Adicionado para auditoria humana
    )
    """)

    conn.commit()
    conn.close()
    print("--- 🛠️ Banco de Dados inicializado com sucesso! (IA + Humano Ready) ---")

if __name__ == "__main__":
    init_database()