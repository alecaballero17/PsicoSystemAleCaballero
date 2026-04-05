import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"


def print_separator():
    print("-" * 50)


print("🚀 Simulador de App Móvil Flutter (Test de API)")
print_separator()

# Paso 1: Autenticación (Asumimos que el Psicólogo inicia sesión en la App Móvil)
print("1. Iniciando sesión como Psicólogo...")
username = input("Ingresa tu usuario (ej. admin o psicologo_test): ")
password = input("Ingresa tu contraseña (ej. 1234): ")

response = requests.post(
    f"{BASE_URL}/auth/login/", json={"username": username, "password": password}
)

if response.status_code != 200:
    print(
        f"❌ Error al iniciar sesión. Verifica tus credenciales. (HTTP {response.status_code})"
    )
    print(response.json())
    sys.exit(1)

tokens = response.json()
access_token = tokens.get("access")
role = tokens.get("role")

print("✅ ¡Login Exitoso! Token recibido.")
print(f"👤 Rol detectado en el token JWT: {role}")
print_separator()

# Paso 2: Registrar Paciente desde el Móvil
print("2. Registrando un nuevo paciente desde Flutter...")
nuevo_paciente = {
    "nombre": "Juan Pérez (Test Flutter)",
    "ci": "12345678",
    "fecha_nacimiento": "1990-05-15",
    "telefono": "77766655",
    "motivo_consulta": "Ansiedad severa y estrés académico",
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

response_paciente = requests.post(
    f"{BASE_URL}/pacientes/registrar/", json=nuevo_paciente, headers=headers
)

if response_paciente.status_code == 201:
    print("✅ ¡Paciente registrado exitosamente vía API REST!")
    print(
        "El Backend ha protegido la información vinculándolo automáticamente a tu clínica (Multi-tenant) gracias al Token."
    )
    print("Respuesta de la BD:")
    print(json.dumps(response_paciente.json(), indent=2, ensure_ascii=False))
else:
    print(f"❌ Error al registrar paciente. (HTTP {response_paciente.status_code})")
    print(json.dumps(response_paciente.json(), indent=2, ensure_ascii=False))
