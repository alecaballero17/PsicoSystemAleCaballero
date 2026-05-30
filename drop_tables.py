import sys
import psycopg2

def main():
    if len(sys.argv) < 2:
        print("Uso: python drop_tables.py <DATABASE_URL>")
        sys.exit(1)

    db_url = sys.argv[1]
    try:
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Obtener todas las tablas en el esquema public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("La base de datos ya está vacía. No hay tablas para borrar.")
            cursor.close()
            conn.close()
            return
            
        print(f"Se encontraron {len(tables)} tablas. Iniciando borrado en cascada...")
        for table in tables:
            table_name = table[0]
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            print(f"✓ Tabla '{table_name}' eliminada.")
            
        cursor.close()
        conn.close()
        print("¡Base de datos limpiada con éxito! Lista para migrar.")
    except Exception as e:
        print("Error al limpiar la base de datos:", e)

if __name__ == "__main__":
    main()
