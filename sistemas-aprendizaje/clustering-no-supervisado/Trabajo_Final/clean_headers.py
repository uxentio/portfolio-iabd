import json
import re

file_path = "UT7_autor_XXXXXXXXX.ipynb"

# Leer el cuaderno
with open(file_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Expresiones regulares para encontrar cabeceras HTML con estilos
h1_pattern = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
h2_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.IGNORECASE | re.DOTALL)
h3_pattern = re.compile(r'<h3[^>]*>(.*?)</h3>', re.IGNORECASE | re.DOTALL)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "markdown":
        new_source = []
        for line in cell.get("source", []):
            # Formateamos las cabeceras a Markdown estándar (#, ##, ###)
            line = h1_pattern.sub(r'# \1', line)
            line = h2_pattern.sub(r'## \1', line)
            line = h3_pattern.sub(r'### \1', line)
            new_source.append(line)
        cell["source"] = new_source

# Guardar los cambios
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
    
print("Cabeceras limpiadas y convertidas a Markdown estándar.")
