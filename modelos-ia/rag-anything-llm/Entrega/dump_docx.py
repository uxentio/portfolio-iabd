import docx
doc = docx.Document("Informe_MauiRAG.docx")
with open("informe_text.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip():
            f.write(f"{i}: {p.text}\n")
