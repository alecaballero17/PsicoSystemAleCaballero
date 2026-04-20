import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='P5ico_5yst3m_2026!#', host='127.0.0.1', port='5432')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute('DROP DATABASE IF EXISTS db_psicosystem WITH (FORCE);')
    cursor.execute('CREATE DATABASE db_psicosystem;')
    print('Database reseteada con exito.')
    cursor.close()
    conn.close()
except Exception as e:
    print('Error:', e)
