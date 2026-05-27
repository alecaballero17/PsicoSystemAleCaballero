import socket

hosts = [
    "dpg-d7e0kn9j2pic73fu16c0-a",
    "dpg-d7e0kn9j2pic73fu16c0-a.oregon-postgres.render.com",
    "dpg-d7e0kn9j2pic73fu16c0-a-a.oregon-postgres.render.com",
    "dpg-d7e0kn9j2pic73fu16c0.oregon-postgres.render.com"
]

for host in hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"SUCCESS: {host} -> {ip}")
    except Exception as e:
        print(f"FAILED: {host} -> {e}")
