#!/usr/bin/env python3
"""Rebuild the 4 homework notebooks."""
import json, os

BASE_DIR = "D:/RETO01INTEGRIDAD"

def make_md(text):
    lines = text.split(chr(10))
    src = []
    for i, line in enumerate(lines):
        src.append(line + chr(10) if i < len(lines) - 1 else line)
    return {"cell_type": "markdown", "metadata": {}, "source": src}

def make_code(text):
    lines = text.split(chr(10))
    src = []
    for i, line in enumerate(lines):
        src.append(line + chr(10) if i < len(lines) - 1 else line)
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}

def sep():
    return {"cell_type": "markdown", "metadata": {}, "source": ["---"]}

def load_nb(fn):
    with open(os.path.join(BASE_DIR, fn), "r", encoding="utf-8") as f:
        return json.load(f)

def save_nb(nb, fn):
    with open(os.path.join(BASE_DIR, fn), "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"  Saved: {fn}")

# Load cell data from JSON
with open(os.path.join(BASE_DIR, "cell_data.json"), "r", encoding="utf-8") as f:
    D = json.load(f)

# ===== NB01 =====
print("Rebuilding 01...")
nb = load_nb("01_Tarea_Calidad_IoT.ipynb")
c0, c1 = nb["cells"][0], nb["cells"][1]
ex1, ex2, ex3, res = nb["cells"][3], nb["cells"][8], nb["cells"][13], nb["cells"][18]
d = D["nb01"]
nb["cells"] = [c0, c1, sep(), ex1,
    make_code(d["code1a"]), make_md(d["just1"]), make_code(d["code1b"]),
    sep(), ex2,
    make_code(d["code2a"]), make_md(d["just2"]), make_code(d["code2b"]),
    sep(), ex3,
    make_code(d["code3a"]), make_md(d["just3"]), make_code(d["code3b"]),
    sep(), res, make_code(d["code_result"])]
save_nb(nb, "01_Tarea_Calidad_IoT.ipynb")

# ===== NB02 =====
print("Rebuilding 02...")
nb = load_nb("02_Tarea_Riesgos_Integridad.ipynb")
c0, c1 = nb["cells"][0], nb["cells"][1]
ex1, ex2, ex3, res = nb["cells"][2], nb["cells"][4], nb["cells"][6], nb["cells"][8]
d = D["nb02"]
nb["cells"] = [c0, c1,
    ex1, make_md(d["just1"]), make_code(d["code1"]),
    ex2, make_md(d["just2"]), make_code(d["code2"]),
    ex3, make_md(d["just3"]), make_code(d["code3"]),
    res, make_code(d["code_result"])]
save_nb(nb, "02_Tarea_Riesgos_Integridad.ipynb")

# ===== NB03 =====
print("Rebuilding 03...")
nb = load_nb("03_Tarea_Mecanismos_Verificacion.ipynb")
c0, c1 = nb["cells"][0], nb["cells"][1]
ex1, ex2, ex3 = nb["cells"][2], nb["cells"][4], nb["cells"][6]
d = D["nb03"]
nb["cells"] = [c0, c1,
    ex1, make_md(d["just1"]), make_code(d["code1"]),
    ex2, make_md(d["just2"]), make_code(d["code2"]),
    ex3, make_md(d["just3"]), make_code(d["code3"])]
save_nb(nb, "03_Tarea_Mecanismos_Verificacion.ipynb")

# ===== NB04 =====
print("Rebuilding 04...")
nb = load_nb("04_Tarea_Gestion_Integridad.ipynb")
c0, c1 = nb["cells"][0], nb["cells"][1]
ex1, ex2, ex3 = nb["cells"][2], nb["cells"][4], nb["cells"][6]
d = D["nb04"]
nb["cells"] = [c0, c1,
    ex1, make_md(d["just1"]), make_code(d["code1"]),
    ex2, make_md(d["just2"]), make_code(d["code2"]),
    ex3, make_md(d["just3"]), make_code(d["code3"])]
save_nb(nb, "04_Tarea_Gestion_Integridad.ipynb")

print("All 4 notebooks rebuilt!")
