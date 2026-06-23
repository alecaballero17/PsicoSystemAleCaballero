from django.db import connection, transaction
try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ADD COLUMN IF NOT EXISTS horario_atencion varchar(200) DEFAULT \'\';')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ADD COLUMN IF NOT EXISTS ultima_fecha_pass timestamp with time zone DEFAULT CURRENT_TIMESTAMP;')
        cursor.execute('ALTER TABLE "P1_Identidad_Acceso_usuario" ADD COLUMN IF NOT EXISTS forzar_cambio_pass boolean DEFAULT false;')
    connection.commit()
    print('Usuario columns added successfully')
except Exception as e:
    print('Error:', e)
