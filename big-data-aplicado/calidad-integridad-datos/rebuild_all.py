#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, os, copy

SRC_DIR = r"D:/RETO01INTEGRIDAD/hadoop-lab_v4 - copia/contenido_ut3"
DST_DIR = r"D:/RETO01INTEGRIDAD"

# Solutions are loaded from a JSON sidecar file
with open(r"D:/RETO01INTEGRIDAD/_solutions.json", "r", encoding="utf-8") as f:
    SOLUTIONS = json.load(f)


def code_to_source_lines(code_str):
    code_str = code_str.strip(chr(10))
    lines = code_str.split(chr(10))
    result = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result.append(line + chr(10))
        else:
            result.append(line)
    return result


def rebuild_notebook(filename, replacements):
    src_path = os.path.join(SRC_DIR, filename)
    dst_path = os.path.join(DST_DIR, filename)

    with open(src_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    nb = copy.deepcopy(nb)

    tu_codigo_indices = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            src_text = "".join(cell["source"])
            if "TU CÓDIGO AQUÍ" in src_text:
                tu_codigo_indices.append(i)

    if len(tu_codigo_indices) != len(replacements):
        print(f"  WARNING: Found {len(tu_codigo_indices)} TU CODIGO cells but have "
              f"{len(replacements)} replacements for {filename}")

    for idx, cell_index in enumerate(tu_codigo_indices):
        if idx < len(replacements):
            nb["cells"][cell_index]["source"] = code_to_source_lines(replacements[idx])
            nb["cells"][cell_index]["outputs"] = []
            nb["cells"][cell_index]["execution_count"] = None

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"  [OK] {filename}")
    print(f"       Source: {src_path}")
    print(f"       Output: {dst_path}")
    print(f"       Replaced {len(tu_codigo_indices)} code cells")


def main():
    print("=" * 60)
    print("REBUILD ALL NOTEBOOKS")
    print("=" * 60)
    print()

    for filename, replacements in SOLUTIONS.items():
        print(f"Processing: {filename}")
        rebuild_notebook(filename, replacements)
        print()

    print("=" * 60)
    print("ALL NOTEBOOKS REBUILT SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
