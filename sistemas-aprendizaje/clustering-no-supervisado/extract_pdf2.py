import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

directory = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(directory, "Presentación_clustering_afinidad.pdf")
print('File exists:', os.path.exists(path))
doc = fitz.open(path)
print(f'Total pages: {doc.page_count}')
for i in range(doc.page_count):
    page = doc[i]
    text = page.get_text()
    if text.strip():
        print(f'\n===== PAGE {i+1} =====')
        print(text)
doc.close()
