import re

def extract_class(filename, class_name, out_file):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'(class ' + class_name + r'\b.*?:(?:\n(?:(?:[ \t]+.*?\n)|(?:\n))*)?)'
    match = re.search(pattern, content)
    if match:
        out_file.write(f"--- {class_name} ---\n")
        out_file.write(match.group(1))
        out_file.write("\n\n")
    else:
        out_file.write(f"Class {class_name} not found in {filename}\n")

with open('scratch_serializers.txt', 'w', encoding='utf-8') as out_f:
    extract_class('scratch_p2_serializers.py', 'PacienteRegistroPublicoSerializer', out_f)
