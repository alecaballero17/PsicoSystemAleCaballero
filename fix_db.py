from django.db import connection, transaction
try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN email_contacto DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN especialidades DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN horarios_atencion DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN telefono DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN saldo DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN fecha_creacion DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_clinica" ALTER COLUMN logo DROP NOT NULL;')
    connection.commit()
    print('All constraints dropped successfully with COMMIT')
except Exception as e:
    print('Error:', e)
