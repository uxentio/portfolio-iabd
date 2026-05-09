import json

with open("UT7_autor_XXXXXXXXX.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

with open("nb_content.txt", "w", encoding="utf-8") as out:
    for i, cell in enumerate(nb.get("cells", [])):
        ctype = cell.get("cell_type")
        out.write(f"--- Cell {i} ({ctype}) ---\n")
        out.write("".join(cell.get("source", [])))
        out.write("\n\n")
