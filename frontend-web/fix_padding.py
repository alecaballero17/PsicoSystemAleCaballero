import os

path = r'c:\Users\ElCremosasWee\PsicoSystem_SI2\frontend-web\src\pages'
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith('.js'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            if "padding: '32px 40px'" in content:
                content = content.replace("padding: '32px 40px'", "padding: 'clamp(16px, 5vw, 40px)'")
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Fixed {f}")
