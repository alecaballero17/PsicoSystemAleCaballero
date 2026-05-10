import psycopg2
import sys

dsn = "postgresql://psicosystem_db_7292_user:AG3Ux8zIxuPKlnIfuRNqSVvA0zLAElTC@dpg-d7e0kn9j2pic73fu16c0-a.oregon-postgres.render.com/psicosystem_db_7292"

try:
    print("Conectando a la base de datos de Render...")
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Limpiando esquema public...")
    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    
    print("✅ Base de datos reseteada con éxito. Ahora está vacía y lista.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
