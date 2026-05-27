import psycopg2
import sys

dsn = "postgresql://psicosystem_db_7292_user:AG3Ux8zIxuPKlnIfuRNqSVvA0zLAElTC@dpg-d7e0kn9j2pic73fu16c0-a.oregon-postgres.render.com/psicosystem_db_7292?sslmode=require"

try:
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    
    # Intenta buscar las tablas
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    
    if not tables:
        print("La base de datos en Render ESTÁ VACÍA (no tiene tablas).")
        sys.exit(0)
    
    # Busca la tabla de usuarios
    # Django típicamente usa 'auth_user' o un custom user model.
    # En este proyecto el custom user module parece ser 'P1_Identidad_Acceso_usuario'
    user_table = None
    for t in tables:
        if 'usuario' in t[0].lower() or 'user' in t[0].lower():
            if 'P1_Identidad_Acceso_usuario'.lower() == t[0].lower() or 'auth_user' == t[0].lower():
                user_table = t[0]
                break
    
    if not user_table:
        print("No se encontró la tabla de usuarios.")
        sys.exit(0)
        
    print(f"Consultando la tabla de usuarios: {user_table}")
    cur.execute(f"SELECT email, username, rol FROM {user_table} LIMIT 10;")
    users = cur.fetchall()
    
    if not users:
        print("La tabla de usuarios está vacía. No hay credenciales.")
    else:
        print("Usuarios encontrados:")
        for u in users:
            print(f"Email: {u[0]}, Username: {u[1]}, Rol: {u[2] if len(u)>2 else 'N/A'}")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
