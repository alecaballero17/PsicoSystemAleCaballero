import subprocess
import sys
import re

def run_migrations():
    while True:
        print("Ejecutando: python manage.py migrate")
        process = subprocess.Popen(
            ['python', 'manage.py', 'migrate'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(stdout)
            print("========================================")
            print("Migraciones completadas exitosamente.")
            return

        output = stdout + "\n" + stderr
        print("Se detectó un error en las migraciones:")
        print(output)
        
        # Check if the error is due to something already existing
        if "already exists" in output:
            # We need to find which migration failed
            # Format is usually: "Applying app_label.migration_name... "
            # Let's extract the last one that was applying
            applying_matches = re.findall(r"Applying\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\.\.\.", output)
            if applying_matches:
                app_label, migration_name = applying_matches[-1]
                print(f"========================================")
                print(f"Falsificando migración conflictiva que ya existe en DB: {app_label}.{migration_name}")
                fake_process = subprocess.run(
                    ['python', 'manage.py', 'migrate', app_label, migration_name, '--fake'],
                    capture_output=True,
                    text=True
                )
                if fake_process.returncode == 0:
                    print("Falsificación exitosa. Reintentando migraciones...")
                    continue
                else:
                    print("Error al falsificar la migración:")
                    print(fake_process.stderr)
                    sys.exit(1)
            else:
                print("No se pudo detectar qué migración falló. Abortando.")
                sys.exit(1)
        else:
            print("El error no es 'already exists'. Abortando.")
            sys.exit(1)

if __name__ == "__main__":
    run_migrations()
