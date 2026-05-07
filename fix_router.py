import os
import sys

# Update P4 urls.py
file_path_p4 = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\urls.py'
with open(file_path_p4, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('DefaultRouter', 'SimpleRouter')
with open(file_path_p4, 'w', encoding='utf-8') as f:
    f.write(content)

# Update P2 urls.py
file_path_p2 = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P2_Gestion_Clinica\urls.py'
if os.path.exists(file_path_p2):
    with open(file_path_p2, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('DefaultRouter', 'SimpleRouter')
    with open(file_path_p2, 'w', encoding='utf-8') as f:
        f.write(content)

# Update P3 urls.py just in case
file_path_p3 = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P3_Logistica_Citas\urls.py'
if os.path.exists(file_path_p3):
    with open(file_path_p3, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('DefaultRouter', 'SimpleRouter')
    with open(file_path_p3, 'w', encoding='utf-8') as f:
        f.write(content)

# Update P1 urls.py just in case
file_path_p1 = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P1_Identidad_Acceso\urls.py'
if os.path.exists(file_path_p1):
    with open(file_path_p1, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('DefaultRouter', 'SimpleRouter')
    with open(file_path_p1, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated all routers to SimpleRouter')
