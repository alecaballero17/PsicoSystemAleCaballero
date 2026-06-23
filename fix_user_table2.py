from django.db import connection, transaction
try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ALTER COLUMN debe_cambiar_password DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ALTER COLUMN cancelaciones_hoy DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ALTER COLUMN ultima_cancelacion_fecha DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ALTER COLUMN ultimo_cambio_password DROP NOT NULL;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ALTER COLUMN ci DROP NOT NULL;')
    connection.commit()
    print('Usuario extra constraints dropped successfully')
except Exception as e:
    print('Error:', e)
